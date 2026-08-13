<script setup lang="ts">
import { onMounted, ref } from 'vue'

interface Project {
  id: number
  name: string
  description: string | null
}

const projects = ref<Project[]>([])
const name = ref('')
const description = ref('')

async function load() {
  const r = await fetch('/api/projects')
  projects.value = await r.json()
}

async function create() {
  if (!name.value) return
  await fetch('/api/projects', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: name.value, description: description.value }),
  })
  name.value = ''
  description.value = ''
  await load()
}

async function remove(id: number) {
  await fetch(`/api/projects/${id}`, { method: 'DELETE' })
  await load()
}

onMounted(load)
</script>

<template>
  <div>
    <el-card>
      <el-form inline>
        <el-form-item label="名称">
          <el-input v-model="name" placeholder="项目名" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="description" placeholder="描述" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="create">新建项目</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="projects" style="margin-top: 16px">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
