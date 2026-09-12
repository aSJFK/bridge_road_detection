<script setup lang="ts">
const version = 'v1.0.0'
</script>

<template>
  <footer class="footer">
    <div class="footer-inner">
      <p>© 2026 桥路缺陷检测系统 | 基于深度学习的智能检测与分析平台</p>
      <span class="version mono">{{ version }}</span>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: linear-gradient(180deg, #0a0d14 0%, #000000 100%);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.footer-inner {
  max-width: 1440px;
  margin: 0 auto;
  padding: 22px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.footer p {
  font-size: 13px;
  color: #8d9ab0;
}

.version {
  font-size: 12px;
  color: #5c6b80;
  border: 1px solid rgba(92, 107, 128, 0.4);
  padding: 3px 10px;
  border-radius: 20px;
  white-space: nowrap;
}

@media (max-width: 600px) {
  .footer-inner {
    flex-direction: column;
    text-align: center;
  }
}
</style>
