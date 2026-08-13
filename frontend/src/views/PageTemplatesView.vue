<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

interface PageTemplate {
  id: number
  name: string
  url: string
  project_id: number
  shapes: unknown[]
}

const router = useRouter()
const templates = ref<PageTemplate[]>([])
const projects = ref<{ id: number; name: string }[]>([])
const form = ref({ project_id: 0, name: '', url: '' })

async function loadProjects() {
  const r = await fetch('/api/projects')
  projects.value = await r.json()
  if (projects.value.length && form.value.project_id === 0) {
    form.value.project_id = projects.value[0].id
  }
}

async function load() {
  const r = await fetch(`/api/page-templates?project_id=${form.value.project_id}`)
  templates.value = await r.json()
}

async function create() {
  if (!form.value.name || !form.value.project_id) return
  await fetch('/api/page-templates', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value),
  })
  form.value.name = ''
  form.value.url = ''
  await load()
}

async function remove(id: number) {
  await fetch(`/api/page-templates/${id}`, { method: 'DELETE' })
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
          <el-input v-model="form.name" placeholder="页面名" />
        </el-form-item>
        <el-form-item label="URL">
          <el-input v-model="form.url" placeholder="/login 或完整地址" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="create">新建页面</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="templates" style="margin-top: 16px">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="url" label="URL" />
      <el-table-column label="形状数" width="100">
        <template #default="{ row }">{{ row.shapes.length }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="router.push(`/page-templates/${row.id}`)">
            编辑画布
          </el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
