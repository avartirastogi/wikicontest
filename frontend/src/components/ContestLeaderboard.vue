<template>
    <div class="container py-5">
        <!-- Header with Back Button -->
        <div class="mb-4 d-flex justify-content-between align-items-center">
            <button class="btn btn-outline-secondary" @click="goBack">
                <i class="fas fa-arrow-left me-2"></i>Back to Contest
            </button>

            <button v-if="!loading" class="btn btn-primary" @click="refreshLeaderboard" :disabled="refreshing">
                <span v-if="refreshing" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="fas fa-sync-alt me-2"></i>
                {{ refreshing ? 'Refreshing...' : 'Refresh' }}
            </button>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-3 text-muted">Loading leaderboard...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="alert alert-danger">
            <i class="fas fa-exclamation-circle me-2"></i>{{ error }}
            <button class="btn btn-sm btn-outline-danger ms-3" @click="goBack">
                Go Back
            </button>
        </div>

        <!-- Leaderboard Content -->
        <div v-else-if="contest" class="leaderboard-view">
            <!-- Contest Header -->
            <div class="contest-header-section mb-4">
                <h1 class="contest-title">
                    <i class="fas fa-trophy me-3 trophy-icon"></i>{{ contest.name }}
                </h1>
                <div class="contest-meta">
                    <span class="badge bg-primary me-2">Leaderboard</span>
                    <span class="badge" :class="getStatusBadgeClass(contest.status)">
                        {{ getStatusLabel(contest.status) }}
                    </span>
                </div>
            </div>

            <!-- Contest Statistics -->
            <div class="row mb-4">
                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="stat-card">
                        <div class="stat-icon-wrapper">
                            <div class="stat-icon bg-primary">
                                <i class="fas fa-file-alt"></i>
                            </div>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">{{ contestStats.total_submissions }}</div>
                            <div class="stat-label">Total Submissions</div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="stat-card">
                        <div class="stat-icon-wrapper">
                            <div class="stat-icon bg-success">
                                <i class="fas fa-check-circle"></i>
                            </div>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">{{ contestStats.total_reviewed }}</div>
                            <div class="stat-label">Reviewed</div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="stat-card">
                        <div class="stat-icon-wrapper">
                            <div class="stat-icon bg-warning">
                                <i class="fas fa-clock"></i>
                            </div>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">{{ contestStats.total_pending }}</div>
                            <div class="stat-label">Pending Review</div>
                        </div>
                    </div>
                </div>

                <div class="col-lg-3 col-md-6 mb-3">
                    <div class="stat-card">
                        <div class="stat-icon-wrapper">
                            <div class="stat-icon bg-info">
                                <i class="fas fa-star"></i>
                            </div>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">{{ contestStats.total_marks_awarded }}</div>
                            <div class="stat-label">Total Marks</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Filters -->
            <div class="card mb-4 filters-card">
                <div class="card-header">
                    <h5 class="mb-0"><i class="fas fa-filter me-2"></i>Filters</h5>
                </div>
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-lg-3 col-md-6">
                            <label class="form-label">Filter by Status</label>
                            <select v-model="filters.filter_type" class="form-select" @change="applyFilters">
                                <option value="all">All Participants</option>
                                <option value="reviewed">Reviewed Only</option>
                                <option value="pending">Pending Only</option>
                            </select>
                        </div>

                        <div class="col-lg-3 col-md-6">
                            <label class="form-label">Minimum Marks</label>
                            <input v-model.number="filters.min_marks" type="number" class="form-control"
                                placeholder="e.g., 100" @change="applyFilters" />
                        </div>

                        <div class="col-lg-3 col-md-6">
                            <label class="form-label">Sort By</label>
                            <select v-model="filters.sort_by" class="form-select" @change="applyFilters">
                                <option value="marks">Total Marks</option>
                                <option value="submissions">Submission Count</option>
                            </select>
                        </div>

                        <div class="col-lg-3 col-md-6 d-flex align-items-end">
                            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
                                <i class="fas fa-undo me-2"></i>Reset Filters
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Empty State -->
            <div v-if="leaderboard.length === 0" class="card empty-state-card">
                <div class="card-body text-center py-5">
                    <i class="fas fa-trophy empty-state-icon mb-3"></i>
                    <h4 class="mb-3">No participants found</h4>
                    <p class="text-muted mb-0">
                        {{ filters.filter_type !== 'all' || filters.min_marks
                            ? 'Try adjusting your filters to see more results'
                            : 'No submissions have been made to this contest yet' }}
                    </p>
                </div>
            </div>

            <!-- Leaderboard Table -->
            <div v-else class="card leaderboard-card">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            <i class="fas fa-list-ol me-2"></i>Rankings
                        </h5>
                        <span class="badge bg-secondary">{{ pagination.total_results }} participants</span>
                    </div>
                </div>
                <div class="card-body p-0">
                    <div class="table-responsive">
                        <table class="table table-hover mb-0 leaderboard-table">
                            <thead>
                                <tr>
                                    <th class="rank-col">Rank</th>
                                    <th>Username</th>
                                    <th class="text-center">Submissions</th>
                                    <th class="text-center">Total Marks</th>
                                    <th class="text-center">Reviewed</th>
                                    <th class="text-center">Pending</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="participant in leaderboard" :key="participant.user_id"
                                    :class="getRankRowClass(participant.rank)">
                                    <td class="rank-col">
                                        <div class="rank-badge" :class="getRankBadgeClass(participant.rank)">
                                            <span v-if="participant.rank <= 3" class="rank-icon">
                                                <i :class="getRankIcon(participant.rank)"></i>
                                            </span>
                                            <span v-else class="rank-number">{{ participant.rank }}</span>
                                        </div>
                                    </td>
                                    <td>
                                        <div class="username-cell">
                                            <i class="fas fa-user me-2 text-muted"></i>
                                            <strong>{{ participant.username }}</strong>
                                        </div>
                                    </td>
                                    <td class="text-center">
                                        <span class="badge bg-light text-dark submissions-badge">
                                            {{ participant.total_submissions }}
                                        </span>
                                    </td>
                                    <td class="text-center">
                                        <strong class="marks-highlight">{{ participant.total_marks }}</strong>
                                    </td>
                                    <td class="text-center">
                                        <span class="badge bg-success">{{ participant.reviewed_count }}</span>
                                    </td>
                                    <td class="text-center">
                                        <span class="badge bg-warning text-dark">{{ participant.pending_count }}</span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- Pagination -->
            <div v-if="pagination.total_pages > 1" class="d-flex justify-content-center mt-4">
                <nav>
                    <ul class="pagination">
                        <li class="page-item" :class="{ disabled: pagination.page === 1 }">
                            <button class="page-link" @click="changePage(pagination.page - 1)"
                                :disabled="pagination.page === 1">
                                <i class="fas fa-chevron-left"></i>
                            </button>
                        </li>

                        <li v-for="page in visiblePages" :key="page" class="page-item"
                            :class="{ active: page === pagination.page }">
                            <button class="page-link" @click="changePage(page)">
                                {{ page }}
                            </button>
                        </li>

                        <li class="page-item" :class="{ disabled: pagination.page === pagination.total_pages }">
                            <button class="page-link" @click="changePage(pagination.page + 1)"
                                :disabled="pagination.page === pagination.total_pages">
                                <i class="fas fa-chevron-right"></i>
                            </button>
                        </li>
                    </ul>
                </nav>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../services/api'
