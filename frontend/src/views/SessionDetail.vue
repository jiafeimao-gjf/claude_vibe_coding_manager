<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSettingsStore } from '../stores/settings'
import { getSession } from '../api'
import { Loader2, ArrowLeft, MessageSquare, Clock, Terminal, Copy, X } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const settings = useSettingsStore()
const session = ref(null)
const loading = ref(true)
const activeTab = ref('messages')
const showContinueModal = ref(false)
const commandCopied = ref(false)

onMounted(async () => {
  try {
    const res = await getSession(route.params.id)
    session.value = res.data
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
function formatTime(d) {
  if (!d) return '-'
  return new Date(d).toLocaleTimeString(settings.locale === 'en' ? 'en-US' : 'zh-CN')
}

const continueCommand = computed(() => {
  if (!session.value) return ''
  const cwd = session.value.cwd || '~'
  const sid = session.value.session_id
  return `cd "${cwd}" && claude --resume ${sid}`
})

async function copyCommand() {
  try {
    await navigator.clipboard.writeText(continueCommand.value)
    commandCopied.value = true
    setTimeout(() => { commandCopied.value = false }, 2000)
  } catch (e) {
    console.error('Failed to copy:', e)
  }
}
</script>

<template>
  <div class="space-y-6">
    <button
      @click="router.back()"
      class="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
    >
      <ArrowLeft :size="16" /> {{ t('common.back') }}
    </button>

    <div v-if="loading" class="flex justify-center py-16">
      <Loader2 :size="32" class="animate-spin text-gray-400 dark:text-gray-500" />
    </div>

    <template v-else-if="session">
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center gap-2 text-sm text-gray-400 dark:text-gray-500 mb-2">
          <Terminal :size="14" />
          <span>{{ session.kind || 'interactive' }} · {{ session.entrypoint || 'cli' }}</span>
          <span
            class="ml-auto text-xs px-2 py-0.5 rounded-full"
            :class="session.status === 'completed'
              ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
              : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'"
          >
            {{ session.status || t('status.unknown') }}
          </span>
        </div>
        <h1 class="text-xl font-bold text-gray-900 dark:text-gray-100">
          {{ t('sessionDetail.title') }}
        </h1>
        <div class="flex flex-wrap items-center gap-4 mt-3 text-sm text-gray-500 dark:text-gray-400">
          <div class="flex items-center gap-1.5">
            <Clock :size="14" />
            {{ formatDate(session.started_at) }}
          </div>
          <div class="flex items-center gap-1.5">
            <MessageSquare :size="14" />
            {{ session.message_count }} {{ t('common.messages') }}
          </div>
          <span>v{{ session.version }}</span>
          <span>{{ t('sessionDetail.pid') }} {{ session.pid }}</span>
        </div>
        <p class="text-xs text-gray-400 dark:text-gray-500 mt-2 truncate">
          {{ t('sessionDetail.cwd') }} {{ session.cwd }}
        </p>
        <div class="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700 flex items-center gap-3 flex-wrap">
          <button
            @click="showContinueModal = true"
            class="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 rounded-lg transition-colors"
          >
            <Terminal :size="14" />
            {{ t('sessionDetail.continueDev') }}
          </button>
          <span class="text-xs text-gray-400 dark:text-gray-500">→</span>
          <code class="text-xs text-gray-500 dark:text-gray-400 font-mono truncate">claude --resume {{ session.session_id.slice(0, 8) }}...</code>
        </div>
      </div>

      <!-- Tabs -->
      <div class="flex gap-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1 w-fit">
        <button
          @click="activeTab = 'messages'"
          class="px-4 py-1.5 text-sm rounded-md transition-colors text-gray-700 dark:text-gray-200"
          :class="activeTab === 'messages'
            ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow-sm font-medium'
            : 'hover:text-gray-900 dark:hover:text-white'"
        >
          {{ t('sessionDetail.messages') }} ({{ session.messages.length }})
        </button>
        <button
          @click="activeTab = 'events'"
          class="px-4 py-1.5 text-sm rounded-md transition-colors text-gray-700 dark:text-gray-200"
          :class="activeTab === 'events'
            ? 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 shadow-sm font-medium'
            : 'hover:text-gray-900 dark:hover:text-white'"
        >
          {{ t('sessionDetail.events') }} ({{ session.events.length }})
        </button>
      </div>

      <!-- Messages Tab -->
      <div v-if="activeTab === 'messages'" class="space-y-3">
        <div v-if="session.messages.length === 0" class="text-center py-12 text-gray-400 dark:text-gray-500">
          {{ t('sessionDetail.noMessages') }}
        </div>
        <div
          v-for="msg in session.messages"
          :key="msg.id"
          class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs text-gray-400 dark:text-gray-500">{{ formatTime(msg.timestamp) }}</span>
          </div>
          <div class="text-sm text-gray-800 dark:text-gray-100 whitespace-pre-wrap break-words font-mono">
            {{ msg.display_text }}
          </div>
          <div
            v-if="msg.pasted_contents && Object.keys(msg.pasted_contents).length > 0"
            class="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700"
          >
            <p class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">
              {{ t('sessionDetail.pastedContents') }}
            </p>
            <div
              v-for="(content, filename) in msg.pasted_contents"
              :key="filename"
              class="bg-gray-50 dark:bg-gray-700/50 rounded p-2 mt-1"
            >
              <p class="text-xs font-medium text-gray-600 dark:text-gray-300 mb-1">{{ filename }}</p>
              <pre class="text-xs text-gray-700 dark:text-gray-200 overflow-x-auto">{{ content }}</pre>
            </div>
          </div>
        </div>
      </div>

      <!-- Events Tab -->
      <div v-if="activeTab === 'events'" class="space-y-2">
        <div v-if="session.events.length === 0" class="text-center py-12 text-gray-400 dark:text-gray-500">
          {{ t('sessionDetail.noEvents') }}
        </div>
        <div
          v-for="evt in session.events"
          :key="evt.id"
          class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 px-4 py-3 grid grid-cols-6 gap-4 items-start"
        >
          <div class="col-span-1">
            <span class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">{{ evt.event_type }}</span>
          </div>
          <pre class="col-span-5 text-xs text-gray-600 dark:text-gray-300 overflow-x-auto">{{ JSON.stringify(evt.event_data, null, 2) }}</pre>
        </div>
      </div>
    </template>

    <div v-else class="text-center py-16 text-gray-500 dark:text-gray-400">
      {{ t('sessionDetail.notFound') }}
    </div>

    <Teleport to="body">
      <div
        v-if="showContinueModal"
        @click.self="showContinueModal = false"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      >
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 w-full max-w-xl mx-4 overflow-hidden">
          <div class="flex items-center justify-between px-5 py-3 border-b border-gray-100 dark:border-gray-700">
            <h3 class="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <Terminal :size="16" />
              {{ t('sessionDetail.continueDev') }}
            </h3>
            <button
              @click="showContinueModal = false"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
            >
              <X :size="18" />
            </button>
          </div>
          <div class="p-5 space-y-3">
            <p class="text-sm text-gray-600 dark:text-gray-300">
              {{ t('sessionDetail.commandHint') }}
            </p>
            <pre class="bg-gray-900 text-green-400 p-4 rounded-lg text-sm font-mono overflow-x-auto whitespace-pre-wrap break-all">{{ continueCommand }}</pre>
          </div>
          <div class="px-5 py-3 bg-gray-50 dark:bg-gray-700/30 flex items-center justify-end gap-2">
            <button
              @click="showContinueModal = false"
              class="px-3 py-1.5 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              {{ t('sessionDetail.close') }}
            </button>
            <button
              @click="copyCommand"
              class="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors"
            >
              <Copy :size="14" />
              {{ commandCopied ? t('sessionDetail.copied') : t('sessionDetail.copyCommand') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
