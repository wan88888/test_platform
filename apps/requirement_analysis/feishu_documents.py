"""User-scoped Feishu document input and resumable spreadsheet output.

Only documented OpenAPI endpoints are called; supplied URLs are parsed, never fetched.
"""
import base64
import hashlib
import html
import re
from datetime import timedelta
from urllib.parse import urlsplit, quote

import requests
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.utils import timezone
from django.views.decorators.debug import sensitive_variables

from apps.users.models import FeishuDocumentGrant, FeishuIdentity

DOCUMENT_SCOPES = ('docx:document:readonly', 'wiki:node:read', 'sheets:spreadsheet')
MINDNOTE_SCOPES = DOCUMENT_SCOPES + ('wiki:node:create', 'mindnote:node:read', 'mindnote:node:create',
                                    'wiki:space:read', 'space:document:move')
API_ROOT = 'https://open.feishu.cn/open-apis'
MAX_TEXT = 100000


class FeishuDocumentError(Exception):
    def __init__(self, message, status=400, uncertain=False):
        self.status = status
        self.uncertain = uncertain
        super().__init__(message)


def cipher():
    # Domain-separated key; deployment SECRET_KEY must be stable and private.
    key = hashlib.sha256(('testhub-feishu-documents-v1:' + settings.SECRET_KEY).encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


@sensitive_variables()
def save_grant(user, token, required_scopes=None):
    if not isinstance(token, dict) or not isinstance(token.get('expires_in'), int) or token['expires_in'] <= 60:
        raise FeishuDocumentError('飞书未返回有效的文档授权有效期，请重新授权。')
    scopes = set(str(token.get('scope', '')).split())
    if not set(required_scopes or DOCUMENT_SCOPES).issubset(scopes):
        raise FeishuDocumentError('文档权限未完整授权，请管理员开通并发布所选输出方式需要的用户身份权限后重试。', 403)
    FeishuDocumentGrant.objects.update_or_create(user=user, defaults={
        'app_id': settings.FEISHU_APP_ID,
        'encrypted_token': cipher().encrypt(token['access_token'].encode()).decode(),
        'scopes': sorted(scopes),
        'expires_at': timezone.now() + timedelta(seconds=min(token['expires_in'], 7200) - 60),
    })


@sensitive_variables()
def get_token(user, output_type='sheet'):
    grant = FeishuDocumentGrant.objects.filter(user=user, app_id=settings.FEISHU_APP_ID).first()
    identity = FeishuIdentity.objects.filter(user=user, app_id=settings.FEISHU_APP_ID,
        tenant_key__in=settings.FEISHU_ALLOWED_TENANT_KEYS).exists()
    if not user.is_active or not identity or not grant or grant.expires_at <= timezone.now():
        if grant and grant.expires_at <= timezone.now():
            grant.delete()
        raise FeishuDocumentError('请先授权飞书文档访问；授权过期后可重新授权，无需重新生成用例。', 403)
    if output_type == 'mindnote' and not set(MINDNOTE_SCOPES).issubset(grant.scopes):
        raise FeishuDocumentError('请先选择飞书思维笔记并重新授权，补齐文档库读取、思维笔记读写和移动文档权限。', 403)
    try:
        return cipher().decrypt(grant.encrypted_token.encode()).decode()
    except (InvalidToken, ValueError):
        grant.delete()
        raise FeishuDocumentError('飞书文档授权已失效，请重新授权。', 403) from None


def parse_document_url(value):
    try:
        uri = urlsplit(value.strip())
        host = uri.hostname or ''
        if (uri.scheme != 'https' or uri.username or uri.password or uri.port not in (None, 443)
                or not (host == 'feishu.cn' or host.endswith('.feishu.cn')
                        or host == 'larkoffice.com' or host.endswith('.larkoffice.com'))):
            raise ValueError
        match = re.fullmatch(r'/(docx|wiki)/([A-Za-z0-9]{10,128})/?', uri.path)
        if not match:
            raise ValueError
        return match.groups()
    except (ValueError, AttributeError):
        raise FeishuDocumentError('请粘贴有效的飞书新版文档（/docx/）或知识库文档（/wiki/）HTTPS 链接。') from None


def safe_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', value):
        raise FeishuDocumentError('飞书返回的资源标识无效，请稍后重试。', 502)
    return value


class FeishuClient:
    def __init__(self, user, output_type='sheet'):
        self.token = get_token(user, output_type)

    def personal_mindnote_destination(self):
        space = self.call('GET', '/wiki/v2/spaces/my_library').get('space', {})
        if space.get('space_type') != 'my_library':
            raise FeishuDocumentError('飞书未返回当前账号的个人文档库，已停止创建，请联系管理员。', 502)
        return {'mode': 'drive', 'space_id': safe_id(space.get('space_id')), 'origin': 'https://www.feishu.cn'}

    @sensitive_variables()
    def call(self, method, path, **kwargs):
        try:
            response = requests.request(method, API_ROOT + path,
                headers={'Authorization': 'Bearer ' + self.token},
                timeout=(5, 30), allow_redirects=False, **kwargs)
            if len(response.content) > 12 * 1024 * 1024:
                raise FeishuDocumentError('飞书文档内容过大，请拆分需求文档。')
            body = response.json()
        except (requests.RequestException, ValueError):
            raise FeishuDocumentError('飞书连接中断，请稍后重试。', 502, uncertain=True) from None
        code = body.get('code') if isinstance(body, dict) else None
        if response.status_code != 200 or type(code) is not int or code != 0:
            if code == 131006 and path.startswith('/wiki/'):
                if method == 'POST' and re.fullmatch(r'/wiki/v2/spaces/[^/]+/nodes', path):
                    message = ('无法在目标知识库页面下新建思维笔记：当前飞书账号的知识库或父页面权限不足。'
                               '请联系知识库管理员，为当前账号开通该页面的创建子页面（容器编辑）权限，'
                               '必要时加入知识库成员。权限调整后点击“重试写入已有结果”，无需重新生成用例。')
                else:
                    message = '当前飞书账号无权访问该知识库页面，请联系页面所有者或知识库管理员授予访问权限。'
                raise FeishuDocumentError(message + '（飞书错误码：131006）', 403)
            suffix = f'（飞书错误码：{code}）' if type(code) is int else ''
            raise FeishuDocumentError('飞书请求失败，请检查应用权限已发布、本人有文档访问权限且授权未过期。' + suffix,
                                      400, uncertain=response.status_code >= 500)
        data = body.get('data')
        if not isinstance(data, dict):
            raise FeishuDocumentError('飞书响应格式异常，请稍后重试。', 502, uncertain=True)
        return data

    def read_document(self, url):
        kind, token = parse_document_url(url)
        if kind == 'wiki':
            node = self.call('GET', '/wiki/v2/spaces/get_node', params={'token': token})['node']
            if node.get('obj_type') != 'docx':
                raise FeishuDocumentError('该知识库链接不是新版需求文档，请选择文档类型页面。')
            token = safe_id(node.get('obj_token'))
        info = self.call('GET', f'/docx/v1/documents/{token}')
        content = self.call('GET', f'/docx/v1/documents/{token}/raw_content').get('content')
        if not isinstance(content, str) or not content.strip():
            raise FeishuDocumentError('文档没有可读取的正文，请使用包含文字需求的文档。')
        if len(content) > MAX_TEXT:
            raise FeishuDocumentError('需求正文超过 10 万字符，请拆分文档后生成，避免遗漏需求。')
        return {'title': info.get('document', {}).get('title', '飞书需求文档')[:200],
                'text': content, 'characters': len(content)}


def table_rows(content):
    """Preserve every column, escaped pipe and multiline cell from the model table."""
    rows, headers = [], None
    for line in content.splitlines():
        if not line.strip().startswith('|'):
            continue
        line = line.strip()[1:]
        if line.endswith('|'):
            line = line[:-1]
        cells = [html.unescape(re.sub(r'<br\s*/?>', '\n', s, flags=re.I)).strip()
                 for s in re.split(r'(?<!\\)\|', line)]
        cells = [re.sub(r'\*\*(.*?)\*\*', r'\1', s.replace(r'\|', '|'), flags=re.S) for s in cells]
        if all(re.fullmatch(r':?-{3,}:?', c) for c in cells):
            if rows:
                header = rows.pop()
                # Some model revisions concatenate a dangling case ID before the
                # header. Recover only a recognizable header of separator width;
                # data rows remain strictly checked, never truncated or discarded.
                if len(header) > len(cells):
                    candidate = header[-len(cells):]
                    id_label = re.sub(r'\s+', '', candidate[0]).lower()
                    if id_label in ('用例id', '用例编号', '测试用例id', '测试用例编号', 'id', 'caseid'):
                        header = candidate
                if len(header) != len(cells):
                    raise FeishuDocumentError('用例表头与分隔行列数不一致，请检查生成结果后重试。')
                if headers is not None and header != headers:
                    raise FeishuDocumentError('生成结果包含不同格式的表格，请统一用例列后重试。')
                headers = header
            continue
        rows.append(cells)
    if not headers or not rows or len(headers) > 26 or len(rows) > 4999:
        raise FeishuDocumentError('请让编写和评审提示词输出 Markdown 用例表格（最多 4999 条、26 列），然后重新生成。')
    tables = [headers] + [row for row in rows if row != headers]
    if any(len(row) != len(headers) for row in tables):
        raise FeishuDocumentError('用例表格列数不一致，请检查提示词及生成结果后重试。')
    if any(len(cell) > 40000 for row in tables for cell in row):
        raise FeishuDocumentError('单个用例单元格超过 4 万字符，请拆分后重试。')
    return tables


def export_task(task):
    """Claim one writer atomically; failure never changes completed generation status."""
    from .models import FeishuCaseExport
    if task.status != 'completed':
        return
    claimed = FeishuCaseExport.objects.filter(task=task, status__in=['pending', 'failed']).update(
        status='running', error='', updated_at=timezone.now())
    if not claimed:
        return
    output = FeishuCaseExport.objects.get(task=task)
    creating = False
    creation_acknowledged = False
    try:
        client = FeishuClient(task.created_by, output.output_type)
        if not output.rows:
            output.rows = table_rows(task.final_test_cases)
            output.save(update_fields=['rows'])
        if output.output_type == 'mindnote':
            from .feishu_mindnotes import export_mindnote
            export_mindnote(client, task, output)
            output.status, output.error = 'succeeded', ''
            output.save(update_fields=['status', 'error', 'updated_at'])
            return
        if not output.spreadsheet_token:
            creating = True
            data = client.call('POST', '/sheets/v3/spreadsheets', json={'title': task.title + ' - 测试用例'})
            creation_acknowledged = True
            sheet = data.get('spreadsheet', {})
            output.spreadsheet_token = safe_id(sheet.get('spreadsheet_token'))
            # Only allow a trusted Feishu navigation URL, never arbitrary provider HTML.
            url = sheet.get('url', '')
            parsed = urlsplit(url)
            if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
                    or not any(parsed.hostname == host or parsed.hostname.endswith('.' + host)
                               for host in ('feishu.cn', 'larkoffice.com'))):
                raise FeishuDocumentError('飞书返回的表格链接异常，请在飞书云空间核对新建结果。', 502, uncertain=True)
            output.url = url
            output.save(update_fields=['spreadsheet_token', 'url'])
            creating = False
        token = safe_id(output.spreadsheet_token)
        sheets = client.call('GET', f'/sheets/v3/spreadsheets/{token}/sheets/query')['sheets']
        sheet = next((s for s in sheets if s.get('sheet_id') == output.sheet_id), None) if output.sheet_id else next(iter(sheets), None)
        if not sheet:
            raise FeishuDocumentError('目标工作表已删除或不存在，请在飞书中检查表格。')
        output.sheet_id = safe_id(sheet['sheet_id'])
        output.save(update_fields=['sheet_id'])
        grid = sheet.get('grid_properties', {})
        for dimension, size, current in [('ROWS', len(output.rows), grid.get('row_count', 0)),
                                         ('COLUMNS', len(output.rows[0]), grid.get('column_count', 0))]:
            if size > current:
                client.call('POST', f'/sheets/v2/spreadsheets/{token}/dimension_range', json={
                    'dimension': {'sheetId': output.sheet_id, 'majorDimension': dimension, 'length': size - current}})
        # Plain strings, not formula objects: model-generated formulas are literal text.
        end_column = chr(64 + len(output.rows[0]))
        for start in range(0, len(output.rows), 500):
            chunk = output.rows[start:start + 500]
            cell_range = f'{output.sheet_id}!A{start + 1}:{end_column}{start + len(chunk)}'
            client.call('PUT', f'/sheets/v2/spreadsheets/{token}/values',
                        json={'valueRange': {'range': cell_range, 'values': chunk}})
            actual = client.call('GET', f'/sheets/v2/spreadsheets/{token}/values/{quote(cell_range, safe="!:")}',
                                 params={'valueRenderOption': 'ToString'})
            values = actual.get('valueRange', {}).get('values', [])
            # Sheets can return null/trailing empty cells instead of empty strings.
            normalized = [[str(c) if c is not None else '' for c in row] + [''] * (len(chunk[0]) - len(row)) for row in values]
            while len(normalized) < len(chunk) and not any(chunk[len(normalized)]):
                normalized.append([''] * len(chunk[0]))
            if normalized != chunk:
                raise FeishuDocumentError('飞书表格写入后的校验不一致，用例仍保存在平台，可重试写入。', 502)
        output.status, output.error = 'succeeded', ''
    except FeishuDocumentError as exc:
        output.status = 'uncertain' if output.status == 'uncertain' or creating and (exc.uncertain or creation_acknowledged) else 'failed'
        output.error = str(exc)
        if output.status == 'uncertain':
            output.error += ' 操作结果未知，为避免重复操作，请先到飞书云空间核对，暂不自动重试。'
    except Exception:
        # No raw provider errors, token values or requirement content in logs/responses.
        output.status = 'uncertain' if creating or output.status == 'uncertain' else 'failed'
        output.error = '飞书同步未完成，用例已保留；请稍后重试或联系管理员。'
    output.save(update_fields=['status', 'error', 'updated_at'])