import { showAlert } from '../utils/alerts'

export default {
    name: 'ContestLeaderboard',

    setup() {
        const router = useRouter()
        const route = useRoute()

        // State
        const contest = ref(null)
        const contestStats = ref({
            total_submissions: 0,
            total_reviewed: 0,
            total_pending: 0,
            total_marks_awarded: 0
        })
        const leaderboard = ref([])
        const loading = ref(true)
        const refreshing = ref(false)
        const error = ref(null)

        // Filters
        const filters = ref({
            filter_type: 'all',
            min_marks: null,
            sort_by: 'marks'
        })

        // Pagination
        const pagination = ref({
            page: 1,
            per_page: 50,
            total_pages: 1,
            total_results: 0
        })

        // Get contest ID from contest name
        const getContestId = async () => {
            try {
                const contestName = route.params.name
                const contestData = await api.get(`/contest/name/${contestName}`)
                return contestData.id
            } catch (err) {
                console.error('Error getting contest ID:', err)
                throw err
            }
        }

        // Load leaderboard data
        const loadLeaderboard = async (showLoading = true) => {
            if (showLoading) loading.value = true
            else refreshing.value = true
            error.value = null

            try {
                const contestId = await getContestId()

                // Build query parameters
                const params = {
                    filter: filters.value.filter_type,
                    sort_by: filters.value.sort_by,
                    page: pagination.value.page,
                    per_page: pagination.value.per_page
                }

                if (filters.value.min_marks) {
                    params.min_marks = filters.value.min_marks
                }

                // Fetch leaderboard
                const data = await api.get(`/contest/${contestId}/leaderboard`, { params })

                contest.value = data.contest
                contestStats.value = data.contest_stats
                leaderboard.value = data.leaderboard
                pagination.value = data.pagination
            } catch (err) {
                console.error('Error loading leaderboard:', err)
                error.value = 'Failed to load leaderboard: ' + (err.message || 'Unknown error')
            } finally {
                loading.value = false
                refreshing.value = false
            }
        }

        // Apply filters
        const applyFilters = () => {
            pagination.value.page = 1
            loadLeaderboard(false)
        }

        // Reset filters
        const resetFilters = () => {
            filters.value = {
                filter_type: 'all',
                min_marks: null,
                sort_by: 'marks'
            }
            pagination.value.page = 1
            loadLeaderboard(false)
        }

        // Refresh leaderboard
        const refreshLeaderboard = () => {
            loadLeaderboard(false)
        }

        // Change page
        const changePage = (page) => {
            if (page < 1 || page > pagination.value.total_pages) return
            pagination.value.page = page
            loadLeaderboard(false)
            window.scrollTo({ top: 0, behavior: 'smooth' })
        }

        // Visible pages for pagination
        const visiblePages = computed(() => {
            const total = pagination.value.total_pages
            const current = pagination.value.page
            const delta = 2
            const pages = []

            for (let i = Math.max(1, current - delta); i <= Math.min(total, current + delta); i++) {
                pages.push(i)
            }

            return pages
        })

        // Get status label
        const getStatusLabel = (status) => {
            const labels = {
                current: 'Active',
                upcoming: 'Upcoming',
                past: 'Ended',
                unknown: 'Unknown'
            }
            return labels[status] || 'Unknown'
        }

        // Get status badge class
        const getStatusBadgeClass = (status) => {
            const classes = {
                current: 'bg-success',
                upcoming: 'bg-warning',
                past: 'bg-secondary',
                unknown: 'bg-secondary'
            }
            return classes[status] || 'bg-secondary'
        }

        // Get rank row class
        const getRankRowClass = (rank) => {
            if (rank === 1) return 'rank-row-1'
            if (rank === 2) return 'rank-row-2'
            if (rank === 3) return 'rank-row-3'
            return ''
        }

        // Get rank badge class
        const getRankBadgeClass = (rank) => {
            if (rank === 1) return 'rank-badge-gold'
            if (rank === 2) return 'rank-badge-silver'
            if (rank === 3) return 'rank-badge-bronze'
            return 'rank-badge-default'
        }

        // Get rank icon
        const getRankIcon = (rank) => {
            if (rank === 1) return 'fas fa-trophy'
            if (rank === 2) return 'fas fa-medal'
            if (rank === 3) return 'fas fa-award'
            return ''
        }

        // Go back to contest view
        const goBack = () => {
            router.push({
                name: 'ContestView',
                params: { name: route.params.name }
            })
        }

        // Load on mount
        onMounted(() => {
            loadLeaderboard()
        })

        return {
            contest,
            contestStats,
            leaderboard,
            loading,
            refreshing,
            error,
            filters,
            pagination,
            visiblePages,
            applyFilters,
            resetFilters,
            refreshLeaderboard,
            changePage,
            getStatusLabel,
            getStatusBadgeClass,
            getRankRowClass,
            getRankBadgeClass,
            getRankIcon,
            goBack
        }
    }
}
</script>

