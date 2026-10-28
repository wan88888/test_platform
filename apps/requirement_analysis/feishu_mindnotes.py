"""Native Mindnote output, created as a child of a user-selected Wiki page.

API contracts: Feishu Wiki v2 create-node documentation and the official
larksuite/cli internal/registry/catalog/services/mindnotes.json catalog.
"""
import uuid
import time
from urllib.parse import quote, urlsplit

from .feishu_documents import FeishuDocumentError, safe_id


def rich_text(text):
    return [{'element_type': 'text', 'text': {'content': text}}]


def plain_text(elements):
    if not isinstance(elements, list):
        return None
    if any(e.get('element_type') != 'text' for e in elements):
        return None
    return ''.join(e.get('text', {}).get('content', '') for e in elements)


def read_nodes(client, path):
    nodes = client.call('GET', path).get('nodes')
    if not isinstance(nodes, list):
        raise FeishuDocumentError('飞书未返回完整的思维笔记节点，请稍后重试。', 502)
    return {safe_id(node.get('node_id')): node for node in nodes}


def matches(node, expected):
    return (plain_text(node.get('texts')) == plain_text(expected['texts'])
            and (not expected.get('parent_id') or node.get('parent_id') == expected['parent_id']))


def write_nodes(client, path, output, key, nodes):
    """Persist the exact request and idempotency key before every node mutation."""
    operation = output.node_operations.get(key)
    if operation is None:
        operation = {'client_token': str(uuid.uuid4()), 'nodes': nodes, 'ids': []}
        output.node_operations[key] = operation
        output.save(update_fields=['node_operations'])
    elif operation['nodes'] != nodes:
        raise FeishuDocumentError('思维笔记同步内容已变化，请联系管理员核对，避免重复写入。')
    if not operation['ids']:
        data = client.call('POST', path, json={
            'client_token': operation['client_token'], 'nodes': operation['nodes']})
        ids = data.get('ids')
        if not isinstance(ids, list) or len(ids) != len(nodes):
            raise FeishuDocumentError('思维笔记节点响应不完整，可重试同一次写入。', 502)
        ids = [safe_id(value) for value in ids]
        if len(set(ids)) != len(ids):
            raise FeishuDocumentError('思维笔记返回了重复节点标识，请重试写入。', 502)
        # Do not assume response IDs have request order. Match actual content and
        # parent before recording IDs or creating children under those nodes.
        actual = read_nodes(client, path)
        ordered = []
        for expected in nodes:
            found = [value for value in ids if value not in ordered and value in actual and matches(actual[value], expected)]
            if len(found) != 1:
                raise FeishuDocumentError('思维笔记节点写入校验不一致，用例仍保留在平台。', 502)
            ordered.append(found[0])
        operation['ids'] = ordered
        output.save(update_fields=['node_operations'])
    return operation['ids']


def export_mindnote(client, task, output):
    personal = output.destination.get('mode') == 'drive'
    if personal and not output.destination.get('space_id'):
        output.destination = client.personal_mindnote_destination()
        output.save(update_fields=['destination'])
    if personal and output.destination.get('move_task_id'):
        # A resumed export with an outstanding move only polls that same task.
        # It must not recreate the note or resubmit the move request.
        finish_move_to_drive(client, output)
        return
    if not output.mindnote_token:
        destination = output.destination
        space_id = safe_id(destination.get('space_id'))
        payload = {'obj_type': 'mindnote', 'node_type': 'origin', 'title': task.title + ' - 测试用例'}
        if not personal:
            payload['parent_node_token'] = safe_id(destination.get('parent_node_token'))
        # Wiki creation has no documented idempotency key. Any ambiguous result
        # must stop recreation, including a crash between the response and save.
        output.status = 'uncertain'
        output.save(update_fields=['status'])
        try:
            data = client.call('POST', f'/wiki/v2/spaces/{space_id}/nodes', json=payload)
        except FeishuDocumentError as exc:
            if not exc.uncertain:
                output.status = 'failed'
            raise
        node = data.get('node', {})
        if node.get('obj_type') != 'mindnote':
            raise FeishuDocumentError('飞书未返回原生思维笔记，请在目标知识库核对创建结果。', 502)
        output.mindnote_token = safe_id(node.get('obj_token'))
        output.destination['node_token'] = safe_id(node.get('node_token'))
        output.url = destination['origin'] + '/wiki/' + output.destination['node_token']
        output.status = 'running'
        output.save(update_fields=['mindnote_token', 'url', 'status', 'destination'])

    path = f'/mindnote/v1/mindnotes/{safe_id(output.mindnote_token)}/nodes'
    if 'root_id' not in output.node_operations:
        existing = read_nodes(client, path)
        roots = [key for key, node in existing.items() if not node.get('parent_id')]
        if len(roots) == 1:
            root = roots[0]
        elif not existing:
            root = write_nodes(client, path, output, 'root', [{'texts': rich_text(task.title + ' - 测试用例')}])[0]
        else:
            raise FeishuDocumentError('无法确认思维笔记根节点，请检查目标笔记后重试。')
        output.node_operations['root_id'] = root
        output.save(update_fields=['node_operations'])
    root = safe_id(output.node_operations['root_id'])
    headers, rows = output.rows[0], output.rows[1:]
    title_column = next((i for i, h in enumerate(headers) if h in ('用例标题', '测试用例名称', '用例名称', '测试目标', '标题')), min(1, len(headers) - 1))
    for start in range(0, len(rows), 20):
        chunk = rows[start:start + 20]
        cases = [{'parent_id': root, 'texts': rich_text(f'用例 {start + i + 1} · {row[title_column]}')}
                 for i, row in enumerate(chunk)]
        ids = write_nodes(client, path, output, f'cases-{start}', cases)
        fields = [{'parent_id': parent, 'texts': rich_text(f'{column + 1}. {header}：{value}')}
                  for parent, row in zip(ids, chunk) for column, (header, value) in enumerate(zip(headers, row))]
        for offset in range(0, len(fields), 50):
            write_nodes(client, path, output, f'fields-{start}-{offset}', fields[offset:offset + 50])
    # Recheck every stored node, including earlier completed batches on retry.
    actual = read_nodes(client, path)
    if root not in actual:
        raise FeishuDocumentError('思维笔记根节点已删除，请检查笔记。', 502)
    for key, operation in output.node_operations.items():
        if key == 'root_id':
            continue
        for node_id, expected in zip(operation['ids'], operation['nodes']):
            if node_id not in actual or not matches(actual[node_id], expected):
                raise FeishuDocumentError('思维笔记内容校验不一致，请检查是否有节点被修改或删除。', 502)
    if personal:
        finish_move_to_drive(client, output)


