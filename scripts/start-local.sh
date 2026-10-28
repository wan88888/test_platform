#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"
PYTHON="$ROOT/venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
fi
if [[ ! -x "$PYTHON" ]]; then
  echo 'Create venv/ or .venv/ and install requirements.txt first.' >&2
  exit 1
fi
if [[ ! -x frontend/node_modules/.bin/vite ]]; then
  echo 'Install frontend dependencies first: cd frontend && npm ci' >&2
  exit 1
fi
export DJANGO_SETTINGS_MODULE=backend.local_settings
export TESTHUB_BACKEND_URL=http://127.0.0.1:8001
export JUDGE_MOCK=1
export REDIS_URL=redis://127.0.0.1:6379/15

"$PYTHON" - <<'PY'
import socket
for port in (3001, 8001):
    with socket.socket() as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('127.0.0.1', port))
        except OSError:
            raise SystemExit(f'Port {port} is occupied; stop the existing demo first.')
PY

"$PYTHON" manage.py makemigrations --noinput
"$PYTHON" manage.py migrate --noinput
"$PYTHON" manage.py shell <<'PY'
import secrets
from django.conf import settings
from django.contrib.auth import get_user_model
from apps.projects.models import Project, ProjectMember
User = get_user_model()
user, created = User.objects.get_or_create(username='localadmin', defaults={
    'email': 'localadmin@example.test', 'is_staff': True, 'is_superuser': True,
})
if created:
    password = secrets.token_urlsafe(15)
    user.set_password(password)
    user.save()
    path = settings.LOCAL_DIR / 'admin-password.txt'
    path.write_text(password + '\n')
    path.chmod(0o600)
project, _ = Project.objects.get_or_create(name='本地体验项目', owner=user, defaults={
    'description': '用于体验用例管理、测试计划和二次开发的本地项目。',
})
ProjectMember.objects.get_or_create(project=project, user=user, defaults={'role': 'owner'})
print('账号: localadmin; 密码文件: .local/admin-password.txt')
PY

BACKEND_PID=''
FRONTEND_PID=''
cleanup() {
  [[ -z "$BACKEND_PID" ]] || kill "$BACKEND_PID" 2>/dev/null || true
  [[ -z "$FRONTEND_PID" ]] || kill "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 130' INT TERM
"$PYTHON" -m daphne -b 127.0.0.1 -p 8001 backend.asgi:application &
BACKEND_PID=$!
(cd frontend && exec node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 3001 --strictPort) &
FRONTEND_PID=$!
echo "TestHub: http://127.0.0.1:3001 | API: http://127.0.0.1:8001/api/docs/"
while kill -0 "$BACKEND_PID" 2>/dev/null && kill -0 "$FRONTEND_PID" 2>/dev/null; do
  sleep 2
done
echo 'A local service exited; stopping the other service.' >&2
exit 1
