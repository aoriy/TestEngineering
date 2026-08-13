<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const menus = [
  { path: '/projects', label: '项目管理' },
  { path: '/requirements', label: '需求管理' },
  { path: '/testcases', label: '用例管理' },
  { path: '/traceability', label: '追溯矩阵' },
  { path: '/page-templates', label: '页面模板' },
  { path: '/flows', label: '流转图' },
  { path: '/runs', label: '执行' },
]
</script>

<template>
  <el-container class="layout">
    <el-aside width="200px" class="aside">
      <div class="logo">TestEngineering</div>
      <el-menu :default-active="route.path" @select="(p: string) => router.push(p)">
        <el-menu-item v-for="m in menus" :key="m.path" :index="m.path">
          {{ m.label }}
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-main class="main">
      <router-view />
    </el-main>
  </el-container>
</template>

<style scoped>
.layout {
  height: 100vh;
}
.aside {
  background: #fff;
  border-right: 1px solid #eee;
}
.logo {
  height: 56px;
  line-height: 56px;
  text-align: center;
  font-weight: bold;
  color: #409eff;
  border-bottom: 1px solid #eee;
}
.main {
  background: #f5f6f8;
  overflow: auto;
}
</style>
