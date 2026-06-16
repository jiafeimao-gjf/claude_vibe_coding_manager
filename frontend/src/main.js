import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { watch } from 'vue'
import router from './router'
import App from './App.vue'
import { i18n } from './i18n'
import { useDarkMode } from './composables/useDarkMode'
import { useSettingsStore } from './stores/settings'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(i18n)

// Initialize dark mode (applies before mount, so no flash)
useDarkMode()

// Sync i18n locale with settings store
const settings = useSettingsStore()
watch(
  () => settings.locale,
  (newLocale) => {
    i18n.global.locale.value = newLocale
  },
  { immediate: true },
)

app.mount('#app')
