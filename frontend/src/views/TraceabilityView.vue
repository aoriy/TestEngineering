<script setup lang="ts">
import { onMounted, ref } from 'vue'

interface ReqRow {
  id: number
  title: string
  status: string
  testcase_ids: number[]
}
interface TcRow {
  id: number
  name: string
  requirement_ids: number[]
}

const projects = ref<{ id: number; name: string }[]>([])
const projectId = ref(0)
const reqs = ref<ReqRow[]>([])
const tcs = ref<TcRow[]>([])

async function loadProjects() {
  const r = await fetch('/api/projects')
  projects.value = await r.json()
  if (projects.value.length) projectId.value = projects.value[0].id
}

async function load() {
  if (!projectId.value) return
  const r = await fetch(`/api/traceability?project_id=${projectId.value}`)
  const d = await r.json()
  reqs.value = d.requirements
  tcs.value = d.testcases
}

function linked(reqId: number, tcId: number): boolean {
  const req = reqs.value.find((x) => x.id === reqId)
  return req ? req.testcase_ids.includes(tcId) : false
}

async function toggle(reqId: number, tcId: number) {
  const isLinked = linked(reqId, tcId)
  const method = isLinked ? 'DELETE' : 'POST'
  await fetch(`/api/testcases/${tcId}/requirements/${reqId}`, { method })
  await load()
}

onMounted(async () => {
  await loadProjects()
  await load()
})
</script>

<template>
  <div>
    <el-card>
      <el-form inline>
        <el-form-item label="项目">
          <el-select v-model="projectId" @change="load">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <div class="hint">点击单元格切换 需求 ↔ 用例 关联</div>
    </el-card>

    <el-table :data="reqs" style="margin-top: 16px">
      <el-table-column prop="id" label="需求ID" width="90" />
      <el-table-column prop="title" label="需求" width="180" />
      <el-table-column v-for="tc in tcs" :key="tc.id" :label="`#${tc.id}`" align="center">
        <template #default="{ row }">
          <el-checkbox
            :model-value="linked(row.id, tc.id)"
            @change="toggle(row.id, tc.id)"
          />
        </template>
      </el-table-column>
    </el-table>

    <el-table :data="tcs" style="margin-top: 16px">
      <el-table-column prop="id" label="用例ID" width="90" />
      <el-table-column prop="name" label="用例名称" />
    </el-table>
  </div>
</template>

<style scoped>
.hint {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>
