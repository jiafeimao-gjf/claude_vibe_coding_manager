<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSettingsStore } from '../stores/settings'
import { getProjects } from '../api'
import { Search, Loader2, FolderOpen, ArrowRight } from 'lucide-vue-next'

const router = useRouter()
const { t } = useI18n()
const settings = useSettingsStore()
const projects = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const search = ref('')
const loading = ref(false)

async function fetchProjects() {
  loading.value = true
  try {
    const res = await getProjects(page.value, pageSize, search.value)
    projects.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString(settings.locale === 'en' ? 'en-US' : 'zh-CN')
}

let debounceTimer = null
watch(search, () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    fetchProjects()
  }, 300)
})

onMounted(fetchProjects)
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
        {{ t('projects.title') }}
      </h1>
      <div class="relative w-64">
        <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500" />
        <input
          v-model="search"
          type="text"
          :placeholder="t('projects.search')"
          class="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <Loader2 :size="32" class="animate-spin text-gray-400 dark:text-gray-500" />
    </div>

    <div v-else-if="projects.length === 0" class="text-center py-16">
      <FolderOpen :size="48" class="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
      <p class="text-gray-500 dark:text-gray-400">{{ t('projects.noFound') }}</p>
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="p in projects"
        :key="p.id"
        @click="router.push(`/projects/${p.id}`)"
        class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 hover:shadow-md hover:border-indigo-200 dark:hover:border-indigo-700 transition-all cursor-pointer group"
      >
        <div class="flex items-start justify-between">
          <div class="min-w-0 flex-1">
            <h3 class="font-semibold text-gray-900 dark:text-gray-100 truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
              {{ p.name }}
            </h3>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-1 truncate">{{ p.path }}</p>
          </div>
          <ArrowRight :size="16" class="text-gray-300 dark:text-gray-600 group-hover:text-indigo-500 dark:group-hover:text-indigo-400 transition-colors shrink-0 ml-2 mt-1" />
        </div>
        <div class="flex items-center gap-4 mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          <div>
            <p class="text-lg font-bold text-gray-900 dark:text-gray-100">{{ p.session_count }}</p>
            <p class="text-xs text-gray-400 dark:text-gray-500">{{ t('projects.sessionsUnit') }}</p>
          </div>
          <div class="text-xs text-gray-400 dark:text-gray-500">
            {{ t('projects.last') }}: {{ formatDate(p.last_seen_at) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="flex items-center justify-center gap-2">
      <button
        :disabled="page <= 1"
        @click="page--; fetchProjects()"
        class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
      >
        {{ t('common.prev') }}
      </button>
      <span class="text-sm text-gray-500 dark:text-gray-400">
        {{ t('common.page', { page, total: Math.ceil(total / pageSize) }) }}
      </span>
      <button
        :disabled="page >= Math.ceil(total / pageSize)"
        @click="page++; fetchProjects()"
        class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
      >
        {{ t('common.next') }}
      </button>
    </div>
  </div>
</template>
