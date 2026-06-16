import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN'
import en from './locales/en'

const STORAGE_KEY = 'claude-history-settings'

function getInitialLocale() {
  try {
    const s = JSON.parse(localStorage.getItem(STORAGE_KEY))
    if (s && s.locale) return s.locale
  } catch {
    // ignore
  }
  return 'zh-CN'
}

export const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: getInitialLocale(),
  fallbackLocale: 'en',
  messages: {
    'zh-CN': zhCN,
    en,
  },
})

export const availableLocales = [
  { code: 'zh-CN', label: '中文' },
  { code: 'en', label: 'EN' },
]
