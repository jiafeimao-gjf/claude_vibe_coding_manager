import { watch } from 'vue'
import { useSettingsStore } from '../stores/settings'

/**
 * Applies the dark class to <html> based on the current settings.theme.
 * Call once at app startup; reacts automatically to theme changes.
 */
export function useDarkMode() {
  const settings = useSettingsStore()

  function apply() {
    const isDark = settings.theme === 'dark'
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', isDark)
    }
  }

  watch(() => settings.theme, apply, { immediate: true })
}
