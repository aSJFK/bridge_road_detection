// 认证状态管理（轻量 store，无第三方依赖）
import { reactive } from 'vue'
import { getUserInfo, login as apiLogin, logout as apiLogout } from '@/api'
import { clearTokens, getRefreshToken, getToken, setTokens, redirectToLogin } from '@/api/http'
import type { UserInfo } from '@/api/types'

export const authState = reactive({
  user: null as UserInfo | null,
  initialized: false,
})

/** 根据 token 拉取用户信息 */
export async function fetchUser(): Promise<UserInfo | null> {
  if (!getToken()) {
    authState.user = null
    authState.initialized = true
    return null
  }
  try {
    authState.user = await getUserInfo()
  } catch {
    authState.user = null
    // 401 已由 http 层处理跳转
  } finally {
    authState.initialized = true
  }
  return authState.user
}

/** 登录：保存 token + 拉取用户信息 */
export async function login(username: string, password: string): Promise<UserInfo> {
  const res = await apiLogin(username, password)
  setTokens(res.access, res.refresh)
  authState.user = res.user
  authState.initialized = true
  return res.user
}

/** 退出登录 */
export async function logout() {
  const refresh = getRefreshToken()
  try {
    if (refresh) await apiLogout(refresh)
  } catch {
    // 忽略退出接口错误
  }
  clearTokens()
  authState.user = null
}

/** 登出后跳转 */
export async function doLogout() {
  await logout()
  window.location.href = '/login'
}

export { redirectToLogin }
