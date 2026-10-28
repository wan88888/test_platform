from datetime import timedelta
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

from django.test import TestCase, SimpleTestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.users.models import User, FeishuIdentity, FeishuDocumentGrant
from .models import TestCaseGenerationTask, FeishuCaseExport
from .feishu_documents import (FeishuClient, FeishuDocumentError, DOCUMENT_SCOPES, MINDNOTE_SCOPES,
                               parse_document_url, table_rows, save_grant, get_token, export_task)

TABLE = '| 用例ID | 测试目标 | 操作步骤 | 预期结果 |\n| --- | --- | --- | --- |\n| 001 | 登录 | 输入 a\\|b<br>点击登录 | 成功 |'


class LinkAndTableTests(SimpleTestCase):
    def test_strict_links_and_no_url_fetch(self):
        for url in ['http://team.feishu.cn/docx/abcdefghijk', 'https://127.0.0.1/docx/abcdefghijk',
                    'https://feishu.cn.evil.com/docx/abcdefghijk', 'https://user@feishu.cn/docx/abcdefghijk',
                    'https://feishu.cn:8000/docx/abcdefghijk', 'https://feishu.cn/docx/../abcdefghijk',
                    'https://team.feishu.cn/sheets/abcdefghijk', 'https://evil.com/?url=https://feishu.cn']:
            with self.subTest(url=url), self.assertRaises(FeishuDocumentError):
                parse_document_url(url)
        self.assertEqual(parse_document_url('https://team.feishu.cn/wiki/abcdefghijk?from=copy#section'), ('wiki', 'abcdefghijk'))

    def test_table_preserves_columns_multiline_and_escaped_pipes(self):
        rows = table_rows(TABLE)
        self.assertEqual(rows[1], ['001', '登录', '输入 a|b\n点击登录', '成功'])
        self.assertEqual(len(rows[0]), 4)

    def test_bad_tables_are_not_silently_dropped(self):
        for content in ['非表格用例', TABLE + '\n| 002 | 缺列 |', TABLE + '\n| extra | title |\n| --- | --- |\n| x | y |']:
            with self.subTest(content=content), self.assertRaises(FeishuDocumentError):
                table_rows(content)

    def test_revision_header_prefix_is_recovered_without_truncating_case_rows(self):
        content = '| **CASE_99** |' + TABLE
        self.assertEqual(table_rows(content), table_rows(TABLE))
        with self.assertRaises(FeishuDocumentError):
            table_rows(TABLE + '\n| 002 | extra | unexpected | a | b |')

    def test_emphasis_is_plain_text_and_empty_final_cells_are_preserved(self):
        self.assertEqual(table_rows('|ID|标题|\n|---|---|\n|**01**||'), [['ID', '标题'], ['01', '']])


@override_settings(FEISHU_LOGIN_ENABLED=True, FEISHU_APP_ID='cli_test', FEISHU_APP_SECRET='secret',
                   FEISHU_REDIRECT_URI='https://testhub.example/auth/feishu/callback',
                   FEISHU_ALLOWED_TENANT_KEYS=['tenant'], FEISHU_AUTO_CREATE_USER=True)
class DocumentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='feishu_user')
        self.other = User.objects.create_user(username='another_user')
        FeishuIdentity.objects.create(user=self.user, app_id='cli_test', open_id='ou_test', tenant_key='tenant')
        self.grant()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.task = TestCaseGenerationTask.objects.create(task_id='TASK_DOCS', title='登录需求',
            requirement_text='private requirement', created_by=self.user, status='completed', final_test_cases=TABLE)
        self.output = FeishuCaseExport.objects.create(task=self.task)

    def grant(self):
        save_grant(self.user, {'access_token': 'private-provider-token', 'expires_in': 7200,
                              'scope': ' '.join(DOCUMENT_SCOPES)})

    def test_grants_are_encrypted_expire_and_remain_user_scoped(self):
        grant = FeishuDocumentGrant.objects.get(user=self.user)
        self.assertNotIn('private-provider-token', grant.encrypted_token)
        self.assertEqual(get_token(self.user), 'private-provider-token')
        with self.assertRaises(FeishuDocumentError): get_token(self.other)
        grant.expires_at = timezone.now() - timedelta(seconds=1)
        grant.save()
        with self.assertRaises(FeishuDocumentError): get_token(self.user)
        self.assertFalse(FeishuDocumentGrant.objects.exists())

    def test_missing_scopes_cannot_be_saved(self):
        with self.assertRaises(FeishuDocumentError):
            save_grant(self.user, {'access_token': 'token', 'expires_in': 7200, 'scope': 'docx:document:readonly'})

    def test_access_api_and_disconnect_never_return_tokens(self):
        response = self.client.get('/api/requirement-analysis/feishu/access/')
        self.assertTrue(response.data['authorized'])
        self.assertNotIn('private-provider-token', str(response.data))
        self.client.delete('/api/requirement-analysis/feishu/access/')
        self.assertFalse(FeishuDocumentGrant.objects.exists())

    def test_authorization_requests_scopes_and_binds_current_user(self):
        response = self.client.post('/api/requirement-analysis/feishu/authorize/', HTTP_ORIGIN='https://testhub.example')
        self.assertEqual(response.status_code, 200)
        query = parse_qs(urlsplit(response.data['authorize_url']).query)
        self.assertEqual(query['scope'], [' '.join(DOCUMENT_SCOPES)])
        from apps.users.models import FeishuLoginAttempt
        self.assertEqual(FeishuLoginAttempt.objects.get().document_user_id, self.user.id)

    @patch('apps.users.feishu.fetch_user_info')
    def test_callback_rejects_account_switch_and_accepts_matching_grant(self, profile):
        response = self.client.post('/api/requirement-analysis/feishu/authorize/', HTTP_ORIGIN='https://testhub.example')
        state = parse_qs(urlsplit(response.data['authorize_url']).query)['state'][0]
        profile.return_value = {'open_id': 'ou_wrong', 'tenant_key': 'tenant'}
        response = self.client.post('/api/auth/feishu/callback/', {'state': state, 'code': 'code'}, format='json')
        self.assertEqual(response.status_code, 403)
        response = self.client.post('/api/requirement-analysis/feishu/authorize/', HTTP_ORIGIN='https://testhub.example')
        state = parse_qs(urlsplit(response.data['authorize_url']).query)['state'][0]
        profile.return_value = {'open_id': 'ou_test', 'tenant_key': 'tenant', 'name': '成员', '_document_grant': {
            'access_token': 'new-private-token', 'expires_in': 7200, 'scope': ' '.join(DOCUMENT_SCOPES)}}
        response = self.client.post('/api/auth/feishu/callback/', {'state': state, 'code': 'code'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertTrue(response.data['documents_authorized'])
        self.assertNotIn('new-private-token', str(response.data))
        self.assertEqual(get_token(self.user), 'new-private-token')

    def test_export_and_private_task_access_denied_to_other_users(self):
        self.client.force_authenticate(self.other)
        for method in ('get', 'post'):
            response = getattr(self.client, method)('/api/requirement-analysis/feishu/tasks/TASK_DOCS/')
            self.assertEqual(response.status_code, 404)
        response = self.client.get('/api/requirement-analysis/testcase-generation/')
        self.assertNotIn('private requirement', str(response.data))
        self.assertEqual(self.client.get('/api/requirement-analysis/testcase-generation/TASK_DOCS/').status_code, 404)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/requirement-analysis/testcase-generation/TASK_DOCS/stream_progress/').status_code, 404)
        self.assertEqual(self.client.get('/api/requirement-analysis/feishu/access/').status_code, 401)

    @patch.object(FeishuClient, 'call')
    def test_wiki_is_resolved_before_document_read_and_empty_or_large_rejected(self, call):
        call.side_effect = [{'node': {'obj_type': 'docx', 'obj_token': 'realDocToken'}},
                            {'document': {'title': '需求标题'}}, {'content': '需求正文'}]
        data = FeishuClient(self.user).read_document('https://team.feishu.cn/wiki/abcdefghijk')
        self.assertEqual(data['text'], '需求正文')
        self.assertIn('realDocToken', call.call_args_list[1].args[1])
        for content in ['', 'a' * 100001]:
            call.side_effect = [{'document': {'title': '需求'}}, {'content': content}]
            with self.assertRaises(FeishuDocumentError):
                FeishuClient(self.user).read_document('https://team.feishu.cn/docx/abcdefghijk')

    @patch('apps.requirement_analysis.feishu_documents.requests.request')
    def test_provider_errors_are_sanitized_and_redirects_disabled(self, request):
        request.return_value = Mock(status_code=403, content=b'error', json=lambda: {'code': 99991672, 'msg': 'private-provider-token'})
        with self.assertRaises(FeishuDocumentError) as exc:
            FeishuClient(self.user).call('GET', '/docx/v1/documents/doc')
        self.assertNotIn('private-provider-token', str(exc.exception))
        self.assertIn('99991672', str(exc.exception))
        self.assertFalse(request.call_args.kwargs['allow_redirects'])
        self.assertTrue(request.call_args.args[1].startswith('https://open.feishu.cn/open-apis/'))

    @patch('apps.requirement_analysis.feishu_documents.requests.request')
    def test_wiki_resource_permission_error_explains_creation_access_without_reauthorization(self, request):
        request.return_value = Mock(status_code=400, content=b'error',
            json=lambda: {'code': 131006, 'msg': 'private-provider-token'})
        for method, path, expected in [
            ('POST', '/wiki/v2/spaces/123456/nodes', '创建子页面（容器编辑）权限'),
            ('GET', '/wiki/v2/spaces/get_node', '授予访问权限')]:
            with self.subTest(method=method), self.assertRaises(FeishuDocumentError) as exc:
                FeishuClient(self.user).call(method, path)
            self.assertEqual(exc.exception.status, 403)
            self.assertIn(expected, str(exc.exception))
            self.assertNotIn('重新授权', str(exc.exception))
            self.assertNotIn('private-provider-token', str(exc.exception))
            self.assertFalse(exc.exception.uncertain)

    def sheet_api(self, method, path, **kwargs):
        if path == '/sheets/v3/spreadsheets':
            return {'spreadsheet': {'spreadsheet_token': 'newSheet', 'url': 'https://team.feishu.cn/sheets/newSheet'}}
        if path.endswith('/sheets/query'):
            return {'sheets': [{'sheet_id': 'sheet1', 'grid_properties': {'row_count': 200, 'column_count': 20}}]}
        if method == 'PUT':
            self.written = kwargs['json']['valueRange']['values']
            return {}
        if '/values/' in path:
            return {'valueRange': {'values': self.written}}
        return {}

    @patch.object(FeishuClient, 'call')
    def test_export_writes_and_reads_back_once_and_is_idempotent(self, call):
        call.side_effect = self.sheet_api
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'succeeded', self.output.error)
        self.assertEqual(self.written[1][2], '输入 a|b\n点击登录')
        before = call.call_count
        export_task(self.task)
        self.assertEqual(call.call_count, before)

    @patch.object(FeishuClient, 'call')
    def test_failed_write_resumes_same_spreadsheet(self, call):
        def fail_once(method, path, **kwargs):
            if method == 'PUT': raise FeishuDocumentError('暂时不可用')
            return self.sheet_api(method, path, **kwargs)
        call.side_effect = fail_once
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'failed')
        self.assertEqual(self.output.spreadsheet_token, 'newSheet')
        call.reset_mock()
        call.side_effect = self.sheet_api
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'succeeded')
        self.assertFalse(any(c.args[1] == '/sheets/v3/spreadsheets' for c in call.call_args_list))
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')

    @patch.object(FeishuClient, 'call')
    def test_unknown_creation_outcome_is_never_blindly_retried(self, call):
        call.side_effect = FeishuDocumentError('网络中断', 502, uncertain=True)
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'uncertain')
        export_task(self.task)
        call.assert_called_once()
        self.assertEqual(self.client.post('/api/requirement-analysis/feishu/tasks/TASK_DOCS/').status_code, 409)

    @patch.object(FeishuClient, 'call')
    def test_readback_mismatch_does_not_report_success(self, call):
        def changed(method, path, **kwargs):
            if '/values/' in path: return {'valueRange': {'values': [['wrong']]}}
            return self.sheet_api(method, path, **kwargs)
        call.side_effect = changed
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'failed')

    @patch.object(FeishuClient, 'call')
    def test_missing_create_result_does_not_create_duplicates(self, call):
        call.return_value = {'spreadsheet': {}}
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'uncertain')
        export_task(self.task)
        call.assert_called_once()

    @patch('threading.Thread.start')
    @patch.object(FeishuClient, 'read_document')
    def test_generation_reads_source_creates_export_and_uses_document_title(self, read, start):
        from .models import AIModelConfig, PromptConfig
        for role in ('writer', 'reviewer'):
            AIModelConfig.objects.create(name=role, model_type='other', role=role,
                base_url='https://model.example/v1', model_name='model', created_by=self.user)
            PromptConfig.objects.create(name=role, prompt_type=role, content='输出 Markdown 表格', created_by=self.user)
        read.return_value = {'title': '文档标题', 'text': '来源正文'}
        response = self.client.post('/api/requirement-analysis/testcase-generation/generate/', {
            'feishu_source_url': 'https://team.feishu.cn/wiki/abcdefghijk',
            'requirement_text': '不应使用客户端伪造的正文', 'feishu_output': False,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        task = TestCaseGenerationTask.objects.get(task_id=response.data['task_id'])
        self.assertEqual(task.title, '文档标题')
        self.assertEqual(task.requirement_text, '来源正文')
        self.assertEqual(task.created_by, self.user)
        self.assertEqual(task.feishu_export.status, 'pending')
        start.assert_called_once()

    @patch.object(FeishuClient, 'read_document')
    def test_expired_grant_blocks_generation_before_read(self, read):
        FeishuDocumentGrant.objects.all().delete()
        response = self.client.post('/api/requirement-analysis/testcase-generation/generate/', {
            'feishu_source_url': 'https://team.feishu.cn/wiki/abcdefghijk'}, format='json')
        self.assertEqual(response.status_code, 403)
        read.assert_not_called()

    @patch.object(FeishuClient, 'call')
    def test_large_output_expands_sheet_and_preserves_all_rows_in_batches(self, call):
        self.task.final_test_cases = '| ID | 标题 |\n| --- | --- |\n' + '\n'.join(
            f'| {number:03d} | 用例{number} |' for number in range(750))
        self.task.save()
        call.side_effect = self.sheet_api
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'succeeded')
        writes = [c.kwargs['json']['valueRange'] for c in call.call_args_list if c.args[0] == 'PUT']
        self.assertEqual([w['range'] for w in writes], ['sheet1!A1:B500', 'sheet1!A501:B751'])
        self.assertEqual(sum(len(w['values']) for w in writes), 751)
        self.assertEqual(writes[-1]['values'][-1], ['749', '用例749'])
        dimensions = [c for c in call.call_args_list if c.args[1].endswith('/dimension_range')]
        self.assertEqual(dimensions[0].kwargs['json']['dimension']['length'], 551)

    def prepare_mindnote(self):
        save_grant(self.user, {'access_token': 'private-provider-token', 'expires_in': 7200,
                              'scope': ' '.join(MINDNOTE_SCOPES)}, required_scopes=MINDNOTE_SCOPES)
        self.output.output_type = 'mindnote'
        self.output.destination = {'space_id': '123456', 'parent_node_token': 'parentWiki', 'origin': 'https://team.feishu.cn'}
        self.output.save()
        self.nodes = {'root': {'node_id': 'root', 'parent_id': '', 'texts': [{'element_type': 'text', 'text': {'content': '需求'}}]}}
        self.node_requests = {}
        self.note_creations = 0

    def mindnote_api(self, method, path, **kwargs):
        if path == '/wiki/v2/spaces/123456/nodes':
            self.note_creations += 1
            self.assertEqual(kwargs['json']['obj_type'], 'mindnote')
            self.assertEqual(kwargs['json']['parent_node_token'], 'parentWiki')
            return {'node': {'obj_type': 'mindnote', 'obj_token': 'newMindnote', 'node_token': 'newWikiNode'}}
        self.assertEqual(path, '/mindnote/v1/mindnotes/newMindnote/nodes')
        if method == 'GET':
            return {'nodes': list(self.nodes.values())}
        payload = kwargs['json']
        key = payload['client_token']
        if key in self.node_requests:
            self.assertEqual(payload, self.node_requests[key][0])
            return {'ids': self.node_requests[key][1]}
        ids = []
        for node in payload['nodes']:
            node_id = 'node_' + str(len(self.nodes))
            self.nodes[node_id] = dict(node, node_id=node_id)
            ids.append(node_id)
        # Response order is deliberately different from input order.
        self.node_requests[key] = (payload, ids[::-1])
        return {'ids': ids[::-1]}

    @patch.object(FeishuClient, 'call')
    def test_native_mindnote_hierarchy_preserves_fields_and_readback(self, call):
        self.prepare_mindnote()
        call.side_effect = self.mindnote_api
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'succeeded', self.output.error)
        self.assertEqual(self.output.url, 'https://team.feishu.cn/wiki/newWikiNode')
        self.assertEqual(len(self.nodes), 6)
        case = self.nodes['node_1']
        self.assertEqual(case['parent_id'], 'root')
        self.assertEqual(case['texts'][0]['text']['content'], '用例 1 · 登录')
        fields = [n for n in self.nodes.values() if n.get('parent_id') == 'node_1']
        self.assertIn('3. 操作步骤：输入 a|b\n点击登录', [n['texts'][0]['text']['content'] for n in fields])
        before = call.call_count
        export_task(self.task)
        self.assertEqual(before, call.call_count)
        self.assertEqual(self.note_creations, 1)

    @patch.object(FeishuClient, 'call')
    def test_mindnote_retry_reuses_destination_and_idempotency_request_after_timeout(self, call):
        self.prepare_mindnote()
        def timeout_after_write(method, path, **kwargs):
            result = self.mindnote_api(method, path, **kwargs)
            if path.startswith('/mindnote/') and method == 'POST':
                raise FeishuDocumentError('连接中断', 502, uncertain=True)
            return result
        call.side_effect = timeout_after_write
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'failed')
        self.assertEqual(self.output.mindnote_token, 'newMindnote')
        call.side_effect = self.mindnote_api
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'succeeded', self.output.error)
        self.assertEqual(len(self.nodes), 6)
        self.assertEqual(self.note_creations, 1)

    @patch.object(FeishuClient, 'call')
    def test_ambiguous_native_creation_never_recreates(self, call):
        self.prepare_mindnote()
        call.side_effect = FeishuDocumentError('连接中断', 502, uncertain=True)
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'uncertain')
        export_task(self.task)
        call.assert_called_once()

    @patch.object(FeishuClient, 'call')
    def test_malformed_native_creation_never_recreates(self, call):
        self.prepare_mindnote()
        call.return_value = {'node': {'obj_type': 'docx'}}
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'uncertain')
        export_task(self.task)
        call.assert_called_once()

    @patch.object(FeishuClient, 'call')
    def test_native_creation_permission_failure_can_retry(self, call):
        self.prepare_mindnote()
        call.side_effect = FeishuDocumentError('没有父页面编辑权限', 403)
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'failed')
        self.assertFalse(self.output.mindnote_token)

    @patch.object(FeishuClient, 'call')
    def test_mindnote_readback_mismatch_does_not_report_success(self, call):
        self.prepare_mindnote()
        def changed(method, path, **kwargs):
            result = self.mindnote_api(method, path, **kwargs)
            if method == 'GET' and len(self.nodes) > 2:
                self.nodes['node_1']['texts'] = []
            return result
        call.side_effect = changed
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'failed')
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')

    @patch.object(FeishuClient, 'call')
    def test_mindnote_without_root_creates_root_then_children(self, call):
        self.prepare_mindnote()
        self.nodes = {}
        call.side_effect = self.mindnote_api
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'succeeded', self.output.error)
        self.assertEqual(len(self.nodes), 6)

    def test_sheet_grant_is_unchanged_and_cannot_create_mindnotes(self):
        response = self.client.get('/api/requirement-analysis/feishu/access/')
        self.assertTrue(response.data['authorized'])
        self.assertFalse(response.data['mindnote_authorized'])
        with self.assertRaises(FeishuDocumentError): get_token(self.user, 'mindnote')
        self.assertEqual(get_token(self.user), 'private-provider-token')

    def test_mindnote_authorization_binds_requested_scopes(self):
        from apps.users.models import FeishuLoginAttempt
        response = self.client.post('/api/requirement-analysis/feishu/authorize/',
            {'output_type': 'mindnote'}, HTTP_ORIGIN='https://testhub.example')
        self.assertEqual(response.status_code, 200)
        query = parse_qs(urlsplit(response.data['authorize_url']).query)
        self.assertEqual(set(query['scope'][0].split()), set(MINDNOTE_SCOPES))
        self.assertEqual(FeishuLoginAttempt.objects.get().document_scopes, list(MINDNOTE_SCOPES))
        with self.assertRaises(FeishuDocumentError):
            save_grant(self.user, {'access_token': 'token', 'expires_in': 7200, 'scope': ' '.join(DOCUMENT_SCOPES)}, MINDNOTE_SCOPES)

    def test_mindnote_source_accepts_docx_and_wiki_without_destination(self):
        from .serializers import TestCaseGenerationRequestSerializer
        source = 'https://team.feishu.cn/docx/abcdefghijk'
        serializer = TestCaseGenerationRequestSerializer(data={'feishu_source_url': source, 'feishu_output_type': 'mindnote'})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer = TestCaseGenerationRequestSerializer(data={'feishu_source_url': source.replace('/docx/', '/wiki/'),
            'feishu_output_type': 'mindnote'})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('feishu_destination_url', serializer.validated_data)

    @patch.object(FeishuClient, 'read_document')
    def test_mindnote_missing_scope_stops_before_ai_or_reading_document(self, read):
        response = self.client.post('/api/requirement-analysis/testcase-generation/generate/', {
            'feishu_source_url': 'https://team.feishu.cn/wiki/abcdefghijk', 'feishu_output_type': 'mindnote'}, format='json')
        self.assertEqual(response.status_code, 403)
        read.assert_not_called()

    def personal_mindnote_api(self, method, path, **kwargs):
        if path == '/wiki/v2/spaces/my_library':
            return {'space': {'space_id': 'personalSpace', 'space_type': 'my_library'}}
        if path == '/wiki/v2/spaces/personalSpace/nodes':
            self.assertNotIn('parent_node_token', kwargs['json'])
            self.note_creations += 1
            return {'node': {'obj_type': 'mindnote', 'obj_token': 'newMindnote', 'node_token': 'newWikiNode'}}
        if path.endswith('/move_wiki_to_docs'):
            self.assertEqual(kwargs['json'], {})
            self.assertEqual(path, '/wiki/v2/nodes/newWikiNode/move_wiki_to_docs')
            return {'task_id': 'full-opaque-task-id-with-hyphens'}
        if path.startswith('/wiki/v2/tasks/'):
            self.assertEqual(path, '/wiki/v2/tasks/full-opaque-task-id-with-hyphens')
            self.assertEqual(kwargs['params']['task_type'], 'move_wiki_to_docs')
            return {'task': {'move_wiki_to_docs_result': {'status': 0, 'obj_token': 'newMindnote',
                'obj_type': 'mindnote', 'url': 'https://team.feishu.cn/mindnotes/newMindnote'}}}
        return self.mindnote_api(method, path, **kwargs)

    @patch.object(FeishuClient, 'call')
    def test_personal_mindnote_moves_only_new_note_to_current_user_drive_root(self, call):
        self.prepare_mindnote()
        self.output.destination = {'mode': 'drive'}
        self.output.save()
        call.side_effect = self.personal_mindnote_api
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'succeeded', self.output.error)
        self.assertTrue(self.output.destination['moved_to_drive'])
        self.assertEqual(self.output.url, 'https://team.feishu.cn/mindnotes/newMindnote')
        self.assertEqual(self.note_creations, 1)

    @patch.object(FeishuClient, 'call')
    def test_personal_library_rejects_team_space(self, call):
        call.return_value = {'space': {'space_id': 'teamSpace', 'space_type': 'team'}}
        with self.assertRaises(FeishuDocumentError): FeishuClient(self.user).personal_mindnote_destination()
        call.assert_called_once_with('GET', '/wiki/v2/spaces/my_library')

    @patch('apps.requirement_analysis.feishu_mindnotes.time.sleep')
    @patch.object(FeishuClient, 'call')
    def test_move_timeout_resumes_same_opaque_task_without_rewriting_or_moving_again(self, call, sleep):
        self.prepare_mindnote()
        self.output.destination = {'mode': 'drive'}
        self.output.save()
        def processing(method, path, **kwargs):
            if path.startswith('/wiki/v2/tasks/'):
                return {'task': {'move_wiki_to_docs_result': {'status': 1}}}
            return self.personal_mindnote_api(method, path, **kwargs)
        call.side_effect = processing
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'failed')
        self.assertEqual(self.output.destination['move_task_id'], 'full-opaque-task-id-with-hyphens')
        call.reset_mock()
        call.side_effect = self.personal_mindnote_api
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'succeeded', self.output.error)
        call.assert_called_once_with('GET', '/wiki/v2/tasks/full-opaque-task-id-with-hyphens', params={'task_type': 'move_wiki_to_docs'})

    @patch.object(FeishuClient, 'call')
    def test_unknown_move_outcome_stops_automatic_retry(self, call):
        self.prepare_mindnote()
        self.output.destination = {'mode': 'drive'}
        self.output.save()
        def timeout(method, path, **kwargs):
            if path.endswith('/move_wiki_to_docs'):
                raise FeishuDocumentError('连接中断', 502, uncertain=True)
            return self.personal_mindnote_api(method, path, **kwargs)
        call.side_effect = timeout
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'uncertain')
        self.assertTrue(self.output.destination['move_unknown'])
        before = call.call_count
        export_task(self.task)
        self.assertEqual(before, call.call_count)

    @patch.object(FeishuClient, 'call')
    def test_invalid_move_result_does_not_report_success_or_change_destination(self, call):
        self.prepare_mindnote()
        self.output.destination = {'mode': 'drive'}
        self.output.save()
        def untrusted_url(method, path, **kwargs):
            data = self.personal_mindnote_api(method, path, **kwargs)
            if path.startswith('/wiki/v2/tasks/'):
                data['task']['move_wiki_to_docs_result']['url'] = 'https://evil.example/mindnote'
            return data
        call.side_effect = untrusted_url
        export_task(self.task)
        self.output.refresh_from_db()
        self.assertEqual(self.output.status, 'failed')
        self.assertNotIn('evil.example', self.output.url)
