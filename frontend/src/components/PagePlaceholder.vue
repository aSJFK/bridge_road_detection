<script setup lang="ts">
import { useRouter } from 'vue-router'

const props = defineProps<{
  title: string
  desc: string
  icon: string
  features: string[]
}>()

const router = useRouter()
</script>

<template>
  <div class="ph-wrap">
    <section class="ph-hero">
      <div class="ph-inner">
        <div class="ph-icon"><i :class="`bi ${props.icon}`"></i></div>
        <h1>{{ props.title }}</h1>
        <p>{{ props.desc }}</p>
        <el-button class="ph-back" @click="router.push('/')">
          <i class="bi bi-arrow-left"></i>
          <span>返回首页</span>
        </el-button>
      </div>
    </section>

    <section class="ph-body">
      <div class="ph-grid">
        <div v-for="f in props.features" :key="f" class="ph-card">
          <i class="bi bi-patch-check ph-card-icon"></i>
          <p>{{ f }}</p>
        </div>
      </div>
      <div class="ph-note">
        <i class="bi bi-info-circle"></i>
        本模块正在开发中，后续将接入完整业务功能
      </div>
    </section>
  </div>
</template>

<style scoped>
.ph-wrap {
  min-height: 70vh;
}

.ph-hero {
  background: linear-gradient(180deg, #0a0d14 0%, #000000 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding: 64px 24px;
}

.ph-inner {
  max-width: 760px;
  margin: 0 auto;
  text-align: center;
}

.ph-icon {
  width: 84px;
  height: 84px;
  margin: 0 auto 20px;
  border-radius: 22px;
  background: rgba(30, 144, 255, 0.16);
  border: 1px solid rgba(30, 144, 255, 0.5);
  color: #6fb3ff;
  font-size: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 26px rgba(30, 144, 255, 0.25);
}

.ph-inner h1 {
  font-size: 30px;
  font-weight: 800;
  color: #fff;
}

.ph-inner p {
  font-size: 15px;
  color: #a9c4e4;
  margin-top: 10px;
  line-height: 1.7;
}

.ph-back {
  margin-top: 26px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #2f9cff, #1e90ff);
  border: none;
  color: #fff;
  font-weight: 600;
  border-radius: 10px;
  padding: 11px 24px;
  transition: all 0.25s ease;
}

.ph-back:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(30, 144, 255, 0.4);
}

.ph-body {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 24px 60px;
}

.ph-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.ph-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 22px;
  text-align: center;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: var(--shadow-card);
  transition: all 0.25s ease;
}

.ph-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-card-hover);
  border-color: rgba(30, 144, 255, 0.4);
  background: rgba(255, 255, 255, 0.085);
}

.ph-card-icon {
  font-size: 24px;
  color: var(--blue-light);
}

.ph-card p {
  font-size: 13.5px;
  color: var(--text-2);
  margin-top: 12px;
}

.ph-note {
  margin-top: 32px;
  text-align: center;
  font-size: 13px;
  color: var(--text-3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.ph-note i {
  color: var(--blue-light);
}
</style>
