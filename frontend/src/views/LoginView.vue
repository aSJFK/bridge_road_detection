<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login as doLogin } from '@/stores/auth'
import { register } from '@/api'
import { isApiError } from '@/api/http'

const router = useRouter()
const mode = ref<'login' | 'register'>('login')

// 登录
const loginForm = reactive({ username: '', password: '' })
const loading = ref(false)

// 注册
const regForm = reactive({ username: '', password: '', confirm: '', email: '', phone: '' })
const regLoading = ref(false)

async function handleLogin() {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const user = await doLogin(loginForm.username, loginForm.password)
    ElMessage.success(`欢迎回来，${user.username}`)
    router.push('/')
  } catch (e) {
    ElMessage.error(isApiError(e) ? e.message : '登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (!regForm.username || !regForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  if (regForm.username.length < 3) {
    ElMessage.warning('用户名至少 3 个字符')
    return
  }
  if (regForm.password.length < 6) {
    ElMessage.warning('密码至少 6 位')
    return
  }
  if (regForm.password !== regForm.confirm) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  regLoading.value = true
  try {
    const data = await register({
      username: regForm.username,
      password: regForm.password,
      email: regForm.email || undefined,
      phone: regForm.phone || undefined,
    })
    ElMessage.success(`注册成功，请登录 (${data.username})`)
    mode.value = 'login'
    loginForm.username = data.username
    loginForm.password = ''
  } catch (e) {
    ElMessage.error(isApiError(e) ? e.message : '注册失败，请稍后重试')
  } finally {
    regLoading.value = false
  }
}

function switchMode(m: 'login' | 'register') {
  mode.value = m
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
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
        <h1>桥路缺陷检测系统</h1>
        <p>Bridge &amp; Road Defect Detection System</p>
      </div>

      <!-- 登录 / 注册 切换 -->
      <div class="mode-tabs">
        <button :class="{ active: mode === 'login' }" @click="switchMode('login')">登录</button>
        <button :class="{ active: mode === 'register' }" @click="switchMode('register')">注册</button>
      </div>

      <!-- 登录 -->
      <el-form v-if="mode === 'login'" label-position="top" @submit.prevent="handleLogin">
        <el-form-item label="用户名">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" size="large" clearable>
            <template #prefix><i class="bi bi-person"></i></template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          >
            <template #prefix><i class="bi bi-lock"></i></template>
          </el-input>
        </el-form-item>
        <el-button class="action-btn" type="primary" size="large" :loading="loading" @click="handleLogin">
          <i class="bi bi-box-arrow-in-right"></i>
          <span>登 录</span>
        </el-button>
      </el-form>

      <!-- 注册 -->
      <el-form v-else label-position="top" @submit.prevent="handleRegister">
        <el-form-item label="用户名">
          <el-input v-model="regForm.username" placeholder="请输入用户名（至少 3 个字符）" size="large" clearable>
            <template #prefix><i class="bi bi-person"></i></template>
          </el-input>
        </el-form-item>
        <el-form-item label="邮箱（可选）">
          <el-input v-model="regForm.email" placeholder="请输入邮箱" size="large" clearable>
            <template #prefix><i class="bi bi-envelope"></i></template>
          </el-input>
        </el-form-item>
        <el-form-item label="手机号（可选）">
          <el-input v-model="regForm.phone" placeholder="请输入手机号" size="large" clearable>
            <template #prefix><i class="bi bi-telephone"></i></template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="regForm.password" type="password" placeholder="请输入密码（至少 6 位）" size="large" show-password>
            <template #prefix><i class="bi bi-lock"></i></template>
          </el-input>
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input
            v-model="regForm.confirm"
            type="password"
            placeholder="请再次输入密码"
            size="large"
            show-password
            @keyup.enter="handleRegister"
          >
            <template #prefix><i class="bi bi-shield-lock"></i></template>
          </el-input>
        </el-form-item>
        <el-button class="action-btn" type="primary" size="large" :loading="regLoading" @click="handleRegister">
          <i class="bi bi-person-plus"></i>
          <span>注 册</span>
        </el-button>
        <p class="reg-note"><i class="bi bi-info-circle"></i> 注册账号为普通用户，管理员账号由系统固定</p>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background-color: #0a0e16;
  background-image: url('/images/hero-bg.jpg'), linear-gradient(180deg, #0a0e16, #0b1220);
  background-size: cover, auto;
  background-position: center, center;
}

.login-card {
  width: 420px;
  max-width: 100%;
  background: rgba(13, 22, 38, 0.88);
  border: 1px solid rgba(30, 144, 255, 0.35);
  border-radius: 18px;
  padding: 32px 32px 28px;
  backdrop-filter: blur(16px);
  box-shadow: 0 0 40px rgba(30, 144, 255, 0.15), 0 20px 50px rgba(0, 0, 0, 0.5);
  animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.login-brand {
  text-align: center;
  margin-bottom: 20px;
}

.brand-logo {
  width: 52px;
  height: 52px;
  margin-bottom: 10px;
}

.login-brand h1 {
  font-size: 19px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1px;
}

.login-brand p {
  font-size: 10px;
  color: #ffffff;
  letter-spacing: 0.08em;
  margin-top: 4px;
}

/* 模式切换 */
.mode-tabs {
  display: flex;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 20px;
}

.mode-tabs button {
  flex: 1;
  padding: 10px 0;
  border: none;
  background: transparent;
  color: var(--text-3);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-tabs button.active {
  background: linear-gradient(135deg, #2f9cff, #1e90ff);
  color: #fff;
  font-weight: 600;
}

.action-btn {
  width: 100%;
  margin-top: 8px;
  height: 44px;
  font-size: 15px;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #2f9cff, #1e90ff);
  border: none;
  border-radius: 10px;
}

.action-btn:hover {
  background: linear-gradient(135deg, #3aa6ff, #2b92fb);
  box-shadow: 0 8px 24px rgba(30, 144, 255, 0.4);
}

.reg-note {
  font-size: 12px;
  color: var(--text-3);
  text-align: center;
  margin-top: 14px;
}

.reg-note i {
  color: var(--blue-light);
  margin-right: 4px;
}
</style>
