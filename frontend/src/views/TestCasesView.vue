<script setup lang="ts">
import { onMounted, ref } from 'vue'

interface TestCase {
  id: number
  name: string
  priority: string
  status: string
  project_id: number
  requirement_ids: number[]
}

const testcases = ref<TestCase[]>([])
const projects = ref<{ id: number; name: string }[]>([])
const form = ref({ project_id: 0, name: '', priority: 'medium', status: 'draft' })

async function loadProjects() {
  const r = await fetch('/api/projects')
  projects.value = await r.json()
  if (projects.value.length && form.value.project_id === 0) {
    form.value.project_id = projects.value[0].id
  }
}

async function load() {
  const r = await fetch(`/api/testcases?project_id=${form.value.project_id}`)
  testcases.value = await r.json()
}

async function create() {
  if (!form.value.name || !form.value.project_id) return
  await fetch('/api/testcases', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value),
  })
  form.value.name = ''
  await load()
}

async function remove(id: number) {
  await fetch(`/api/testcases/${id}`, { method: 'DELETE' })
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
          <el-select v-model="form.project_id" @change="load">
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="用例名称" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="form.priority">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="create">新建用例</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="testcases" style="margin-top: 16px">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="priority" label="优先级" width="100" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="关联需求" width="120">
        <template #default="{ row }">{{ row.requirement_ids.length }}</template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
