<script setup lang="ts">
import { onMounted, ref } from 'vue'

interface Requirement {
  id: number
  title: string
  priority: string
  status: string
  project_id: number
  testcase_ids: number[]
}

const requirements = ref<Requirement[]>([])
const projects = ref<{ id: number; name: string }[]>([])
const form = ref({ project_id: 0, title: '', priority: 'medium', status: 'draft' })

async function loadProjects() {
  const r = await fetch('/api/projects')
  projects.value = await r.json()
  if (projects.value.length && form.value.project_id === 0) {
    form.value.project_id = projects.value[0].id
  }
}

async function load() {
  const r = await fetch(`/api/requirements?project_id=${form.value.project_id}`)
  requirements.value = await r.json()
}

async function create() {
  if (!form.value.title || !form.value.project_id) return
  await fetch('/api/requirements', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value),
  })
  form.value.title = ''
  await load()
}

async function remove(id: number) {
  await fetch(`/api/requirements/${id}`, { method: 'DELETE' })
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
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="需求标题" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="form.priority">
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="create">新建需求</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="requirements" style="margin-top: 16px">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="标题" />
      <el-table-column prop="priority" label="优先级" width="100" />
      <el-table-column prop="status" label="状态" width="100" />
      <el-table-column label="关联用例" width="120">
        <template #default="{ row }">{{ row.testcase_ids.length }}</template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
