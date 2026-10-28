<template>
  <div class="feishu-login" aria-live="polite">
    <el-button type="primary" size="large" :loading="starting" @click="startLogin">
      {{ $t('auth.feishuContinue') }}
    </el-button>
    <p v-if="message" class="status-message" role="alert">{{ message }}</p>
    <p class="hint">{{ $t('auth.feishuAccountHint') }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import feishuAuth from '@/api/feishu-auth'

const { t } = useI18n()
const starting = ref(false)
const message = ref('')

async function startLogin() {
  if (starting.value) return
  starting.value = true
  message.value = ''
  try {
    const { data } = await feishuAuth.post('/authorize/')
    const url = new URL(data.authorize_url)
    if (url.origin !== 'https://accounts.feishu.cn' || url.pathname !== '/open-apis/authen/v1/authorize') {
      throw new Error('Unexpected authorization URL')
    }
    window.location.assign(url.href)
  } catch (error) {
    message.value = error.response?.status === 503
      ? t('auth.feishuNotConfigured')
      : error.response?.data?.error || t('auth.feishuUnavailable')
    starting.value = false
  }
}

</script>

<style scoped>
.feishu-login { text-align: center; color: #334155; }
.status-message { margin: 12px 0 0; padding: 12px; border-radius: 8px; background: #fff7ed; color: #9a3412; font-size: 13px; line-height: 1.6; }
.hint { color: #64748b; font-size: 12px; margin: 12px 0 0; line-height: 1.6; }
.el-button { width: 100%; height: 52px; border-radius: 10px; font-size: 17px; font-weight: 600; --el-color-primary: #245ff2; --el-color-primary-light-3: #4b7cf5; --el-color-primary-dark-2: #1c4cc2; }
</style>
