<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { searchMessages } from '../api'
import { Search as SearchIcon, Loader2, MessageSquare } from 'lucide-vue-next'

const router = useRouter()
const { t } = useI18n()
const query = ref('')
const results = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)
const searched = ref(false)

async function doSearch() {
  if (!query.value.trim()) return
  loading.value = true
  searched.value = true
  try {
    const res = await searchMessages(query.value, page.value, pageSize)
    results.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function highlight(text, term) {
  if (!term || !text) return text
  const regex = new RegExp(`(${term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
  return text.replace(regex, '<mark class="bg-yellow-200 dark:bg-yellow-700/50 dark:text-yellow-100 rounded px-0.5">$1</mark>')
}

let debounceTimer = null
watch(query, () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    page.value = 1
    doSearch()
  }, 400)
})
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
      {{ t('search.title') }}
    </h1>

    <div class="relative">
      <SearchIcon :size="18" class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500" />
      <input
        v-model="query"
        type="text"
        :placeholder="t('search.placeholder')"
        class="w-full pl-11 pr-4 py-3 text-sm border border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        @keyup.enter="doSearch"
      />
    </div>

    <div v-if="loading" class="flex justify-center py-12">
      <Loader2 :size="32" class="animate-spin text-gray-400 dark:text-gray-500" />
    </div>

    <div v-else-if="searched && results.length === 0" class="text-center py-16">
      <MessageSquare :size="48" class="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
      <p class="text-gray-500 dark:text-gray-400">
        {{ t('search.noResults', { q: query }) }}
      </p>
    </div>

    <div v-else-if="results.length > 0" class="space-y-3">
      <p class="text-sm text-gray-500 dark:text-gray-400">
        {{ t('search.resultsCount', { count: total }) }}
      </p>
      <div
        v-for="msg in results"
        :key="msg.id"
        @click="router.push(`/sessions/${msg.session_id}`)"
        class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 hover:border-indigo-200 dark:hover:border-indigo-700 hover:shadow-sm cursor-pointer transition-all"
      >
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs text-gray-400 dark:text-gray-500">{{ msg.timestamp }}</span>
          <span class="text-xs text-indigo-500 dark:text-indigo-400 font-medium">
            {{ t('search.sessionLink', { id: msg.session_id }) }}
          </span>
        </div>
        <div
          class="text-sm text-gray-800 dark:text-gray-100 line-clamp-3"
          v-html="highlight(msg.display_text?.slice(0, 500) || '', query)"
        />
      </div>

      <div v-if="total > pageSize" class="flex items-center justify-center gap-2 pt-4">
        <button
          :disabled="page <= 1"
          @click="page--; doSearch()"
          class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
        >
          {{ t('common.prev') }}
        </button>
        <span class="text-sm text-gray-500 dark:text-gray-400">
          {{ t('common.page', { page, total: Math.ceil(total / pageSize) }) }}
        </span>
        <button
          :disabled="page >= Math.ceil(total / pageSize)"
          @click="page++; doSearch()"
          class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-30 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200"
        >
          {{ t('common.next') }}
        </button>
      </div>
    </div>
  </div>
</template>
