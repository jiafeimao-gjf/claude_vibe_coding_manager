import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '../api'

export const useAppStore = defineStore('app', () => {
  const stats = ref(null)
  const timeline = ref([])
  const topProjects = ref([])
  const loading = ref(false)

  async function fetchStats() {
    loading.value = true
    try {
      const [s, t, tp] = await Promise.all([
        api.getStatsOverview(),
        api.getTimeline('day'),
        api.getTopProjects(10),
      ])
      stats.value = s.data
      timeline.value = t.data.points
      topProjects.value = tp.data
    } catch (e) {
      console.error('Failed to fetch stats:', e)
    } finally {
      loading.value = false
    }
  }

  return { stats, timeline, topProjects, loading, fetchStats }
})
