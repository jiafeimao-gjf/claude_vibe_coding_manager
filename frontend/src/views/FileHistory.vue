<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSettingsStore } from '../stores/settings'
import { getFileHistory } from '../api'
import { Loader2, FileText, Clock } from 'lucide-vue-next'

const { t } = useI18n()
const settings = useSettingsStore()
const entries = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)

async function fetchHistory() {
  loading.value = true
  try {
    const res = await getFileHistory(page.value, pageSize)
    entries.value = res.data.items
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

onMounted(fetchHistory)
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
      {{ t('fileHistory.title') }}
    </h1>

    <div v-if="loading" class="flex justify-center py-12">
      <Loader2 :size="32" class="animate-spin text-gray-400 dark:text-gray-500" />
    </div>

    <div v-else-if="entries.length === 0" class="text-center py-16">
      <FileText :size="48" class="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
      <p class="text-gray-500 dark:text-gray-400">{{ t('fileHistory.noFound') }}</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="entry in entries"
        :key="entry.file_history_uuid"
        class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5"
      >
        <div class="flex items-center justify-between mb-3">
          <div>
            <p class="text-sm font-medium text-gray-900 dark:text-gray-100 font-mono">
              {{ entry.file_path || t('fileHistory.unknownFile') }}
            </p>
            <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5 font-mono">
              {{ t('fileHistory.uuid') }}: {{ entry.file_history_uuid }}
            </p>
          </div>
          <span class="text-xs text-gray-400 dark:text-gray-500 flex items-center gap-1">
            <Clock :size="12" />
            {{ entry.versions.length }} {{ t('common.versions') }}
          </span>
        </div>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="v in entry.versions"
            :key="v.id"
            class="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 font-mono"
          >
            v{{ v.version }}
            <span class="text-gray-400 dark:text-gray-500 ml-1">{{ formatDate(v.created_at) }}</span>
          </span>
        </div>
      </div>
    </div>

    <div v-if="total > pageSize" class="flex items-center justify-center gap-2">
      <button
        :disabled="page <= 1"
        @click="page--; fetchHistory()"
        class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
      >
        {{ t('common.prev') }}
      </button>
      <span class="text-sm text-gray-500 dark:text-gray-400">
        {{ t('common.page', { page, total: Math.ceil(total / pageSize) }) }}
      </span>
      <button
        :disabled="page >= Math.ceil(total / pageSize)"
        @click="page++; fetchHistory()"
        class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
      >
        {{ t('common.next') }}
      </button>
    </div>
  </div>
</template>
