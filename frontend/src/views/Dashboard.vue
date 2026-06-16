<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAppStore } from '../stores/app'
import { useSettingsStore } from '../stores/settings'
import { getSessions } from '../api'
import {
  MessageSquare,
  FolderOpen,
  Clock,
  TrendingUp,
  Loader2,
} from 'lucide-vue-next'

const router = useRouter()
const store = useAppStore()
const settings = useSettingsStore()
const { t } = useI18n()
const recentSessions = ref([])
const loadingSessions = ref(false)

const dateLocale = () => settings.locale === 'en' ? 'en-US' : 'zh-CN'

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString(dateLocale())
}

onMounted(async () => {
  store.fetchStats()
  loadingSessions.value = true
  try {
    const res = await getSessions(1, 5)
    recentSessions.value = res.data.items
  } catch (e) {
    // ignore
  } finally {
    loadingSessions.value = false
  }
})

function goSession(id) {
  router.push(`/sessions/${id}`)
}
function goProjects() {
  router.push('/projects')
}
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
      {{ t('dashboard.title') }}
    </h1>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 flex items-center gap-4">
        <div class="w-10 h-10 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
          <FolderOpen :size="20" class="text-indigo-600 dark:text-indigo-400" />
        </div>
        <div>
          <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {{ store.stats?.total_projects ?? '-' }}
          </p>
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('dashboard.projects') }}</p>
        </div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 flex items-center gap-4">
        <div class="w-10 h-10 rounded-lg bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
          <MessageSquare :size="20" class="text-emerald-600 dark:text-emerald-400" />
        </div>
        <div>
          <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {{ store.stats?.total_sessions ?? '-' }}
          </p>
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('dashboard.sessions') }}</p>
        </div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 flex items-center gap-4">
        <div class="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
          <TrendingUp :size="20" class="text-amber-600 dark:text-amber-400" />
        </div>
        <div>
          <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {{ store.stats?.total_messages ?? '-' }}
          </p>
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('dashboard.messages') }}</p>
        </div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 flex items-center gap-4">
        <div class="w-10 h-10 rounded-lg bg-rose-100 dark:bg-rose-900/30 flex items-center justify-center">
          <Clock :size="20" class="text-rose-600 dark:text-rose-400" />
        </div>
        <div>
          <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
            {{ store.stats?.date_range_start
              ? formatDate(store.stats.date_range_start).split(' ')[0]
              : '-' }}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400">{{ t('dashboard.dateRange') }}</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Recent Sessions -->
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-semibold text-gray-900 dark:text-gray-100">
            {{ t('dashboard.recentSessions') }}
          </h2>
          <button
            @click="goProjects"
            class="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300"
          >
            {{ t('dashboard.viewAll') }}
          </button>
        </div>
        <div v-if="loadingSessions" class="flex justify-center py-8">
          <Loader2 :size="24" class="animate-spin text-gray-400 dark:text-gray-500" />
        </div>
        <div v-else-if="recentSessions.length === 0" class="text-center py-8 text-gray-400 dark:text-gray-500 text-sm">
          {{ t('dashboard.noSessions') }}
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="s in recentSessions"
            :key="s.id"
            @click="goSession(s.id)"
            class="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors border border-transparent hover:border-gray-200 dark:hover:border-gray-600"
          >
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                {{ s.cwd || (t('common.session') + ' ' + s.id) }}
              </p>
              <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                {{ s.message_count }} {{ t('common.messages') }} · {{ formatDate(s.started_at) }}
              </p>
            </div>
            <span
              class="text-xs px-2 py-0.5 rounded-full shrink-0 ml-3"
              :class="s.status === 'completed'
                ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'"
            >
              {{ s.status || t('status.unknown') }}
            </span>
          </div>
        </div>
      </div>

      <!-- Timeline Chart -->
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
        <h2 class="font-semibold text-gray-900 dark:text-gray-100 mb-4">
          {{ t('dashboard.timeline') }}
        </h2>
        <div v-if="store.timeline.length === 0" class="text-center py-8 text-gray-400 dark:text-gray-500 text-sm">
          {{ t('dashboard.noTimeline') }}
        </div>
        <div v-else class="flex items-end gap-1 h-40">
          <div
            v-for="(point, i) in store.timeline.slice(-60)"
            :key="i"
            class="flex-1 bg-indigo-400 dark:bg-indigo-500 hover:bg-indigo-500 dark:hover:bg-indigo-400 rounded-t transition-colors"
            :style="{ height: Math.max(4, (point.count / Math.max(...store.timeline.map(p => p.count))) * 100) + '%' }"
            :title="t('dashboard.timelinePoint', { date: point.date, count: point.count })"
          />
        </div>
        <div class="flex justify-between mt-2 text-xs text-gray-400 dark:text-gray-500">
          <span>{{ store.timeline[0]?.date || '' }}</span>
          <span>{{ store.timeline[store.timeline.length - 1]?.date || '' }}</span>
        </div>
      </div>
    </div>

    <!-- Top Projects -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5">
      <h2 class="font-semibold text-gray-900 dark:text-gray-100 mb-4">
        {{ t('dashboard.topProjects') }}
      </h2>
      <div v-if="store.topProjects.length === 0" class="text-center py-8 text-gray-400 dark:text-gray-500 text-sm">
        {{ t('dashboard.noProjects') }}
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="(p, i) in store.topProjects"
          :key="p.id"
          class="flex items-center gap-3"
        >
          <span class="text-xs font-medium text-gray-400 dark:text-gray-500 w-5">{{ i + 1 }}</span>
          <div class="flex-1 min-w-0">
            <p
              class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate cursor-pointer hover:text-indigo-600 dark:hover:text-indigo-400"
              @click="router.push(`/projects/${p.id}`)"
            >
              {{ p.name }}
            </p>
            <p class="text-xs text-gray-400 dark:text-gray-500 truncate">{{ p.path }}</p>
          </div>
          <span class="text-sm font-medium text-gray-600 dark:text-gray-300 shrink-0">
            {{ p.session_count }} {{ t('dashboard.sessionsUnit') }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
