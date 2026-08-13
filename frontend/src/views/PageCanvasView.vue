<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Graph } from '@antv/x6'
import { SHAPE_TYPES } from '../shapeStyles'

interface Shape {
  id: number
  shape_type: string
  label: string
  x: number
  y: number
  width: number
  height: number
  locator_type: string
  locator_value: string
  value: string
}

const route = useRoute()
const router = useRouter()
const templateId = Number(route.params.id)

const containerRef = ref<HTMLDivElement>()
const templateName = ref('')
const selectedId = ref<number | null>(null)
const selectedShape = ref<Shape | null>(null)
let graph: Graph | null = null

async function load() {
  const r = await fetch(`/api/page-templates/${templateId}`)
  const t = await r.json()
  templateName.value = t.name
  render(t.shapes as Shape[])
}

function render(shapes: Shape[]) {
  if (!graph) return
  graph.clearCells()
  for (const s of shapes) {
    const style = SHAPE_TYPES[s.shape_type] || SHAPE_TYPES.input
    graph.addNode({
      id: String(s.id),
      shape: 'rect',
      x: s.x,
      y: s.y,
      width: s.width,
      height: s.height,
      label: (style.prefix + s.label) || s.shape_type,
      attrs: {
        body: {
          fill: fillOf(s.shape_type),
          stroke: '#409eff',
          strokeWidth: style.strokeWidth,
          rx: style.rx,
          ry: style.ry,
        },
        label: { fontSize: 12 },
      },
    })
  }
}

function fillOf(type: string): string {
  const fills: Record<string, string> = {
    variable: '#fff7e6',
    code: '#e6f4ff',
    assert: '#f0f9eb',
    api: '#f9f0ff',
    button: '#ffffff',
  }
  return fills[type] || '#ffffff'
}

async function addShape(type: string) {
  await fetch(`/api/page-templates/${templateId}/shapes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      shape_type: type,
      label: SHAPE_TYPES[type].label,
      x: 60 + Math.random() * 200,
      y: 60 + Math.random() * 200,
    }),
  })
  await load()
}

async function removeSelected() {
  if (selectedId.value === null) return
  await fetch(`/api/page-templates/${templateId}/shapes/${selectedId.value}`, {
    method: 'DELETE',
  })
  selectedId.value = null
  selectedShape.value = null
  await load()
}

async function saveSelected() {
  if (!selectedShape.value) return
  await fetch(
    `/api/page-templates/${templateId}/shapes/${selectedShape.value.id}`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        label: selectedShape.value.label,
        locator_type: selectedShape.value.locator_type,
        locator_value: selectedShape.value.locator_value,
        value: selectedShape.value.value,
      }),
    },
  )
  await load()
}

onMounted(() => {
  graph = new Graph({
    container: containerRef.value!,
    grid: true,
    panning: true,
    background: { color: '#f5f6f8' },
  })

  graph.on('node:moved', async ({ node }) => {
    const pos = node.getPosition()
    await fetch(`/api/page-templates/${templateId}/shapes/${node.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ x: pos.x, y: pos.y }),
    })
  })

  graph.on('node:click', ({ node }) => {
    selectedId.value = Number(node.id)
    fetch(`/api/page-templates/${templateId}/shapes/${node.id}`).then((r) =>
      r.json().then((s) => (selectedShape.value = s)),
    )
  })

  graph.on('blank:click', () => {
    selectedId.value = null
    selectedShape.value = null
  })

  load()
})
</script>

<template>
  <div class="canvas-page">
    <div class="toolbar">
      <el-button @click="router.push('/page-templates')">← 返回</el-button>
      <span class="title">{{ templateName }} — 页面简图</span>
      <el-dropdown @command="addShape">
        <el-button type="primary">添加形状<el-icon class="el-icon--right" /></el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item
              v-for="(s, key) in SHAPE_TYPES"
              :key="key"
              :command="key"
            >
              {{ s.prefix }}{{ s.label }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      <el-button
        type="danger"
        :disabled="selectedId === null"
        @click="removeSelected"
      >
        删除选中
      </el-button>
    </div>

    <div class="body">
      <div ref="containerRef" class="canvas"></div>
      <div v-if="selectedShape" class="props">
        <h4>形状属性</h4>
        <el-form label-width="90px" size="small">
          <el-form-item label="标签">
            <el-input v-model="selectedShape.label" />
          </el-form-item>
          <el-form-item label="定位类型">
            <el-select v-model="selectedShape.locator_type">
              <el-option label="data-testid" value="data-testid" />
              <el-option label="xpath" value="xpath" />
              <el-option label="css" value="css" />
              <el-option label="text" value="text" />
            </el-select>
          </el-form-item>
          <el-form-item label="定位值">
            <el-input v-model="selectedShape.locator_value" placeholder="定位器值" />
          </el-form-item>
          <el-form-item label="值">
            <el-input v-model="selectedShape.value" placeholder="默认值或 {{var}}" />
          </el-form-item>
          <el-button type="primary" size="small" @click="saveSelected">保存</el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.canvas-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.toolbar {
  padding: 10px 16px;
  background: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 12px;
}
.title {
  font-weight: bold;
}
.body {
  flex: 1;
  display: flex;
  min-height: 0;
}
.canvas {
  flex: 1;
  min-width: 0;
}
.props {
  width: 280px;
  background: #fff;
  border-left: 1px solid #eee;
  padding: 12px;
  overflow: auto;
}
</style>
