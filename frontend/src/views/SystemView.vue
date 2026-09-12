<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { authState, fetchUser } from '@/stores/auth'
import { listReports, deleteReport, updateReport } from '@/api'
import { http } from '@/api/http'
import { isApiError } from '@/api/http'
import type { ReportItem } from '@/api/types'

const router = useRouter()
const loading = ref(false)
const logs = ref<any[]>([])
const roleMap: Record<string, string> = { admin: '管理员', user: '普通用户' }
const isAdmin = computed(() => authState.user?.role === 'admin')

// 报告管理（管理员）
const reports = ref<ReportItem[]>([])
const reportTotal = ref(0)
const reportPage = ref(1)
const reportLoading = ref(false)
const startDate = ref('')
const endDate = ref('')

async function loadLogs() {
  try {
    const data = await http.get<any>('/api/notifications/logs/?page_size=10')
    logs.value = data.results ?? []
  } catch (e) {
    // 非管理员访问时静默失败
    if (!(isApiError(e) && e.status === 403)) {
      ElMessage.warning('操作日志加载失败')
    }
  }
}

async function loadReports() {
  reportLoading.value = true
  try {
    const params: Record<string, string | number> = { page: reportPage.value, page_size: 10 }
    if (startDate.value) params.start_date = startDate.value
    if (endDate.value) params.end_date = endDate.value
    const data = await listReports(params)
    reports.value = data.results
    reportTotal.value = data.count
  } catch (e) {
    ElMessage.error(isApiError(e) ? e.message : '报告加载失败')
  } finally {
    reportLoading.value = false
  }
}

function searchReports() {
  reportPage.value = 1
  loadReports()
}

function clearReportFilter() {
  startDate.value = ''
  endDate.value = ''
  reportPage.value = 1
  loadReports()
}

function onReportPage(p: number) {
  reportPage.value = p
  loadReports()
}

