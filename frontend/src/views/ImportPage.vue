<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '../stores/app'
import { useSettingsStore } from '../stores/settings'
import { importFull, importIncremental, importStatus, importLogs } from '../api'
import { Upload, RefreshCw, Loader2, CheckCircle, XCircle, Clock } from 'lucide-vue-next'

const store = useAppStore()
const settings = useSettingsStore()
const { t } = useI18n()
const status = ref(null)
const logs = ref([])
const importing = ref(false)
const importMessage = ref('')
const importError = ref('')

async function refreshStatus() {
  try {
    const [s, l] = await Promise.all([importStatus(), importLogs(0, 10)])
    status.value = s.data
    logs.value = l.data
  } catch (e) {
    // ignore
  }
}

async function doFullImport() {
  importing.value = true
  importMessage.value = ''
  importError.value = ''
  try {
    const res = await importFull()
    importMessage.value = res.data.message
    await refreshStatus()
    await store.fetchStats()
  } catch (e) {
    importError.value = e.response?.data?.detail || e.message || 'Import failed'
  } finally {
    importing.value = false
  }
}

async function doIncrementalImport() {
  importing.value = true
  importMessage.value = ''
  importError.value = ''
  try {
    const res = await importIncremental()
    importMessage.value = res.data.message
    await refreshStatus()
    await store.fetchStats()
  } catch (e) {
    importError.value = e.response?.data?.detail || e.message || 'Import failed'
  } finally {
    importing.value = false
  }
}

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString(settings.locale === 'en' ? 'en-US' : 'zh-CN')
}

onMounted(refreshStatus)
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
      {{ t('import.title') }}
    </h1>

    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
      <h2 class="font-semibold text-gray-900 dark:text-gray-100 mb-4">
        {{ t('import.status') }}
      </h2>
      <div v-if="status" class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div>
          <p class="text-xs text-gray-400 dark:text-gray-500">{{ t('import.lastImport') }}</p>
          <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatDate(status.finished_at) }}</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 dark:text-gray-500">{{ t('import.mode') }}</p>
          <p class="text-sm font-medium text-gray-900 dark:text-gray-100 capitalize">{{ status.mode }}</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 dark:text-gray-500">{{ t('import.statusLabel') }}</p>
          <span
            class="inline-flex items-center gap-1 text-sm font-medium px-2 py-0.5 rounded-full"
            :class="status.status === 'completed'
              ? 'text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-900/30'
              : status.status === 'failed'
              ? 'text-red-700 dark:text-red-400 bg-red-50 dark:bg-red-900/30'
              : 'text-yellow-700 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/30'"
          >
            <CheckCircle v-if="status.status === 'completed'" :size="14" />
            <XCircle v-else-if="status.status === 'failed'" :size="14" />
            <Clock v-else :size="14" />
            {{ t(`status.${status.status}`) }}
          </span>
        </div>
        <div>
          <p class="text-xs text-gray-400 dark:text-gray-500">{{ t('import.results') }}</p>
          <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
            {{ t('import.summary', {
              messages: status.total_messages,
              sessions: status.total_sessions,
              projects: status.total_projects
            }) }}
          </p>
        </div>
      </div>
      <div v-else class="text-sm text-gray-400 dark:text-gray-500">
        {{ t('import.noImport') }}
      </div>

      <div class="flex items-center gap-3 mt-5 pt-5 border-t border-gray-100 dark:border-gray-700">
        <button
          @click="doFullImport"
          :disabled="importing"
          class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-lg transition-colors"
        >
          <Loader2 v-if="importing" :size="16" class="animate-spin" />
          <Upload v-else :size="16" />
          {{ t('import.fullImport') }}
        </button>
        <button
          @click="doIncrementalImport"
          :disabled="importing"
          class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 disabled:opacity-50 rounded-lg transition-colors"
        >
          <RefreshCw :size="16" />
          {{ t('import.incremental') }}
        </button>
      </div>
      <p v-if="importMessage" class="mt-3 text-sm text-green-600 dark:text-green-400">{{ importMessage }}</p>
      <p v-if="importError" class="mt-3 text-sm text-red-600 dark:text-red-400">{{ importError }}</p>
    </div>

    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
      <div class="px-5 py-3 border-b border-gray-100 dark:border-gray-700">
        <h2 class="font-semibold text-gray-900 dark:text-gray-100">{{ t('import.logs') }}</h2>
      </div>
      <div v-if="logs.length === 0" class="text-center py-8 text-gray-400 dark:text-gray-500 text-sm">
        {{ t('import.noLogs') }}
      </div>
      <div v-else class="divide-y divide-gray-100 dark:divide-gray-700">
        <div
          v-for="log in logs"
          :key="log.id"
          class="px-5 py-3 flex items-center justify-between"
        >
          <div>
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100 capitalize">{{ log.mode }}</span>
              <span
                class="text-xs px-1.5 py-0.5 rounded-full"
                :class="log.status === 'completed'
                  ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                  : log.status === 'failed'
                  ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400'
                  : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'"
              >
                {{ t(`status.${log.status}`) }}
              </span>
            </div>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
              {{ t('import.summary', {
                messages: log.total_messages,
                sessions: log.total_sessions,
                projects: log.total_projects
              }) }}
            </p>
          </div>
          <span class="text-xs text-gray-400 dark:text-gray-500">{{ formatDate(log.finished_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
