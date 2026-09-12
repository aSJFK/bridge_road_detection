// API 入口层：对接 Django 后端真实接口
import { http, getToken } from './http'
import type {
  LoginResult,
  UserInfo,
  HomeStats,
  DefectTypeMap,
  RecentRecord,
  DetectionTask,
  PageData,
  DefectItem,
  ReportItem,
  ReportDetail,
  ReportRating,
  DatasetItem,
  NotificationItem,
  PredictResult,
} from './types'

// ==================== 认证 ====================

/** POST /api/auth/login/ */
export function login(username: string, password: string): Promise<LoginResult> {
  return http.post<LoginResult>('/api/auth/login/', { username, password })
}

/** POST /api/auth/register/ */
export function register(data: { username: string; password: string; email?: string; phone?: string }): Promise<{ id: number; username: string; role: string }> {
  return http.post('/api/auth/register/', data)
}

/** POST /api/auth/logout/ */
export function logout(refresh: string): Promise<void> {
  return http.post('/api/auth/logout/', { refresh })
}

/** GET /api/user/info/ */
export function getUserInfo(): Promise<UserInfo> {
  return http.get<UserInfo>('/api/user/info/')
}

// ==================== 首页统计 ====================

/** GET /api/home/statistics/ */
export function getHomeStats(): Promise<HomeStats> {
  return http.get<HomeStats>('/api/home/statistics/')
}

/** GET /api/statistics/defect-types/ -> {crack: n, ...} */
export function getDefectTypes(): Promise<DefectTypeMap> {
  return http.get<DefectTypeMap>('/api/statistics/defect-types/')
}

/** GET /api/statistics/trend/?days=7 */
export function getTrend(days = 7): Promise<{ date: string; count: number }[]> {
  return http.get(`/api/statistics/trend/?days=${days}`)
}

// ==================== 检测 ====================

/** GET /api/detection/recent/ */
export function getRecentRecords(): Promise<RecentRecord[]> {
  return http.get<RecentRecord[]>('/api/detection/recent/')
}

/** GET /api/detection/tasks/ 分页 */
export function listTasks(params: Record<string, string | number> = {}): Promise<PageData<DetectionTask>> {
  const qs = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) if (v !== undefined && v !== '') qs.set(k, String(v))
  const query = qs.toString()
  return http.get<PageData<DetectionTask>>(`/api/detection/tasks/${query ? `?${query}` : ''}`)
}

/** GET /api/detection/tasks/{id}/ */
export function getTaskDetail(id: number): Promise<DetectionTask> {
  return http.get<DetectionTask>(`/api/detection/tasks/${id}/`)
}

/** POST /api/detection/tasks/  multipart 创建任务并检测 */
export function createTask(formData: FormData): Promise<{
  task: DetectionTask
  images: DetectionTask['images']
  total_defects: number
  accuracy: number
}> {
  return http.post('/api/detection/tasks/', formData, true)
}

/** POST /api/detection/predict/  multipart 单图检测（不落库） */
export function predictImage(file: File, taskId?: number): Promise<PredictResult> {
  const fd = new FormData()
  fd.append('image', file)
  if (taskId) fd.append('task_id', String(taskId))
  return http.post<PredictResult>('/api/detection/predict/', fd, true)
}

// ==================== 缺陷 ====================

/** GET /api/defects/ */
export function listDefects(params: Record<string, string | number> = {}): Promise<PageData<DefectItem>> {
  const qs = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) if (v !== undefined && v !== '') qs.set(k, String(v))
  return http.get<PageData<DefectItem>>(`/api/defects/${qs.toString() ? `?${qs}` : ''}`)
}

// ==================== 报告 ====================

/** GET /api/reports/ */
export function listReports(params: Record<string, string | number> = {}): Promise<PageData<ReportItem>> {
  const qs = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) if (v !== undefined && v !== '') qs.set(k, String(v))
  return http.get<PageData<ReportItem>>(`/api/reports/${qs.toString() ? `?${qs}` : ''}`)
}

/** GET /api/reports/{id}/ */
export function getReportDetail(id: number): Promise<ReportDetail> {
  return http.get<ReportDetail>(`/api/reports/${id}/`)
}

/** PUT /api/reports/{id}/ 修改报告（仅管理员） */
export function updateReport(id: number, data: Partial<ReportItem>): Promise<ReportItem> {
  return http.put<ReportItem>(`/api/reports/${id}/`, data)
}

/** DELETE /api/reports/{id}/ 删除报告 */
export function deleteReport(id: number): Promise<void> {
  return http.delete(`/api/reports/${id}/`)
}

/** POST /api/reports/{id}/rate/ 提交评价 */
export function rateReport(id: number, score: number, comment: string): Promise<ReportRating> {
  return http.post<ReportRating>(`/api/reports/${id}/rate/`, { score, comment })
}

/** GET /api/reports/{id}/ratings/ 评价列表 */
export function listReportRatings(id: number): Promise<ReportRating[]> {
  return http.get<ReportRating[]>(`/api/reports/${id}/ratings/`)
}

/** PUT /api/reports/ratings/{rid}/ 修改评价（仅管理员） */
export function updateRating(rid: number, data: { score: number; comment: string }): Promise<ReportRating> {
  return http.put<ReportRating>(`/api/reports/ratings/${rid}/`, data)
}

/** DELETE /api/reports/ratings/{rid}/ 删除评价（仅管理员） */
export function deleteRating(rid: number): Promise<void> {
  return http.delete(`/api/reports/ratings/${rid}/`)
}

// ==================== 数据集 ====================

/** GET /api/datasets/ */
export function listDatasets(params: Record<string, string | number> = {}): Promise<PageData<DatasetItem>> {
  const qs = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) if (v !== undefined && v !== '') qs.set(k, String(v))
  return http.get<PageData<DatasetItem>>(`/api/datasets/${qs.toString() ? `?${qs}` : ''}`)
}

// ==================== 通知 ====================

/** GET /api/notifications/messages/ */
export function listNotifications(): Promise<PageData<NotificationItem>> {
  return http.get<PageData<NotificationItem>>('/api/notifications/messages/')
}

/** 判断是否已登录 */
export function isLoggedIn(): boolean {
  return !!getToken()
}
