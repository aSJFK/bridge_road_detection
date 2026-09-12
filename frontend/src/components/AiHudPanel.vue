<script setup lang="ts">
import { ref } from 'vue'
import { IMAGES } from '@/config/images'

// AI 检测结果展示面板（HUD 风格）
// 3 张示例图：直接展示真实图片（图片自带标注框，无需额外叠加检测框）
// 未配置图片时自动回退内置 SVG 场景，不会出现破图

const mainErr = ref(false)
const thumb1Err = ref(false)
const thumb2Err = ref(false)

const mainUrl = IMAGES.hudCrack
const thumb1Url = IMAGES.hudSpalling
const thumb2Url = IMAGES.hudPothole
</script>

<template>
  <div class="hud">
    <!-- HUD 头部 -->
    <div class="hud-head">
      <div class="hud-title">
        <span class="hud-pulse"></span>
        <span class="hud-name">AI 智能识别</span>
      </div>
      <span class="hud-model mono">YOLOv8 ENGINE</span>
    </div>

    <!-- 主检测图：桥梁混凝土裂缝 -->
    <div class="hud-main">
      <!-- 真实图片（优先） -->
      <img
        v-if="mainUrl && !mainErr"
        :src="mainUrl"
        class="hud-img"
        alt="桥梁混凝土裂缝"
        @error="mainErr = true"
      />
      <!-- 内置 SVG 场景（回退） -->
      <svg v-show="!mainUrl || mainErr" class="hud-img" viewBox="0 0 400 240" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
        <defs>
          <filter id="grain" x="0" y="0" width="100%" height="100%">
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="5" result="n" />
            <feColorMatrix in="n" type="matrix" values="0 0 0 0 0.62  0 0 0 0 0.64  0 0 0 0 0.68  0 0 0 0.25 0" />
            <feComposite in="SourceGraphic" operator="over" />
          </filter>
        </defs>
        <rect width="400" height="240" fill="#9aa0a8" />
        <rect width="400" height="240" filter="url(#grain)" opacity="0.7" />
        <rect width="400" height="240" fill="url(#shade)" opacity="0.4" />
        <defs>
          <linearGradient id="shade" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#000" stop-opacity="0.05" />
            <stop offset="1" stop-color="#000" stop-opacity="0.45" />
          </linearGradient>
        </defs>
        <path
          d="M150 30 C170 70 130 90 150 130 C165 160 140 185 155 215"
          fill="none"
          stroke="#2c3036"
          stroke-width="4"
          stroke-linecap="round"
        />
        <path
          d="M150 60 C185 75 200 60 225 75"
          fill="none"
          stroke="#33373d"
          stroke-width="2.5"
          stroke-linecap="round"
        />
        <path
          d="M150 150 C120 165 110 150 95 170"
          fill="none"
          stroke="#33373d"
          stroke-width="2"
          stroke-linecap="round"
        />
      </svg>

    </div>

    <!-- 小图 -->
    <div class="hud-thumbs">
      <!-- 混凝土剥落 -->
      <div class="hud-thumb">
        <img
          v-if="thumb1Url && !thumb1Err"
          :src="thumb1Url"
          class="hud-img"
          alt="混凝土剥落"
          @error="thumb1Err = true"
        />
        <svg v-show="!thumb1Url || thumb1Err" class="hud-img" viewBox="0 0 190 110" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
          <rect width="190" height="110" fill="#8d949c" />
          <rect width="190" height="110" filter="url(#grain)" opacity="0.6" />
          <path d="M60 30 C85 22 105 28 118 42 C128 55 122 68 110 74 C95 82 72 80 58 68 C46 58 44 42 60 30 Z" fill="#6a7078" />
          <path d="M66 34 C78 30 92 33 100 40" fill="none" stroke="#545a61" stroke-width="2" />
          <path d="M64 62 C76 72 90 70 100 66" fill="none" stroke="#545a61" stroke-width="1.6" />
        </svg>
      </div>

      <!-- 道路坑洞 -->
      <div class="hud-thumb">
        <img
          v-if="thumb2Url && !thumb2Err"
          :src="thumb2Url"
          class="hud-img"
          alt="道路坑洞"
          @error="thumb2Err = true"
        />
        <svg v-show="!thumb2Url || thumb2Err" class="hud-img" viewBox="0 0 190 110" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
          <rect width="190" height="110" fill="#3a3d42" />
          <rect width="190" height="110" filter="url(#grain)" opacity="0.35" />
          <path d="M0 28 C40 24 90 30 190 26" stroke="#464a50" stroke-width="2" fill="none" />
          <path d="M0 84 C60 88 120 82 190 86" stroke="#464a50" stroke-width="2" fill="none" />
          <ellipse cx="100" cy="55" rx="34" ry="24" fill="#1d1f22" />
          <ellipse cx="100" cy="53" rx="28" ry="19" fill="#131416" />
          <path d="M72 45 C82 38 118 38 128 45" stroke="#575b61" stroke-width="2" fill="none" />
        </svg>
      </div>
    </div>

    <!-- HUD 底部状态 -->
    <div class="hud-foot">
      <span class="hud-status mono"><i class="ok"></i>RECOGNITION ACTIVE</span>
      <span class="hud-status mono">FPS 30 · GPU 0</span>
    </div>
  </div>
</template>

<style scoped>
.hud {
  position: relative;
  background: linear-gradient(180deg, rgba(13, 34, 66, 0.85), rgba(7, 20, 40, 0.9));
  border: 1px solid rgba(30, 144, 255, 0.55);
  border-radius: 16px;
  padding: 16px;
  box-shadow:
    0 0 0 1px rgba(30, 144, 255, 0.12),
    0 0 26px rgba(30, 144, 255, 0.18);
}

/* 头部 */
.hud-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.hud-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #e6f1ff;
}

.hud-pulse {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--cyan);
  animation: pulseGlow 2s infinite;
}

.hud-model {
  font-size: 10px;
  letter-spacing: 0.12em;
  color: #ffffff;
  border: 1px solid rgba(95, 142, 194, 0.4);
  padding: 3px 8px;
  border-radius: 6px;
}

/* 主图 */
.hud-main {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(30, 144, 255, 0.3);
  aspect-ratio: 5 / 3;
  background: #0d2242;
}

.hud-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 小图 */
.hud-thumbs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 12px;
}

.hud-thumb {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(30, 144, 255, 0.25);
  aspect-ratio: 19 / 11;
  background: #0d2242;
}

/* 底部 */
.hud-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
}

.hud-status {
  font-size: 9px;
  letter-spacing: 0.1em;
  color: #ffffff;
}

.hud-status .ok {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--success);
  margin-right: 5px;
  animation: pulseGlow 2s infinite;
}

@media (max-width: 600px) {
  .hud {
    padding: 12px;
  }
}
</style>
