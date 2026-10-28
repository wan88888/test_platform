<template>
  <section class="feishu-card" aria-labelledby="feishu-source-title">
    <h2 id="feishu-source-title">{{ resultOnly ? outputLabel + '输出' : '🔗 复制粘贴飞书文档链接' }}</h2>
    <template v-if="!busy">
      <el-alert v-if="access && !access.linked" title="请使用飞书账号登录后使用此功能。" type="info" :closable="false" />
      <div v-else class="access-row">
        <span>{{ authorized ? '飞书文档访问已授权' : '请授权所选输出方式的飞书文档访问' }}</span>
        <el-button :loading="authorizing" :disabled="!access?.configured" @click="authorize">
          {{ authorized ? '重新授权' : '授权飞书文档访问' }}
        </el-button>
        <el-button v-if="access?.authorized" text @click="disconnect">取消授权</el-button>
      </div>
      <el-form v-if="!resultOnly" label-position="top" @submit.prevent="generate">
        <el-form-item label="飞书文档链接">
          <el-input v-model="sourceUrl" maxlength="2048" clearable @change="saveDraft" />
        </el-form-item>
        <el-form-item label="用例标题">
          <el-input v-model="title" maxlength="200" placeholder="例如：登录与权限管理" @change="saveDraft" />
        </el-form-item>
        <el-form-item label="生成格式">
          <el-select v-model="outputType" class="format-select" @change="saveDraft">
            <el-option label="飞书表格" value="sheet" />
            <el-option label="飞书思维笔记" value="mindnote" />
          </el-select>
        </el-form-item>
        <el-button type="primary" size="large" :disabled="!sourceUrl.trim() || !authorized" @click="generate">生成测试用例</el-button>
      </el-form>
    </template>
    <p v-if="error" role="alert">{{ error }}</p>
    <div v-if="lastTask" class="export-status" aria-live="polite">
      <strong>最近一次{{ resultLabel }}输出</strong>
      <p v-if="output">{{ statusText }}</p>
      <p v-if="output?.error" role="alert">{{ output.error }}</p>
      <p v-if="output?.status === 'failed' && output?.url" class="hint">重试会继续本次写入，请暂勿手动修改已生成的用例。</p>
      <a v-if="output?.url" :href="output.url" target="_blank" rel="noopener noreferrer">{{ output.status === 'succeeded' ? '打开' + resultLabel : '查看已创建的' + resultLabel + '（同步未完成）' }}</a>
      <el-button v-if="output?.status === 'failed' && output?.task_status === 'completed'" :loading="retrying" @click="retry">重试写入已有结果</el-button>
      <el-button text @click="refreshOutput">刷新状态</el-button>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import api from '@/utils/api'
import { useUserStore } from '@/stores/user'

