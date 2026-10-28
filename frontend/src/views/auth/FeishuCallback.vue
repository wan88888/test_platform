<template>
  <main class="callback-page">
    <section aria-live="polite">
      <h1>{{ $t('auth.feishuTitle') }}</h1>
      <p v-if="pending">{{ $t('auth.feishuCompleting') }}</p>
      <p v-else role="alert">{{ errorMessage }}</p>
      <el-button v-if="!pending" type="primary" @click="router.replace('/login')">
        {{ $t('auth.feishuBack') }}
      </el-button>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n()
const pending = ref(true)
const errorMessage = ref('')

onMounted(async () => {
  const { code, state, error } = route.query
  // Remove provider codes before making API calls; TestHub tokens never enter the URL.
  await router.replace({ path: '/auth/feishu/callback', query: {} })
  if (typeof state !== 'string' || (!code && !error) ||
      (code !== undefined && typeof code !== 'string') ||
      (error !== undefined && typeof error !== 'string')) {
    errorMessage.value = t('auth.feishuInvalidCallback')
    pending.value = false
    return
  }
  try {
    const result = await userStore.feishuLogin({ code, state, error })
    await router.replace(result.documents_authorized ? '/ai-generation/requirement-analysis' : '/home')
  } catch (err) {
    errorMessage.value = err.response?.data?.error || t('auth.feishuUnavailable')
    pending.value = false
  }
})
</script>

<style scoped>
.callback-page { min-height: 100vh; display: grid; place-items: center; background: #f5f7fa; padding: 24px; box-sizing: border-box; }
section { width: min(100%, 460px); padding: 32px; background: white; border-radius: 16px; text-align: center; box-sizing: border-box; }
h1 { font-size: 24px; color: #1e293b; }
p { color: #64748b; line-height: 1.7; margin: 24px 0; }
</style>
