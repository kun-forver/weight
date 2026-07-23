<script>
import { useAuthStore } from './stores/auth'

export default {
  onLaunch() {
    // Check auth on launch
    const token = uni.getStorageSync('access_token')
    if (!token) {
      uni.reLaunch({ url: '/pages/login/index' })
    }
    // Apply dark mode if saved
    const darkMode = uni.getStorageSync('dark_mode')
    if (darkMode) {
      this.applyDarkMode(true)
    }
  },
  onShow() {},
  onHide() {},
  methods: {
    applyDarkMode(isDark) {
      // Store for pages to read
      uni.setStorageSync('dark_mode', isDark)
    }
  }
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

/* CSS Variables - Light Mode */
page {
  --primary: #007aff;
  --green: #34c759;
  --orange: #ff9500;
  --red: #ff3b30;
  --bg-color: #f5f5f7;
  --card-bg: #ffffff;
  --text-primary: #1d1d1f;
  --text-secondary: #86868b;
  --text-tertiary: #aeaeb2;
  --border-color: #f0f0f2;
  --header-bg: #ffffff;
  --sheet-bg: #ffffff;
  --input-bg: #f5f5f7;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
}

/* Dark Mode overrides via class on page root */
page.dark-mode,
.dark-mode {
  --bg-color: #1a1a1a;
  --card-bg: #2c2c2e;
  --text-primary: #f5f5f7;
  --text-secondary: #98989d;
  --text-tertiary: #636366;
  --border-color: #38383a;
  --header-bg: #1a1a1a;
  --sheet-bg: #2c2c2e;
  --input-bg: #38383a;
}

/* Shared utility classes */
.page {
  min-height: 100vh;
  background: var(--bg-color);
  padding-bottom: 80px;
}

.card {
  background: var(--card-bg);
  border-radius: 16px;
  margin: 0 16px 8px;
  overflow: hidden;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin: 16px 16px 8px;
  color: var(--text-primary);
}

.btn-primary {
  width: 100%;
  height: 50px;
  background: var(--primary);
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
  color: var(--text-tertiary);
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
  background: var(--sheet-bg);
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
