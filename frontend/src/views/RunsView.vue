<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

interface TestCase {
  id: number
  name: string
  project_id: number
}
interface TestRun {
  id: number
  run_id: string
  testcase_id: number | null
  status: string
  exit_code: number | null
  started_at: string | null
  finished_at: string | null
}

const testcases = ref<TestCase[]>([])
const runs = ref<TestRun[]>([])
const form = ref({ testcase_id: 0, executor: 'api' })
const selectedRun = ref<TestRun | null>(null)
const logText = ref('')
const logVisible = ref(false)
let timer: number | undefined

async function loadTestcases() {
  const r = await fetch('/api/testcases')
  testcases.value = await r.json()
}

async function loadRuns() {
  const r = await fetch('/api/runs')
  runs.value = await r.json()
  if (runs.value.some((x) => x.status === 'running' || x.status === 'pending')) {
    startPolling()
  }
}

function startPolling() {
  if (timer) return
  timer = window.setInterval(loadRuns, 2000)
}

async function trigger() {
  if (!form.value.testcase_id) return
  await fetch('/api/runs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value),
  })
  await loadRuns()
  startPolling()
}

async function viewLog(run: TestRun) {
  selectedRun.value = run
  const r = await fetch(`/api/runs/${run.run_id}/log`)
  logText.value = await r.text()
  logVisible.value = true
}

function reportUrl(run: TestRun) {
  return `/api/runs/${run.run_id}/report`
}

const statusTag = (s: string) =>
  ({ pending: 'info', running: 'warning', done: 'success', failed: 'danger', timeout: 'danger', cancelled: 'info' })[
    s
  ] || 'info'

onMounted(async () => {
  await loadTestcases()
  await loadRuns()
})
onUnmounted(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <div>
    <el-card>
      <el-form inline>
        <el-form-item label="用例">
          <el-select v-model="form.testcase_id" placeholder="选择用例" filterable>
            <el-option v-for="t in testcases" :key="t.id" :label="`${t.name} (#${t.id})`" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行器">
          <el-select v-model="form.executor" style="width: 120px">
            <el-option label="API" value="api" />
            <el-option label="UI" value="ui" disabled />
            <el-option label="性能" value="perf" disabled />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="trigger">执行</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="runs" style="margin-top: 16px">
      <el-table-column prop="run_id" label="Run ID" width="160" />
      <el-table-column prop="testcase_id" label="用例" width="80" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusTag(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="exit_code" label="退出码" width="80" />
      <el-table-column prop="started_at" label="开始时间" width="180" />
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button size="small" @click="viewLog(row)">日志</el-button>
          <a :href="reportUrl(row)" target="_blank">
            <el-button size="small" type="primary" :disabled="row.status === 'pending'">报告</el-button>
          </a>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="logVisible" :title="`日志 — ${selectedRun?.run_id}`" width="70%">
      <pre class="log">{{ logText }}</pre>
    </el-dialog>
  </div>
</template>

<style scoped>
.log {
  max-height: 60vh;
  overflow: auto;
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  font-size: 12px;
  white-space: pre-wrap;
}
</style>
