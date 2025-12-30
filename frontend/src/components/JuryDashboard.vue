<template>
  <div class="jury-dashboard mt-4">

    <!-- Statistics Cards -->
    <div class="stats-row mb-4">
      <div class="stat-card">
        <div class="stat-icon total">
          <i class="fas fa-trophy"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ totalContests }}</div>
          <div class="stat-label">Total Contests</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon current">
          <i class="fas fa-clock"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ currentContests }}</div>
          <div class="stat-label">Current Contests</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon submissions">
          <i class="fas fa-file-alt"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ totalSubmissions }}</div>
          <div class="stat-label">Total Submissions</div>
        </div>
      </div>
    </div>

    <!-- Main Card -->
    <div class="card">
      <!-- Header -->
      <div class="card-header d-flex align-items-center justify-content-between">
        <div>
          <h5 class="mb-0 d-flex align-items-center">
            <i class="fas fa-gavel me-2"></i>
            Jury Dashboard
          </h5>
          <small class="opacity-75">
            Contests assigned for review
          </small>
        </div>

        <span v-if="juryContests.length" class="badge bg-light text-dark px-3 py-2">
          {{ juryContests.length }} contests
        </span>
      </div>

      <div class="card-body">

        <!-- Loading -->
        <div v-if="loading" class="loading-box">
          <div class="spinner-border text-primary"></div>
          <p class="mt-2 text-muted mb-0">
            Loading assigned contests…
          </p>
        </div>

        <!-- Empty State -->
        <div v-else-if="juryContests.length === 0" class="empty-box">
          <i class="fas fa-inbox"></i>
          <p class="mt-3 mb-1 fw-semibold">
            No contests assigned yet
          </p>
          <small>
            You'll see contests here once you are added as a jury member.
          </small>
        </div>

        <!-- Table -->
        <div v-else class="table-responsive">
          <table class="table jury-table align-middle">
            <thead>
              <tr>
                <th>Contest</th>
                <th>Project</th>
                <th>Status</th>
                <th>Submissions</th>
                <th>Created</th>
                <th class="text-end">Action</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="contest in juryContests" :key="contest.id">
                <td>
                  <div class="fw-semibold">
                    {{ contest.name }}
                  </div>
                  <small class="text-muted">
                    {{ contest.slug }}
                  </small>
                </td>

                <td class="text-muted">
                  {{ contest.project_name || '—' }}
                </td>

                <td>
                  <span :class="`status-pill ${contest.status}`">
                    <span class="dot"></span>
                    {{ contest.status }}
                  </span>
                </td>

                <td class="fw-semibold">
                  {{ contest.submission_count }}
                </td>

                <td class="text-muted">
                  {{ formatDate(contest.created_at) }}
                </td>

                <td class="text-end">
                  <button class="btn btn-sm btn-primary-soft" @click="goToContest(contest)">
                    <i class="fas fa-arrow-right me-1"></i>
                    {{ contest.status === 'past' ? 'Go to Contest' : 'Review' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>
  </div>
</template>


<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

export default {
  name: 'JuryDashboard',

  setup() {
    const router = useRouter()
    const juryContests = ref([])
    const loading = ref(false)

    // Computed statistics
    const totalContests = computed(() => juryContests.value.length)

    const currentContests = computed(() =>
      juryContests.value.filter(c => c.status === 'current').length
    )

    const totalSubmissions = computed(() =>
      juryContests.value.reduce((sum, c) => sum + (c.submission_count || 0), 0)
    )

    const pendingReviews = computed(() =>
      juryContests.value
        .filter(c => c.status === 'current')
        .reduce((sum, c) => sum + (c.submission_count || 0), 0)
    )

    const loadJuryContests = async () => {
      loading.value = true
      try {
        const data = await api.get('/user/dashboard')
        // Sort: current first, then upcoming, then past
        const contests = data.jury_contests || []
        juryContests.value = contests.sort((a, b) => {
          const order = { current: 1, upcoming: 2, past: 3 }
          return (order[a.status] || 4) - (order[b.status] || 4)
        })
      } catch (error) {
        console.error('Failed to load jury contests', error)
        juryContests.value = []
      } finally {
        loading.value = false
      }
    }

    const goToContest = (contest) => {
      router.push({
        name: 'ContestView',
        params: { name: contest.slug || contest.name }
      })
    }

    const formatDate = (date) => {
      if (!date) return ''
      return new Date(date).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    onMounted(loadJuryContests)

    return {
      juryContests,
      loading,
      totalContests,
      currentContests,
      totalSubmissions,
      pendingReviews,
      goToContest,
      formatDate
    }
  }
}
</script>

<style scoped>
/* Statistics Cards */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.25rem;
}

.stat-card {
  background: var(--card-bg, white);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  border: 1px solid var(--border-color, #e9ecef);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  background: var(--wiki-primary);
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary, #1a1a1a);
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted, #6c757d);
  margin-top: 0.25rem;
  font-weight: 500;
}

/* Card */
.jury-dashboard .card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  background: var(--card-bg, white);
  border: 1px solid var(--border-color, #e9ecef);
}

/* Header */
.jury-dashboard .card-header {
  background: var(--wiki-primary);
  color: #fff;
}

/* Loading */
.loading-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem 0;
}

/* Empty */
.empty-box {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted, #6c757d);
}

.empty-box i {
  font-size: 2.2rem;
  color: var(--wiki-primary);
}

/* Table */
.jury-table thead th {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted, #6c757d);
  background-color: var(--table-header-bg, #f8f9fa);
}

.jury-table tbody tr {
  transition: all 0.2s ease;
}

.jury-table tbody tr:hover {
  background-color: var(--table-hover-bg, #f5f8ff);
  transform: translateY(-1px);
}

/* Status pill */
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 20px;
  text-transform: capitalize;
}

.status-pill .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-pill.current {
  background: var(--status-current-bg, #e6f4ea);
  color: var(--status-current-text, #198754);
}

.status-pill.current .dot {
  background: var(--status-current-text, #198754);
}

.status-pill.upcoming {
  background: var(--status-upcoming-bg, #e7f1ff);
  color: var(--wiki-primary);
}

.status-pill.upcoming .dot {
  background: var(--wiki-primary);
}

.status-pill.past {
  background: var(--status-past-bg, #ececec);
  color: var(--status-past-text, #6c757d);
}

.status-pill.past .dot {
  background: var(--status-past-text, #6c757d);
}

/* Button */
.btn-primary-soft {
  background-color: var(--btn-soft-bg, rgba(13, 110, 253, 0.1));
  color: var(--wiki-primary);
  border: none;
  transition: all 0.2s ease;
}

.btn-primary-soft:hover {
  background-color: var(--wiki-primary);
  color: #fff;
  transform: translateY(-1px);
}

/* Responsive */
@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-card {
    padding: 1rem;
  }

  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 1.25rem;
  }

  .stat-value {
    font-size: 1.5rem;
  }

  .jury-table {
    font-size: 0.9rem;
  }
}

@media (max-width: 576px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}

/* Dark Mode Support */
[data-theme="dark"] .stat-card,
.dark-mode .stat-card {
  background: var(--card-bg, #1e1e1e);
  border-color: var(--border-color, #333);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

[data-theme="dark"] .stat-card:hover,
.dark-mode .stat-card:hover {
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
}

[data-theme="dark"] .stat-value,
.dark-mode .stat-value {
  color: var(--text-primary, #ffffff);
}

[data-theme="dark"] .stat-label,
.dark-mode .stat-label {
  color: var(--text-muted, #a0a0a0);
}

[data-theme="dark"] .jury-dashboard .card,
.dark-mode .jury-dashboard .card {
  background: var(--card-bg, #1e1e1e);
  border-color: var(--border-color, #333);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

[data-theme="dark"] .jury-table thead th,
.dark-mode .jury-table thead th {
  background-color: var(--table-header-bg, #2a2a2a);
  color: var(--text-muted, #a0a0a0);
}

[data-theme="dark"] .jury-table tbody tr:hover,
.dark-mode .jury-table tbody tr:hover {
  background-color: var(--table-hover-bg, #2a2a2a);
}

[data-theme="dark"] .empty-box,
.dark-mode .empty-box {
  color: var(--text-muted, #a0a0a0);
}

[data-theme="dark"] .btn-primary-soft,
.dark-mode .btn-primary-soft {
  background-color: var(--btn-soft-bg, rgba(13, 110, 253, 0.2));
}
</style>