def finish_move_to_drive(client, output):
    """Move only this newly generated note to the current user's Drive root."""
    destination = output.destination
    task_id = destination.get('move_task_id')
    if not task_id:
        node = safe_id(destination.get('node_token'))
        if destination.get('move_unknown'):
            output.status = 'uncertain'
            raise FeishuDocumentError('移到我的空间的请求结果未知，请先在飞书核对，暂不重复移动。')
        destination['move_unknown'] = True
        output.status = 'uncertain'
        output.save(update_fields=['destination', 'status'])
        try:
            data = client.call('POST', f'/wiki/v2/nodes/{node}/move_wiki_to_docs', json={})
        except FeishuDocumentError as exc:
            if not exc.uncertain:
                destination['move_unknown'] = False
                output.status = 'running'
                output.save(update_fields=['destination', 'status'])
            raise
        task_id = data.get('task_id')
        if not isinstance(task_id, str) or not task_id or len(task_id) > 2048:
            raise FeishuDocumentError('飞书未返回有效的移动任务，请在我的空间核对笔记位置。', 502)
        destination.update(move_task_id=task_id, move_unknown=False)
        output.status = 'running'
        output.save(update_fields=['destination', 'status'])
    for attempt in range(15):
        if attempt:
            time.sleep(2)
        data = client.call('GET', '/wiki/v2/tasks/' + quote(task_id, safe=''),
                           params={'task_type': 'move_wiki_to_docs'})
        result = data.get('task', {}).get('move_wiki_to_docs_result', {})
        status = result.get('status')
        if type(status) is not int or status not in (-1, 0, 1):
            raise FeishuDocumentError('移动状态响应异常，请点击重试继续查询同一任务。', 502)
        if status == 1:
            continue
        if status == -1:
            raise FeishuDocumentError('飞书移动任务失败，笔记已保留在个人文档库，请联系管理员核对移动权限。')
        # Require the task to identify this exact native Mindnote and its final
        # navigation URL before reporting a successful delivery to Drive.
        if result.get('obj_token') != output.mindnote_token or result.get('obj_type') != 'mindnote':
            raise FeishuDocumentError('移动结果与本次思维笔记不一致，请联系管理员核对。', 502)
        url = result.get('url', '')
        try:
            parsed = urlsplit(url)
            valid = (parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password
                     and parsed.port in (None, 443) and any(parsed.hostname == host or parsed.hostname.endswith('.' + host)
                     for host in ('feishu.cn', 'larkoffice.com')))
        except ValueError:
            valid = False
        if not valid:
            raise FeishuDocumentError('笔记已移动，但飞书未返回有效的结果链接，请到我的空间查看。', 502)
        output.url = url
        destination['moved_to_drive'] = True
        output.save(update_fields=['url', 'destination'])
        return
    raise FeishuDocumentError('笔记已生成，飞书仍在移到我的空间；请点击重试继续查询，无需重新生成。')
