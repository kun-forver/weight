<script>
import { useAuthStore } from './stores/auth'

export default {
  onLaunch() {
    // Check auth on launch
    const token = uni.getStorageSync('access_token')
    if (!token) {
      uni.reLaunch({ url: '/pages/login/index' })
    }
  },
  onShow() {},
  onHide() {}
}
</script>

<style>
/* Global styles */
page {
  background-color: #f5f5f7;
  color: #1d1d1f;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
}

view, text, button, input, textarea, scroll-view {
  box-sizing: border-box;
}

/* CSS Variables */
page {
  --primary: #007aff;
  --green: #34c759;
  --orange: #ff9500;
  --red: #ff3b30;
  --bg-color: #f5f5f7;
  --text-primary: #1d1d1f;
  --text-secondary: #86868b;
  --border-color: #e5e5ea;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
}

/* Shared utility classes */
.page {
  min-height: 100vh;
  background: #f5f5f7;
  padding-bottom: 80px;
}

.card {
  background: #fff;
  border-radius: 16px;
  margin: 0 16px 8px;
  overflow: hidden;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 16px 8px;
  color: #1d1d1f;
}

.btn-primary {
  width: 100%;
  height: 50px;
  background: #007aff;
  color: #fff;
  border-radius: 14px;
  font-size: 17px;
  font-weight: 600;
  border: none;
  margin-top: 4px;
}

.loading-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #aeaeb2;
  font-size: 14px;
}

.bottom-sheet-backdrop {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  z-index: 200;
}

.bottom-sheet {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 20px 20px 0 0;
  padding: 20px;
  z-index: 201;
  max-height: 85vh;
  overflow-y: auto;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}
</style>
