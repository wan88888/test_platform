"""Authenticated, user-scoped endpoints for Feishu document access."""
import threading

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.feishu import is_configured, start_authorization
from apps.users.models import FeishuDocumentGrant, FeishuIdentity
from .feishu_documents import DOCUMENT_SCOPES, MINDNOTE_SCOPES, FeishuDocumentError, get_token, export_task
from .models import FeishuCaseExport


@never_cache
@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def document_access(request):
    if request.method == 'DELETE':
        FeishuDocumentGrant.objects.filter(user=request.user).delete()
        return Response({'authorized': False})
    authorized = False
    mindnote_authorized = False
    try:
        get_token(request.user)
        authorized = True
        get_token(request.user, 'mindnote')
        mindnote_authorized = True
    except FeishuDocumentError:
        pass
    return Response({'configured': is_configured(), 'authorized': authorized, 'mindnote_authorized': mindnote_authorized,
                     'scopes': DOCUMENT_SCOPES,
                     'linked': FeishuIdentity.objects.filter(user=request.user, app_id=settings.FEISHU_APP_ID).exists()})


@never_cache
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def document_authorize(request):
    if not FeishuIdentity.objects.filter(user=request.user, app_id=settings.FEISHU_APP_ID,
            tenant_key__in=settings.FEISHU_ALLOWED_TENANT_KEYS).exists():
        return Response({'error': '请先使用飞书账号登录，再授权文档访问。'}, status=403)
    output_type = request.data.get('output_type', 'sheet')
    if output_type not in ('sheet', 'mindnote'):
        return Response({'error': '请选择飞书表格或飞书思维笔记。'}, status=400)
    return start_authorization(request, document_user=request.user,
                               document_scopes=MINDNOTE_SCOPES if output_type == 'mindnote' else DOCUMENT_SCOPES)


@never_cache
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def export_status(request, task_id):
    output = get_object_or_404(FeishuCaseExport.objects.select_related('task', 'task__created_by'),
                               task__task_id=task_id, task__created_by=request.user)
    if request.method == 'POST':
        if output.task.status != 'completed' or output.status not in ('pending', 'failed'):
            return Response({'error': '当前状态不可重试，请等待生成或同步结束。'}, status=409)
        try:
            get_token(request.user, output.output_type)
        except FeishuDocumentError as exc:
            return Response({'error': str(exc)}, status=exc.status)
        def run():
            from django.db import close_old_connections
            close_old_connections()
            try:
                export_task(output.task)
            finally:
                close_old_connections()
        threading.Thread(target=run, daemon=True).start()
        return Response({'status': 'running'}, status=202)
    return Response({'status': output.status, 'error': output.error, 'url': output.url,
                     'output_type': output.output_type,
                     'task_status': output.task.status,
                     'case_count': max(0, len(output.rows) - 1)})