async function removeReport(row: ReportItem) {
  try {
    await ElMessageBox.confirm(`确认删除用户「${row.created_by_name}」的报告「${row.report_name}」？`, '删除报告', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  try {
    await deleteReport(row.id)
    ElMessage.success('报告已删除')
    loadReports()
  } catch (e) {
    ElMessage.error(isApiError(e) ? e.message : '删除失败')
  }
}

async function editReport(row: ReportItem) {
  try {
    const { value } = await ElMessageBox.prompt('修改报告名称', '编辑报告', {
      confirmButtonText: '保存',
      cancelButtonText: '取消',
      inputValue: row.report_name,
      inputValidator: (v: string) => (v.trim() ? true : '报告名称不能为空'),
    })
    await updateReport(row.id, { report_name: value.trim() })
    ElMessage.success('报告已更新')
    loadReports()
  } catch {
    // 取消或失败
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await fetchUser()
    if (!isAdmin.value) {
      ElMessage.warning('系统管理仅限管理员访问')
      router.replace('/')
      return
    }
    await Promise.all([loadLogs(), loadReports()])
  } catch (e) {
    ElMessage.error(isApiError(e) ? e.message : '数据加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="page-wrap">
    <div class="page-head">
      <h2>系统管理</h2>
      <p>用户权限、角色管理及系统配置与维护</p>
    </div>

    <div class="grid">
      <!-- 用户信息 -->
      <div class="panel">
        <h3>当前用户</h3>
        <div v-if="authState.user" class="user-card">
          <div class="user-avatar">{{ authState.user.username.charAt(0) }}</div>
          <div class="user-info">
            <p class="user-name">{{ authState.user.username }}</p>
            <p class="user-role">{{ roleMap[authState.user.role] ?? authState.user.role }}</p>
          </div>
          <div class="user-detail">
            <p><span>邮箱：</span>{{ authState.user.email || '—' }}</p>
            <p><span>手机号：</span>{{ authState.user.phone || '—' }}</p>
            <p><span>注册时间：</span>{{ authState.user.date_joined?.slice(0, 19).replace('T', ' ') }}</p>
          </div>
        </div>
      </div>

      <!-- 权限说明 -->
      <div class="panel">
        <h3>角色权限</h3>
        <div class="role-row">
          <span class="role-dot admin"></span>
          <div><b>管理员</b><p>全部权限：用户管理、检测、报告、数据集、系统配置</p></div>
        </div>
        <div class="role-row">
          <span class="role-dot user"></span>
          <div><b>普通用户</b><p>上传图片检测、查看报告与缺陷、评价报告、管理数据集</p></div>
        </div>
      </div>
    </div>

    <!-- 报告管理（管理员可见） -->
    <div v-if="isAdmin" class="panel report-admin">
      <h3>报告管理（全部用户报告）</h3>
      <div class="filter-bar">
        <el-date-picker v-model="startDate" type="date" placeholder="开始日期" value-format="YYYY-MM-DD" style="width: 150px" />
        <span class="filter-sep">至</span>
        <el-date-picker v-model="endDate" type="date" placeholder="结束日期" value-format="YYYY-MM-DD" style="width: 150px" />
        <el-button type="primary" @click="searchReports"><i class="bi bi-search"></i> 查询</el-button>
        <el-button @click="clearReportFilter">重置</el-button>
      </div>
      <el-table v-loading="reportLoading" :data="reports" size="small">
        <el-table-column label="编号" width="70">
          <template #default="{ row }"><span class="mono id">#{{ String(row.id).padStart(4, '0') }}</span></template>
        </el-table-column>
        <el-table-column prop="report_name" label="报告名称" min-width="170" show-overflow-tooltip />
        <el-table-column prop="created_by_name" label="提交用户" width="110" />
        <el-table-column label="缺陷数" width="80">
          <template #default="{ row }"><span class="mono">{{ row.total_defects }}</span></template>
        </el-table-column>
        <el-table-column label="时间" width="160">
          <template #default="{ row }"><span class="mono time">{{ row.created_at?.slice(0, 19).replace('T', ' ') }}</span></template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="router.push(`/reports/${row.id}`)">查看</el-button>
            <el-button link type="warning" size="small" @click="editReport(row)">修改</el-button>
            <el-button link type="danger" size="small" @click="removeReport(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pager">
        <el-pagination background layout="prev, pager, next, total" :total="reportTotal" :page-size="10" :current-page="reportPage" @current-change="onReportPage" />
      </div>
    </div>

    <!-- 操作日志（管理员可见） -->
    <div v-if="authState.user?.role === 'admin'" class="panel logs">
      <h3>最近操作日志</h3>
      <el-table :data="logs" size="small">
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="operation" label="操作" width="90">
          <template #default="{ row }">
            <el-tag :type="row.operation === 'DELETE' ? 'danger' : 'primary'" effect="dark" size="small">
              {{ row.operation }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP" width="140">
          <template #default="{ row }"><span class="mono">{{ row.ip_address || '—' }}</span></template>
        </el-table-column>
        <el-table-column label="时间" width="160">
          <template #default="{ row }"><span class="mono time">{{ row.created_at?.slice(0, 19).replace('T', ' ') }}</span></template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.page-wrap {
  max-width: 1440px;
  margin: 0 auto;
  padding: 24px;
  animation: fadeIn 0.4s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-head h2 {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.page-head p {
  font-size: 13px;
  color: var(--text-3);
  margin-top: 6px;
  margin-bottom: 18px;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-bottom: 18px;
}

.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 18px 20px;
  backdrop-filter: blur(14px);
  box-shadow: var(--shadow-card);
}

.panel h3 {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 14px;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.user-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4da3ff, #1e90ff);
  color: #fff;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-info .user-name {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.user-info .user-role {
  font-size: 12px;
  color: var(--blue-light);
}

.user-detail {
  flex-basis: 100%;
  margin-top: 12px;
  border-top: 1px solid var(--border);
  padding-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: var(--text-2);
}

.user-detail span {
  color: var(--text-3);
}

.role-row {
  display: flex;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}

.role-row:last-child {
  border-bottom: none;
}

.role-row b {
  color: #fff;
  font-size: 14px;
}

.role-row p {
  font-size: 12px;
  color: var(--text-3);
  margin-top: 3px;
}

.role-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 3px;
  flex-shrink: 0;
}

.role-dot.admin { background: #f0574a; }
.role-dot.user { background: #2fd6d6; }

.report-admin,
.logs {
  margin-top: 18px;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.filter-sep {
  color: var(--text-3);
  font-size: 13px;
}

.id {
  color: var(--blue-light);
  font-size: 12px;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}

.time {
  font-size: 12px;
  color: var(--text-3);
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
