export interface ShapeStyle {
  label: string
  strokeWidth: number
  rx: number
  ry: number
  diamond: boolean
  prefix: string
}

export const SHAPE_TYPES: Record<string, ShapeStyle> = {
  input: { label: '输入框', strokeWidth: 1, rx: 0, ry: 0, diamond: false, prefix: '' },
  button: { label: '按钮', strokeWidth: 3, rx: 0, ry: 0, diamond: false, prefix: '' },
  select: { label: '下拉框', strokeWidth: 1, rx: 0, ry: 0, diamond: false, prefix: '▼ ' },
  checkbox: { label: '复选框', strokeWidth: 1, rx: 0, ry: 0, diamond: false, prefix: '☐ ' },
  api: { label: '接口调用', strokeWidth: 1, rx: 8, ry: 8, diamond: false, prefix: '◎ ' },
  variable: { label: '变量', strokeWidth: 1, rx: 0, ry: 0, diamond: true, prefix: '' },
  code: { label: '代码钩子', strokeWidth: 1, rx: 0, ry: 0, diamond: false, prefix: '</> ' },
  assert: { label: '断言', strokeWidth: 1, rx: 0, ry: 0, diamond: false, prefix: '⚖ ' },
  wait: { label: '等待', strokeWidth: 1, rx: 0, ry: 0, diamond: false, prefix: '⏱ ' },
  condition: { label: '条件', strokeWidth: 1, rx: 0, ry: 0, diamond: false, prefix: '◇ ' },
}

export const DIAMOND_PATH = 'M 60 0 L 120 20 L 60 40 L 0 20 Z'