<style scoped>
/* Leaderboard View - Matching WikiContest Theme */
.leaderboard-view {
    max-width: 1200px;
    margin: 0 auto;
}

/* Contest Header Section - Matching ContestView style */
.contest-header-section {
    border-bottom: 2px solid var(--wiki-primary);
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
}

.contest-title {
    color: var(--wiki-dark);
    font-weight: 700;
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    transition: color 0.3s ease;
}

[data-theme="dark"] .contest-title {
    color: #ffffff !important;
}

.trophy-icon {
    color: var(--wiki-primary);
}

.contest-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.contest-meta .badge {
    font-weight: 500;
    padding: 0.4em 0.8em;
    font-size: 0.85em;
}

/* Statistics Cards - Matching ContestView card style */
.stat-card {
    background: white;
    border: 1px solid var(--wiki-border);
    border-radius: 8px;
    padding: 1.25rem;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
    height: 100%;
}

[data-theme="dark"] .stat-card {
    background-color: #2a2a2a;
    border-color: #444;
}

.stat-card:hover {
    box-shadow: 0 4px 8px rgba(0, 102, 153, 0.15);
    transform: translateY(-2px);
}

.stat-icon-wrapper {
    margin-right: 1rem;
}

.stat-icon {
    width: 50px;
    height: 50px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    color: white;
}

