import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const STORAGE_KEY = 'claude-history-settings'

function loadInitial() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}
  } catch {
    return {}
  }
}

export const useSettingsStore = defineStore('settings', () => {
  const initial = loadInitial()
  const theme = ref(initial.theme || 'light')     // 'light' | 'dark'
  const locale = ref(initial.locale || 'zh-CN')   // 'zh-CN' | 'en'

  function persist() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      theme: theme.value,
      locale: locale.value,
    }))
  }

  function toggleTheme() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }
  function toggleLocale() {
    locale.value = locale.value === 'zh-CN' ? 'en' : 'zh-CN'
  }
  function setTheme(v) {
    theme.value = v
  }
  function setLocale(v) {
    locale.value = v
  }

  watch([theme, locale], persist, { deep: true })

  return { theme, locale, toggleTheme, toggleLocale, setTheme, setLocale }
})
