<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authState, doLogout, fetchUser } from '@/stores/auth'

const route = useRoute()
const router = useRouter()

// 基础导航（所有登录用户可见）
const baseNavs = [
  { path: '/', name: '首页' },
  { path: '/detection', name: '检测分析' },
  { path: '/defects', name: '缺陷管理' },
  { path: '/reports', name: '报告管理' },
  { path: '/statistics', name: '统计报表' },
  { path: '/datasets', name: '数据集管理' },
]

// 系统管理仅管理员可见
const adminNavs = [{ path: '/system', name: '系统管理' }]

const navs = computed(() => {
  if (authState.user?.role === 'admin') {
    return [...baseNavs, ...adminNavs]
  }
  return baseNavs
})

const activePath = computed(() => route.path)
const username = computed(() => authState.user?.username ?? '管理员')
const roleText = computed(() => {
  const map: Record<string, string> = { admin: '管理员', user: '普通用户' }
  return map[authState.user?.role ?? ''] ?? '管理员'
})

function init() {
  fetchUser()
}

async function onUserCommand(cmd: string) {
  if (cmd === 'logout') {
    await doLogout()
  }
}

onMounted(init)
</script>

<template>
  <header class="navbar">
    <div class="navbar-inner">
      <!-- Logo -->
      <RouterLink to="/" class="brand">
        <svg class="brand-logo" viewBox="0 0 48 48" fill="none" aria-hidden="true">
          <rect x="1.5" y="1.5" width="45" height="45" rx="11" fill="#1e90ff" />
          <path
            d="M10 30 L16 20 L20 27 L24 16 L29 25 L33 21 L38 28"
            stroke="#fff"
            stroke-width="2.6"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <path d="M10 35 L38 35" stroke="#bfe0ff" stroke-width="2" stroke-linecap="round" />
        </svg>
        <div class="brand-text">
          <h1>桥路缺陷检测系统</h1>
          <p>Bridge &amp; Road Defect Detection System</p>
        </div>
      </RouterLink>

      <!-- 导航 -->
      <nav class="menu">
        <RouterLink
          v-for="n in navs"
          :key="n.path"
          :to="n.path"
          class="menu-item"
          :class="{ active: activePath === n.path }"
        >
          <span>{{ n.name }}</span>
        </RouterLink>
      </nav>

      <!-- 右侧 -->
      <div class="navbar-right">
        <el-dropdown trigger="click" @command="onUserCommand">
          <div class="user">
            <span class="user-avatar">{{ username.charAt(0) }}</span>
            <div class="user-meta">
              <span class="user-name">{{ username }}</span>
              <span class="user-role">{{ roleText }}</span>
            </div>
            <i class="bi bi-chevron-down user-caret"></i>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item divided command="logout"><i class="bi bi-box-arrow-right"></i> 退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  height: 64px;
  background: linear-gradient(180deg, #000000 0%, #0a0d14 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 2px 18px rgba(0, 0, 0, 0.5);
}

.navbar-inner {
  max-width: 1440px;
  height: 100%;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  align-items: center;
  gap: 32px;
}

/* Logo */
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.brand-logo {
  width: 42px;
  height: 42px;
  filter: drop-shadow(0 0 8px rgba(30, 144, 255, 0.45));
}

.brand-text h1 {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.5px;
  white-space: nowrap;
  background: linear-gradient(90deg, #ffffff, #9cc6f5);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-text p {
  font-size: 9px;
  color: #ffffff;
  letter-spacing: 0.08em;
  white-space: nowrap;
}

/* 菜单 */
.menu {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.menu-item {
  position: relative;
  padding: 9px 15px;
  font-size: 14px;
  color: #ffffff;
  white-space: nowrap;
  border-radius: 8px;
  transition: color 0.2s ease, background 0.2s ease;
}

.menu-item::after {
  content: '';
  position: absolute;
  left: 15px;
  right: 15px;
  bottom: 4px;
  height: 2px;
  border-radius: 2px;
  background: linear-gradient(90deg, #4da3ff, #2fd6d6);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.25s ease;
}

.menu-item:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.menu-item:hover::after {
  transform: scaleX(0.5);
}

.menu-item.active {
  color: #fff;
  font-weight: 600;
}

.menu-item.active::after {
  transform: scaleX(1);
}

/* 右侧 */
.navbar-right {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-shrink: 0;
}

.user {
  display: flex;
  align-items: center;
  gap: 9px;
  cursor: pointer;
  padding: 5px 8px;
  border-radius: 10px;
  transition: background 0.2s ease;
}

.user:hover {
  background: rgba(255, 255, 255, 0.07);
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4da3ff, #1e90ff);
  box-shadow: 0 0 10px rgba(30, 144, 255, 0.4);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-meta {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}

.user-name {
  font-size: 13px;
  color: #e6eef8;
}

.user-role {
  font-size: 10px;
  color: #ffffff;
}

.user-caret {
  font-size: 11px;
  color: #ffffff;
}

/* 移动端 */
@media (max-width: 1024px) {
  .menu {
    display: none;
  }
  .navbar-inner {
    gap: 16px;
    justify-content: space-between;
  }
}

@media (max-width: 600px) {
  .brand-text p {
    display: none;
  }
  .user-meta {
    display: none;
  }
  .navbar-inner {
    padding: 0 14px;
  }
}
</style>
