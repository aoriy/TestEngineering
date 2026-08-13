<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

interface Flow {
  id: number
  name: string
  description: string | null
  project_id: number
  nodes: unknown[]
}

const router = useRouter()
const flows = ref<Flow[]>([])
const projects = ref<{ id: number; name: string }[]>([])
const form = ref({ project_id: 0, name: '', description: '' })

async function loadProjects() {
  const r = await fetch('/api/projects')
  projects.value = await r.json()
  if (projects.value.length && form.value.project_id === 0) {
    form.value.project_id = projects.value[0].id
  }
}

async function load() {
  const r = await fetch(`/api/flows?project_id=${form.value.project_id}`)
  flows.value = await r.json()
}

async function create() {
  if (!form.value.name || !form.value.project_id) return
  await fetch('/api/flows', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value),
  })
  form.value.name = ''
  form.value.description = ''
  await load()
}

async function remove(id: number) {
  await fetch(`/api/flows/${id}`, { method: 'DELETE' })
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
          <el-input v-model="form.name" placeholder="流程名" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" placeholder="描述" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="create">新建流程</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="flows" style="margin-top: 16px">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column label="节点数" width="100">
        <template #default="{ row }">{{ row.nodes.length }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="router.push(`/flows/${row.id}`)">
            编辑流转图
          </el-button>
          <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
