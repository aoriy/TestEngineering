<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Graph } from '@antv/x6'

const containerRef = ref<HTMLDivElement>()
const health = ref('')

onMounted(() => {
  fetch('/api/health')
    .then((r) => r.json())
    .then((d) => (health.value = JSON.stringify(d)))
    .catch(() => (health.value = 'backend unreachable'))

  const graph = new Graph({
    container: containerRef.value!,
    grid: true,
    panning: true,
    background: { color: '#f5f6f8' },
  })

  graph.addNode({
    shape: 'rect',
    x: 40,
    y: 40,
    width: 120,
    height: 40,
    label: '页面简图画布占位',
    attrs: {
      body: { fill: '#fff', stroke: '#409eff', rx: 4, ry: 4 },
    },
  })
})
</script>

<template>
  <div class="layout">
    <el-header class="header">TestEngineering</el-header>
    <div ref="containerRef" class="canvas"></div>
    <div class="status">backend: {{ health || 'loading...' }}</div>
  </div>
</template>

<style scoped>
.layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.header {
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  font-weight: bold;
}
.canvas {
  flex: 1;
  min-height: 0;
}
.status {
  padding: 8px 16px;
  font-size: 12px;
  color: #888;
}
</style>
