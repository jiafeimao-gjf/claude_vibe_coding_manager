<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSettingsStore } from '../stores/settings'
import { getProject } from '../api'
import { Loader2, ArrowLeft, MessageSquare, Clock } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const settings = useSettingsStore()
const project = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await getProject(route.params.id)
    project.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

function formatDate(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString(settings.locale === 'en' ? 'en-US' : 'zh-CN')
}
</script>

<template>
  <div class="space-y-6">
    <button
      @click="router.push('/projects')"
      class="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
    >
      <ArrowLeft :size="16" /> {{ t('projectDetail.backTo') }}
    </button>

    <div v-if="loading" class="flex justify-center py-16">
      <Loader2 :size="32" class="animate-spin text-gray-400 dark:text-gray-500" />
    </div>

    <template v-else-if="project">
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ project.name }}</h1>
        <p class="text-sm text-gray-400 dark:text-gray-500 mt-1">{{ project.path }}</p>
        <div class="flex items-center gap-6 mt-4">
          <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
            <MessageSquare :size="16" class="text-gray-400 dark:text-gray-500" />
            {{ project.session_count }} {{ t('projectDetail.sessions') }}
          </div>
          <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
            <Clock :size="16" class="text-gray-400 dark:text-gray-500" />
            {{ formatDate(project.first_seen_at) }} — {{ formatDate(project.last_seen_at) }}
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
        <div class="px-5 py-3 border-b border-gray-100 dark:border-gray-700">
          <h2 class="font-semibold text-gray-900 dark:text-gray-100">{{ t('projectDetail.sessions') }}</h2>
        </div>
        <div v-if="project.sessions.length === 0" class="text-center py-12 text-gray-400 dark:text-gray-500 text-sm">
          {{ t('projectDetail.noSessions') }}
        </div>
        <div v-else class="divide-y divide-gray-100 dark:divide-gray-700">
          <div
            v-for="s in project.sessions"
            :key="s.id"
            @click="router.push(`/sessions/${s.id}`)"
            class="flex items-center justify-between px-5 py-3.5 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
          >
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                {{ t('projectDetail.sessionId') }} {{ s.id }}
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
    </template>

    <div v-else class="text-center py-16 text-gray-500 dark:text-gray-400">
      {{ t('projectDetail.notFound') }}
    </div>
  </div>
</template>
