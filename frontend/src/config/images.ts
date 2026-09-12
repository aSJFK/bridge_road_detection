/**
 * 图片路径统一管理
 * ----------------------------------------
 * 使用方式：
 *   1. 将你的真实图片放入 frontend/public/images/ 目录
 *   2. 把下面对应项的值改成图片路径
 *   3. 保存后刷新页面即可生效
 *
 * 建议尺寸：
 *   heroBg      整页背景长图（铺满整个首页并随滚动），建议 1920 宽、高度与整页内容匹配
 *   hudCrack    桥梁混凝土裂缝示例图（图片自带标注框），建议 800x600
 *   hudSpalling 混凝土剥落示例图（图片自带标注框），建议 800x600
 *   hudPothole  道路坑洞示例图（图片自带标注框），建议 800x600
 */

export const IMAGES = {
  heroBg: '/images/hero-bg.jpg',
  hudCrack: '/images/detect-crack.jpg',
  hudSpalling: '/images/detect-spalling.jpg',
  hudPothole: '/images/detect-pothole.jpg',
}