.stat-icon.bg-primary {
    background-color: var(--wiki-primary);
}

.stat-icon.bg-success {
    background-color: #28a745;
}

.stat-icon.bg-warning {
    background-color: #ffc107;
    color: #000;
}

.stat-icon.bg-info {
    background-color: #17a2b8;
}

.stat-content {
    flex: 1;
}

.stat-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--wiki-dark);
    line-height: 1;
    margin-bottom: 0.25rem;
}

[data-theme="dark"] .stat-value {
    color: #ffffff;
}

.stat-label {
    color: var(--wiki-text-muted);
    font-size: 0.85rem;
    font-weight: 500;
}

/* Card Styling - Matching ContestView cards */
.card {
    border: 1px solid var(--wiki-border);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: box-shadow 0.2s ease;
}

[data-theme="dark"] .card {
    background-color: #2a2a2a;
    border-color: #444;
}

.card:hover {
    box-shadow: 0 4px 8px rgba(0, 102, 153, 0.15);
}

.card-header {
    background-color: var(--wiki-primary);
    color: white;
    border-bottom: none;
    padding: 1rem 1.5rem;
    font-weight: 600;
    border-radius: 8px 8px 0 0;
}

.card-body {
    padding: 1.5rem;
}

/* Filters Card */
.filters-card .card-body {
    padding: 1.25rem 1.5rem;
}

.form-label {
    font-weight: 600;
    color: var(--wiki-dark);
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}

[data-theme="dark"] .form-label {
    color: #ffffff;
}

.form-control,
.form-select {
    border: 1px solid var(--wiki-border);
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
    transition: all 0.2s ease;
    background-color: white;
    color: var(--wiki-dark);
}

[data-theme="dark"] .form-control,
[data-theme="dark"] .form-select {
    background-color: #2a2a2a;
    color: #ffffff;
    border-color: #444;
}

.form-control:focus,
.form-select:focus {
    border-color: var(--wiki-primary);
    box-shadow: 0 0 0 0.2rem rgba(0, 102, 153, 0.25);
    outline: none;
}

/* Empty State */
.empty-state-card .card-body {
    padding: 3rem 1.5rem;
}

.empty-state-icon {
    font-size: 4rem;
    color: var(--wiki-primary);
    opacity: 0.3;
}

.empty-state-card h4 {
    color: var(--wiki-dark);
    font-weight: 600;
}

[data-theme="dark"] .empty-state-card h4 {
    color: #ffffff;
}

/* Leaderboard Table - Matching ContestView table style */
.leaderboard-table {
    font-size: 1rem;
    margin: 0;
}

.leaderboard-table thead th {
    background-color: rgba(0, 102, 153, 0.1);
    color: var(--wiki-primary);
    font-weight: 600;
    border-bottom: 2px solid var(--wiki-primary);
    padding: 0.75rem;
    white-space: nowrap;
}

[data-theme="dark"] .leaderboard-table thead th {
    background-color: rgba(93, 184, 230, 0.15);
    border-bottom-color: var(--wiki-primary);
}

.leaderboard-table tbody tr {
    transition: background-color 0.2s ease;
    border-bottom: 1px solid var(--wiki-border);
}

[data-theme="dark"] .leaderboard-table tbody tr {
    border-bottom-color: #444;
}

.leaderboard-table tbody tr:hover {
    background-color: var(--wiki-hover-bg);
}

.leaderboard-table tbody td {
    padding: 0.75rem;
    vertical-align: middle;
    color: var(--wiki-text);
}

/* Top 3 Row Highlights */
.rank-row-1 {
    background-color: rgba(255, 215, 0, 0.08) !important;
}

.rank-row-2 {
    background-color: rgba(192, 192, 192, 0.08) !important;
}

.rank-row-3 {
    background-color: rgba(205, 127, 50, 0.08) !important;
}

[data-theme="dark"] .rank-row-1:hover,
[data-theme="dark"] .rank-row-2:hover,
[data-theme="dark"] .rank-row-3:hover {
    background-color: rgba(93, 184, 230, 0.1) !important;
}

/* Rank Badge */
.rank-col {
    width: 70px;
    text-align: center;
}

