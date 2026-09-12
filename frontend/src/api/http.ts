// 统一 API 请求层
// 处理：GET/POST/PUT/DELETE、文件上传、JWT Token、错误处理、401 自动跳转登录

const BASE_URL = '' // 同源（vite 代理 /api -> 127.0.0.1:8000）
const TOKEN_KEY = 'bridge_access_token'
const REFRESH_KEY = 'bridge_refresh_token'

// ---------- Token 管理 ----------
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_KEY)
}

export function setTokens(access: string, refresh?: string) {
  localStorage.setItem(TOKEN_KEY, access)
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

export function redirectToLogin() {
  clearTokens()
  if (!window.location.pathname.startsWith('/login')) {
    window.location.href = '/login'
  }
}

// ---------- 请求核心 ----------
export interface ApiError {
  status: number
  message: string
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
    this.name = 'ApiError'
  }
}

async function request<T>(method: string, url: string, body?: unknown, options?: { isFormData?: boolean }): Promise<T> {
  const headers: Record<string, string> = { Accept: 'application/json' }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  let payload: BodyInit | undefined
  if (body !== undefined) {
    if (options?.isFormData) {
      payload = body as FormData
    } else {
      headers['Content-Type'] = 'application/json'
      payload = JSON.stringify(body)
    }
  }

  // 登录/注册接口不参与 token 过期跳转逻辑
  const isAuthEndpoint = url.startsWith('/api/auth/')

  let res: Response
  try {
    res = await fetch(BASE_URL + url, { method, headers, body: payload })
  } catch {
    // 网络错误（后端未启动等）
    throw new ApiError(0, '无法连接服务器，请检查后端服务是否已启动')
  }

  // 401：token 过期或无效（登录失败除外，登录失败应返回具体错误信息）
  if (res.status === 401 && !isAuthEndpoint) {
    redirectToLogin()
    throw new ApiError(401, '登录已过期，请重新登录')
  }

  // 尝试解析统一格式 {code, data, message}
  let data: any = null
  try {
    data = await res.json()
  } catch {
    throw new ApiError(res.status, `请求失败 (${res.status})`)
  }

  if (!res.ok || (data && typeof data === 'object' && 'code' in data && data.code !== 200 && data.code !== 201)) {
    const code = res.ok && data?.code ? data.code : res.status
    throw new ApiError(code, data?.message || `请求失败 (${res.status})`)
  }

  // 统一格式：返回 data 字段
  if (data && typeof data === 'object' && 'data' in data && 'code' in data) {
    return data.data as T
  }
  return data as T
}

// ---------- 导出方法 ----------
export const http = {
  get: <T>(url: string): Promise<T> => request<T>('GET', url),
  post: <T>(url: string, body?: unknown, isFormData = false): Promise<T> =>
    request<T>('POST', url, body, { isFormData }),
  put: <T>(url: string, body?: unknown, isFormData = false): Promise<T> =>
    request<T>('PUT', url, body, { isFormData }),
  delete: <T>(url: string): Promise<T> => request<T>('DELETE', url),
}

export function isApiError(e: unknown): e is ApiError {
  return e instanceof ApiError
}

/** 将后端返回的绝对媒体 URL（如 http://127.0.0.1:8000/media/x.jpg）归一化为当前站点相对路径 */
export function mediaUrl(url: string | null | undefined): string {
  if (!url) return ''
  try {
    const u = new URL(url, window.location.origin)
    // 本地开发：后端在 127.0.0.1:8000，前端在 5173，走同源代理
    if (u.origin && u.origin !== window.location.origin) {
      return u.pathname
    }
    return u.pathname
  } catch {
    return url
  }
}
