<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Graph } from '@antv/x6'

interface Step {
  id: number
  shape_id: number
  order: number
  action_type: string
  action_params: Record<string, unknown>
}
interface FlowNode {
  id: number
  page_template_id: number
  page_template_name: string
  x: number
  y: number
  steps: Step[]
}
interface FlowEdge {
  id: number
  source_node_id: number
  target_node_id: number
  trigger: string
}
interface Shape {
  id: number
  label: string
  shape_type: string
}

const route = useRoute()
const router = useRouter()
const flowId = Number(route.params.id)

const containerRef = ref<HTMLDivElement>()
const flowName = ref('')
const nodes = ref<FlowNode[]>([])
const edges = ref<FlowEdge[]>([])
const templates = ref<{ id: number; name: string }[]>([])
const selectedNodeId = ref<number | null>(null)
const selectedNode = ref<FlowNode | null>(null)
const nodeShapes = ref<Shape[]>([])
const addStepForm = ref({ shape_id: 0, action_type: 'click' })
let graph: Graph | null = null

const ACTIONS = ['click', 'input', 'select', 'assert', 'api_call', 'wait', 'condition', 'custom']

async function loadTemplates() {
  const r = await fetch('/api/page-templates')
  templates.value = await r.json()
}

async function load() {
  const r = await fetch(`/api/flows/${flowId}`)
  const f = await r.json()
  flowName.value = f.name
  nodes.value = f.nodes
  edges.value = f.edges
  if (selectedNodeId.value !== null) {
    selectedNode.value = nodes.value.find((n) => n.id === selectedNodeId.value) || null
  }
  renderGraph()
}

function renderGraph() {
  if (!graph) return
  graph.clearCells()
  for (const n of nodes.value) {
    graph.addNode({
      id: String(n.id),
      shape: 'rect',
      x: n.x,
      y: n.y,
      width: 120,
      height: 48,
      label: n.page_template_name || `#${n.id}`,
      attrs: {
        body: { fill: '#e6f4ff', stroke: '#409eff', rx: 6, ry: 6 },
        label: { fontSize: 12 },
      },
    })
  }
  for (const e of edges.value) {
    graph.addEdge({
      source: { cell: String(e.source_node_id) },
      target: { cell: String(e.target_node_id) },
      attrs: { line: { stroke: '#999', strokeWidth: 1.5, targetMarker: null } },
    })
  }
}

async function addNode(templateId: number) {
  await fetch(`/api/flows/${flowId}/nodes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ page_template_id: templateId, x: 60, y: 60 }),
  })
  await load()
}

async function selectNode(nodeId: number) {
  selectedNodeId.value = nodeId
  selectedNode.value = nodes.value.find((n) => n.id === nodeId) || null
  if (selectedNode.value) {
    const r = await fetch(`/api/page-templates/${selectedNode.value.page_template_id}`)
    const t = await r.json()
    nodeShapes.value = t.shapes
  }
}

async function addStep() {
  if (!selectedNode.value || !addStepForm.value.shape_id) return
  await fetch(`/api/flows/${flowId}/nodes/${selectedNode.value.id}/steps`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(addStepForm.value),
  })
  addStepForm.value.shape_id = 0
  await load()
}

async function removeStep(stepId: number) {
  await fetch(`/api/flows/${flowId}/nodes/${selectedNodeId.value}/steps/${stepId}`, {
    method: 'DELETE',
  })
  await load()
}

async function reorder(stepId: number, dir: -1 | 1) {
  const steps = [...(selectedNode.value?.steps || [])].sort((a, b) => a.order - b.order)
  const idx = steps.findIndex((s) => s.id === stepId)
  const jdx = idx + dir
  if (idx < 0 || jdx < 0 || jdx >= steps.length) return
  ;[steps[idx], steps[jdx]] = [steps[jdx], steps[idx]]
  await fetch(`/api/flows/${flowId}/nodes/${selectedNodeId.value}/steps/reorder`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ordered_ids: steps.map((s) => s.id) }),
  })
  await load()
}

onMounted(async () => {
  graph = new Graph({
    container: containerRef.value!,
    grid: true,
    panning: true,
    background: { color: '#f5f6f8' },
    connecting: { snap: true, allowBlank: false },
  })

  graph.on('node:moved', async ({ node }) => {
    const pos = node.getPosition()
    await fetch(`/api/flows/${flowId}/nodes/${node.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ x: pos.x, y: pos.y }),
    })
  })

  graph.on('node:click', ({ node }) => selectNode(Number(node.id)))

  graph.on('edge:connected', async ({ edge, isNew }) => {
    if (!isNew) return
    const source = Number(edge.getSourceCellId())
    const target = Number(edge.getTargetCellId())
    await fetch(`/api/flows/${flowId}/edges`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_node_id: source, target_node_id: target }),
    })
    await load()
  })

  await loadTemplates()
  await load()
})
</script>

<template>
  <div class="flow-page">
    <div class="toolbar">
      <el-button @click="router.push('/flows')">← 返回</el-button>
      <span class="title">{{ flowName }} — 流转图</span>
      <el-dropdown @command="addNode">
        <el-button type="primary">添加页面节点</el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item
              v-for="t in templates"
              :key="t.id"
              :command="t.id"
            >
              {{ t.name }}
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <div class="body">
      <div ref="containerRef" class="canvas"></div>
      <div v-if="selectedNode" class="steps">
        <h4>{{ selectedNode.page_template_name }} — 步骤</h4>
        <el-form inline size="small">
          <el-form-item label="形状">
            <el-select v-model="addStepForm.shape_id" placeholder="选择形状">
              <el-option
                v-for="s in nodeShapes"
                :key="s.id"
                :label="`${s.label || s.shape_type} (#${s.id})`"
                :value="s.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="动作">
            <el-select v-model="addStepForm.action_type">
              <el-option v-for="a in ACTIONS" :key="a" :label="a" :value="a" />
            </el-select>
          </el-form-item>
          <el-button type="primary" size="small" @click="addStep">添加步骤</el-button>
        </el-form>

        <div v-for="(s, i) in [...selectedNode.steps].sort((a, b) => a.order - b.order)" :key="s.id" class="step-row">
          <span class="idx">{{ i + 1 }}</span>
          <span class="act">{{ s.action_type }}</span>
          <span class="sid">shape#{{ s.shape_id }}</span>
          <span class="ops">
            <el-button size="small" text @click="reorder(s.id, -1)">↑</el-button>
            <el-button size="small" text @click="reorder(s.id, 1)">↓</el-button>
            <el-button size="small" text type="danger" @click="removeStep(s.id)">✕</el-button>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.flow-page {
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
.steps {
  width: 320px;
  background: #fff;
  border-left: 1px solid #eee;
  padding: 12px;
  overflow: auto;
}
.step-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-bottom: 1px solid #f0f0f0;
}
.idx {
  width: 20px;
  color: #999;
}
.act {
  font-weight: bold;
  flex: 1;
}
.sid {
  color: #999;
  font-size: 12px;
}
.ops {
  display: flex;
}
</style>