.rank-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 45px;
    height: 45px;
    border-radius: 50%;
    font-weight: 700;
    font-size: 1.1rem;
}

.rank-badge-gold {
    background: linear-gradient(135deg, #ffd700, #ffed4e);
    color: #000;
    box-shadow: 0 2px 6px rgba(255, 215, 0, 0.4);
}

.rank-badge-silver {
    background: linear-gradient(135deg, #c0c0c0, #e8e8e8);
    color: #444;
    box-shadow: 0 2px 6px rgba(192, 192, 192, 0.4);
}

.rank-badge-bronze {
    background: linear-gradient(135deg, #cd7f32, #e89c5f);
    color: #fff;
    box-shadow: 0 2px 6px rgba(205, 127, 50, 0.4);
}

.rank-badge-default {
    background-color: #f8f9fa;
    color: var(--wiki-dark);
    border: 2px solid #dee2e6;
}

[data-theme="dark"] .rank-badge-default {
    background-color: #3a3a3a;
    color: #ffffff;
    border-color: #555;
}

.rank-icon {
    font-size: 1.3rem;
}

.rank-number {
    font-size: 1rem;
}

/* Username Cell */
.username-cell {
    display: flex;
    align-items: center;
}

.username-cell strong {
    color: var(--wiki-dark);
    font-weight: 600;
}

[data-theme="dark"] .username-cell strong {
    color: #ffffff;
}

/* Marks Highlight */
.marks-highlight {
    color: var(--wiki-primary);
    font-size: 1.15rem;
    font-weight: 700;
}

/* Badges - Matching ContestView badge style */
.badge {
    font-weight: 500;
    padding: 0.4em 0.8em;
    font-size: 0.85em;
}

.submissions-badge {
    border: 1px solid #dee2e6;
}

[data-theme="dark"] .submissions-badge {
    background-color: #3a3a3a !important;
    color: #ffffff !important;
    border-color: #555;
}

.badge.bg-primary {
    background-color: var(--wiki-primary) !important;
}

/* Button Styling - Matching ContestView buttons */
.btn-primary {
    background-color: var(--wiki-primary);
    border-color: var(--wiki-primary);
    transition: all 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
    background-color: var(--wiki-primary-hover);
    border-color: var(--wiki-primary-hover);
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 102, 153, 0.3);
}

.btn-outline-secondary {
    border-color: var(--wiki-text-muted);
    color: var(--wiki-text-muted);
    transition: all 0.2s ease;
}

.btn-outline-secondary:hover {
    background-color: var(--wiki-text-muted);
    border-color: var(--wiki-text-muted);
    color: white;
}

/* Pagination - Matching ContestView pagination */
.pagination {
    margin: 0;
}

.pagination .page-link {
    color: var(--wiki-primary);
    border-color: var(--wiki-border);
    padding: 0.5rem 0.75rem;
    transition: all 0.2s ease;
}

[data-theme="dark"] .pagination .page-link {
    background-color: #2a2a2a;
    border-color: #444;
    color: var(--wiki-primary);
}

.pagination .page-item.active .page-link {
    background-color: var(--wiki-primary);
    border-color: var(--wiki-primary);
    color: white;
}

.pagination .page-link:hover:not(.disabled) {
    background-color: rgba(0, 102, 153, 0.1);
    color: var(--wiki-primary);
    border-color: var(--wiki-primary);
}

.pagination .page-item.disabled .page-link {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Alert Styling - Matching ContestView alerts */
.alert {
    border-radius: 0.5rem;
    border-left: 4px solid;
    padding: 0.75rem 1rem;
}

.alert-danger {
    background-color: rgba(153, 0, 0, 0.1);
    border-color: var(--wiki-danger);
    color: var(--wiki-danger);
}

/* Spinner - Matching ContestView spinner */
.spinner-border.text-primary {
    color: var(--wiki-primary) !important;
    width: 3rem;
    height: 3rem;
    border-width: 0.3em;
}

/* Responsive */
@media (max-width: 768px) {
    .contest-title {
        font-size: 1.5rem;
    }

    .stat-card {
        padding: 1rem;
    }

    .stat-icon {
        width: 50px;
        height: 50px;
        font-size: 1.2rem;
    }

    .stat-content h3 {
        font-size: 1.5rem;
    }

    .leaderboard-table {
        font-size: 0.9rem;
    }

    .rank-badge {
        width: 40px;
        height: 40px;
        font-size: 1rem;
    }
}
</style>