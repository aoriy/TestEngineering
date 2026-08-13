import { createRouter, createWebHistory } from 'vue-router'
import Layout from './views/Layout.vue'
import ProjectsView from './views/ProjectsView.vue'
import RequirementsView from './views/RequirementsView.vue'
import TestCasesView from './views/TestCasesView.vue'
import TraceabilityView from './views/TraceabilityView.vue'
import PageTemplatesView from './views/PageTemplatesView.vue'
import PageCanvasView from './views/PageCanvasView.vue'
import FlowsView from './views/FlowsView.vue'
import FlowEditorView from './views/FlowEditorView.vue'
import RunsView from './views/RunsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: Layout,
      children: [
        { path: '', redirect: '/projects' },
        { path: 'projects', component: ProjectsView },
        { path: 'requirements', component: RequirementsView },
        { path: 'testcases', component: TestCasesView },
        { path: 'traceability', component: TraceabilityView },
        { path: 'page-templates', component: PageTemplatesView },
        { path: 'page-templates/:id', component: PageCanvasView },
        { path: 'flows', component: FlowsView },
        { path: 'flows/:id', component: FlowEditorView },
        { path: 'runs', component: RunsView },
      ],
    },
  ],
})

export default router
