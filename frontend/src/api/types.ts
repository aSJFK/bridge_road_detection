// 与 Django 后端对齐的数据类型

// ---------- 认证 ----------
export interface LoginResult {
  access: string
  refresh: string
  user: UserInfo
}

export interface UserInfo {
  id: number
  username: string
  email: string
  role: 'admin' | 'user'
  phone: string
  avatar: string | null
  is_active: boolean
  date_joined: string
  accuracy: number
}

// ---------- 首页统计 ----------
export interface HomeStats {
  image_count: number
  defect_count: number
  accuracy: number
}

// ---------- 缺陷类型统计（后端返回 {crack: n, ...}） ----------
export type DefectTypeMap = Record<string, number>

// ---------- 最近检测记录 ----------
export interface RecentRecord {
  id: number
  task_name: string
  created_at: string
  image_count: number
  defect_count: number
  status: string
  status_text: string
}

// ---------- 检测任务 ----------
export interface DetectionTask {
  id: number
  task_name: string
  model_name: string
  model_version: string
  image_count: number
  defect_count: number
  accuracy: number
  status: string
  started_at: string | null
  completed_at: string | null
  created_at: string
  images?: DetectionImage[]
}

export interface Defect {
  id: number
  defect_type: string
  source: string
  confidence: number
  x1: number
  y1: number
  x2: number
  y2: number
  area: number
}

export interface DetectionImage {
  id: number
  original_image: string
  result_image: string | null
  image_width: number
  image_height: number
  defects: Defect[]
  created_at: string
}

// ---------- 分页 ----------
export interface PageData<T> {
  count: number
  page: number
  page_size: number
  results: T[]
}

// ---------- 缺陷/报告/数据集 ----------
export interface DefectItem extends Defect {
  image: number
}

export interface ReportItem {
  id: number
  task: number | null
  task_name: string
  report_name: string
  total_images: number
  total_defects: number
  accuracy: number
  report_file: string | null
  image_url: string | null
  result_url: string | null
  average_score: number | null
  rating_count: number
  my_rating: ReportRating | null
  created_by: number
  created_by_name: string
  created_at: string
}

export interface ReportRating {
  id: number
  report: number
  user: number
  username: string
  user_role: string
  score: number
  comment: string
  created_at: string
}

export interface ReportDetail extends ReportItem {
  defects: Defect[]
}

export interface DatasetItem {
  id: number
  name: string
  description: string
  image_count: number
  annotation_count: number
  version: string
  status: string
  created_by: number
  created_by_name: string
  created_at: string
  updated_at: string
}

// ---------- 通知 ----------
export interface NotificationItem {
  id: number
  title: string
  content: string
  is_read: boolean
  created_at: string
}

// ---------- 检测结果（predict/task 创建） ----------
export interface PredictObject {
  type: string
  confidence: number
  bbox: number[]
  area: number
}

export interface PredictResult {
  count: number
  objects: PredictObject[]
}
