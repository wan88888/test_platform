from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    """扩展用户模型"""
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='手机号')
    department = models.CharField(max_length=100, null=True, blank=True, verbose_name='部门')
    position = models.CharField(max_length=100, null=True, blank=True, verbose_name='职位')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'users_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'


class RegistrationStatsProxy(User):
    """用于后台展示注册统计，不新增数据表"""

    class Meta:
        proxy = True
        verbose_name = '注册统计'
        verbose_name_plural = '注册统计'

class UserProfile(models.Model):
    """用户配置"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    theme = models.CharField(max_length=20, default='light', verbose_name='主题')
    language = models.CharField(max_length=10, default='zh-cn', verbose_name='语言')
    timezone = models.CharField(max_length=50, default='Asia/Shanghai', verbose_name='时区')
    notifications = models.JSONField(default=dict, verbose_name='通知设置')
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户配置'
        verbose_name_plural = '用户配置'


class FeishuIdentity(models.Model):
    """Only verified Feishu identities may be associated with platform users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feishu_identities')
    app_id = models.CharField(max_length=128)
    open_id = models.CharField(max_length=128)
    tenant_key = models.CharField(max_length=128)
    display_name = models.CharField(max_length=150, blank=True)
    avatar_url = models.URLField(max_length=2048, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['app_id', 'open_id'], name='unique_feishu_app_identity'),
            models.UniqueConstraint(fields=['app_id', 'user'], name='unique_feishu_app_user'),
        ]
        verbose_name = '飞书账号关联'
        verbose_name_plural = '飞书账号关联'


class FeishuLoginAttempt(models.Model):
    """Short-lived state shared across workers; consumed with an atomic UPDATE."""
    state_hash = models.CharField(max_length=64, unique=True)
    browser_hash = models.CharField(max_length=64)
    code_verifier = models.CharField(max_length=128)
    app_id = models.CharField(max_length=128)
    redirect_uri = models.URLField(max_length=2048)
    expires_at = models.DateTimeField(db_index=True)
    consumed_at = models.DateTimeField(null=True)
