<script setup>
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSettingsStore } from '../stores/settings'
import {
  LayoutDashboard,
  FolderOpen,
  Search,
  Upload,
  History,
  Sun,
  Moon,
} from 'lucide-vue-next'

const route = useRoute()
const { t } = useI18n()
const settings = useSettingsStore()

const links = [
  { to: '/', labelKey: 'nav.dashboard', icon: LayoutDashboard },
  { to: '/projects', labelKey: 'nav.projects', icon: FolderOpen },
  { to: '/search', labelKey: 'nav.search', icon: Search },
  { to: '/import', labelKey: 'nav.import', icon: Upload },
  { to: '/file-history', labelKey: 'nav.fileHistory', icon: History },
]

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<template>
  <aside class="w-56 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col shrink-0 transition-colors">
    <div class="h-14 flex items-center px-4 border-b border-gray-200 dark:border-gray-700">
      <span class="font-semibold text-sm text-gray-800 dark:text-gray-100">
        {{ t('sidebar.appName') }}
      </span>
    </div>
    <nav class="flex-1 py-2">
      <router-link
        v-for="link in links"
        :key="link.to"
        :to="link.to"
        class="flex items-center gap-3 px-4 py-2.5 text-sm mx-2 rounded-lg transition-colors"
        :class="isActive(link.to)
          ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 font-medium'
          : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
      >
        <component :is="link.icon" :size="16" />
        {{ t(link.labelKey) }}
      </router-link>
    </nav>
    <div class="border-t border-gray-200 dark:border-gray-700 p-3 flex gap-2">
      <button
        @click="settings.toggleTheme"
        :title="t('sidebar.theme')"
        class="flex-1 flex items-center justify-center p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300 transition-colors"
      >
        <Sun v-if="settings.theme === 'dark'" :size="16" />
        <Moon v-else :size="16" />
      </button>
      <button
        @click="settings.toggleLocale"
        :title="t('sidebar.locale')"
        class="flex-1 flex items-center justify-center p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs font-medium transition-colors"
      >
        {{ settings.locale === 'zh-CN' ? 'EN' : '中' }}
      </button>
    </div>
  </aside>
</template>
