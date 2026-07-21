/**
 * Dark mode theme utility
 * Usage: import { useDarkMode } from '../../utils/theme'
 * const { isDark, toggleDark, initDark } = useDarkMode()
 */

import { ref } from 'vue'

const isDark = ref(false)

export function useDarkMode() {
  function initDark() {
    isDark.value = !!uni.getStorageSync('dark_mode')
    applyTheme()
  }

  function toggleDark(val) {
    isDark.value = val
    uni.setStorageSync('dark_mode', val)
    applyTheme()
  }

  function applyTheme() {
    // CSS variables are applied via class on page root
    // Each page's .page element gets dark-mode class
  }

  return { isDark, toggleDark, initDark }
}

// Dark mode color constants for inline styles
export const darkColors = {
  bg: '#1a1a1a',
  cardBg: '#2c2c2e',
  textPrimary: '#f5f5f7',
  textSecondary: '#98989d',
  textTertiary: '#636366',
  border: '#38383a',
  headerBg: '#1a1a1a',
  sheetBg: '#2c2c2e',
  inputBg: '#38383a',
}