const props = defineProps({ busy: Boolean, resultOnly: Boolean, taskId: { type: String, default: '' } })
const emit = defineEmits(['generate'])
const user = useUserStore()
const key = `testhub-feishu-generation-${user.user?.id}`
const sourceUrl = ref('')
const title = ref('')
const outputType = ref('sheet')
const lastTask = ref('')
const output = ref(null)
const access = ref(null)
const error = ref('')
const authorizing = ref(false)
const retrying = ref(false)
let timer
let stopped = false
let refreshing = false
const selectedType = computed(() => props.resultOnly ? output.value?.output_type || 'sheet' : outputType.value)
const outputLabel = computed(() => selectedType.value === 'mindnote' ? '飞书思维笔记' : '飞书表格')
const resultLabel = computed(() => output.value?.output_type === 'mindnote' ? '飞书思维笔记' : '飞书表格')
const authorized = computed(() => selectedType.value === 'mindnote' ? access.value?.mindnote_authorized : access.value?.authorized)
const statusText = computed(() => {
  if (output.value?.task_status === 'failed') return '用例生成失败，请在平台查看生成记录。'
  return { pending: '等待用例生成完成', running: `正在写入并校验${resultLabel.value}`, succeeded: `已写入 ${output.value?.case_count || 0} 条用例`, failed: '用例已保留，飞书同步失败', uncertain: '操作结果待核对，请先检查飞书文档库或我的空间' }[output.value?.status] || '正在读取同步状态'
})
function saveDraft() {
  sessionStorage.setItem(key, JSON.stringify({ sourceUrl: sourceUrl.value, title: title.value, taskId: lastTask.value,
    outputType: selectedType.value }))
}
async function refreshAccess() {
  try { access.value = (await api.get('/requirement-analysis/feishu/access/')).data }
  catch { error.value = '无法检查飞书文档授权，请刷新页面重试。' }
}
async function authorize() {
  authorizing.value = true
  error.value = ''
  saveDraft()
  try {
    const { data } = await api.post('/requirement-analysis/feishu/authorize/', { output_type: selectedType.value })
    window.location.assign(data.authorize_url)
  } catch (err) {
    error.value = err.response?.data?.error || '授权暂时不可用，请稍后重试。'
    authorizing.value = false
  }
}
async function disconnect() {
  try { await api.delete('/requirement-analysis/feishu/access/'); await refreshAccess() }
  catch { error.value = '取消授权失败，请重试。' }
}
function generate() {
  error.value = ''
  saveDraft()
  emit('generate', { title: title.value.trim(), url: sourceUrl.value.trim(),
    outputType: outputType.value })
}
async function refreshOutput() {
  clearTimeout(timer)
  if (!lastTask.value || stopped || refreshing) return
  refreshing = true
  try {
    output.value = (await api.get(`/requirement-analysis/feishu/tasks/${encodeURIComponent(lastTask.value)}/`)).data
    error.value = ''
    if (['pending', 'running'].includes(output.value.status) && !['failed', 'cancelled'].includes(output.value.task_status)) {
      timer = setTimeout(refreshOutput, 4000)
    }
  } catch { error.value = '无法读取飞书同步状态，请点击刷新状态。' }
  finally { refreshing = false }
}
async function retry() {
  retrying.value = true
  try {
    await api.post(`/requirement-analysis/feishu/tasks/${encodeURIComponent(lastTask.value)}/`)
    await refreshOutput()
  } catch (err) { error.value = err.response?.data?.error || '重试失败，请重新授权后再试。' }
  finally { retrying.value = false }
}
watch(() => props.taskId, (value) => {
  if (value) { lastTask.value = value; output.value = null; saveDraft(); refreshOutput() }
})
onMounted(() => {
  try {
    const draft = JSON.parse(sessionStorage.getItem(key) || '{}')
    sourceUrl.value = draft.sourceUrl || ''
    title.value = draft.title || ''
    outputType.value = draft.outputType === 'mindnote' ? 'mindnote' : 'sheet'
    lastTask.value = props.taskId || draft.taskId || ''
  } catch { /* Ignore invalid local draft. */ }
  refreshAccess()
  refreshOutput()
})
onBeforeUnmount(() => { stopped = true; clearTimeout(timer) })
</script>

<style scoped>
.feishu-card { background: white; border: 1px solid #dce5ef; border-radius: 16px; padding: 30px; margin-bottom: 28px; color: #2c3e50; box-shadow: 0 3px 12px #172b4d0a; }
h2 { margin: 0 0 12px; font-size: 25px; }
p { line-height: 1.7; }
.access-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin: 20px 0; }
.access-row :deep(.el-button) { margin: 0; }
.access-row :deep(.el-button.is-text) { padding-inline: 0; }
.hint { color: #64748b; font-size: 13px; }
.format-select { width: 100%; }
.export-status { border-top: 1px solid #e5e7eb; margin-top: 24px; padding-top: 20px; }
a { color: #2563eb; margin-right: 16px; }
</style>
