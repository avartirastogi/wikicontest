<template>
  <div class="modal fade" id="contestModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ contest?.name }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body" v-if="contest">
          <div class="row">
            <div :class="canViewSubmissions ? 'col-md-6' : 'col-md-12'">
              <h6>Contest Details</h6>
              <p><strong>Project:</strong> {{ contest.project_name }}</p>
              <p><strong>Created by:</strong> {{ contest.created_by }}</p>
              <p><strong>Status:</strong> <span class="badge bg-primary">{{ contest.status }}</span></p>
              <p v-if="contest.start_date"><strong>Start Date:</strong> {{ formatDate(contest.start_date) }}</p>
              <p v-if="contest.end_date"><strong>End Date:</strong> {{ formatDate(contest.end_date) }}</p>
            </div>
            <div v-if="canViewSubmissions" class="col-md-6">
              <h6>Scoring</h6>
              <p><strong>Accepted:</strong> {{ contest.marks_setting_accepted }} points</p>
              <p><strong>Rejected:</strong> {{ contest.marks_setting_rejected }} points</p>
              <p><strong>Submissions:</strong> {{ contest.submission_count }}</p>
            </div>
          </div>
          <div v-if="contest.description" class="mt-3 description-section">
            <h6>Description</h6>
            <p class="description-text">{{ contest.description }}</p>
          </div>
          <div v-if="contest.jury_members && contest.jury_members.length > 0" class="mt-3 jury-section">
            <h6>Jury Members</h6>
            <p>{{ contest.jury_members.join(', ') }}</p>
          </div>

          <!-- Submissions Section (for jury and contest creators) -->
          <div v-if="canViewSubmissions" class="mt-4">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6>Submissions</h6>
              <button
                v-if="loadingSubmissions || refreshingMetadata"
                class="btn btn-sm btn-outline-secondary"
                disabled
              >
                <span class="spinner-border spinner-border-sm me-2"></span>{{ loadingSubmissions ? 'Loading...' : 'Refreshing...' }}
              </button>
              <button
                v-else
                class="btn btn-sm btn-outline-light"
                @click="refreshMetadata"
                :disabled="submissions.length === 0"
                title="Refresh article metadata (word count, author, etc.) from MediaWiki and reload submissions"
                style="color: white; border-color: white;"
              >
                <i class="fas fa-database me-1"></i>Refresh Metadata
              </button>
            </div>

            <div v-if="submissions.length === 0 && !loadingSubmissions" class="alert alert-info">
              <i class="fas fa-info-circle me-2"></i>No submissions yet for this contest.
            </div>

            <div v-else-if="submissions.length > 0" class="table-responsive">
              <table class="table table-sm table-hover">
                <thead>
                  <tr>
                    <th>Article Title</th>
                    <th>Article Author</th>
                    <th>Submitted By</th>
                    <th>Status</th>
                    <th>Score</th>
                    <th>Submitted At</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="submission in submissions" :key="submission.id">
                    <td>
                      <a
                        href="#"
                        @click.prevent="showArticlePreview(submission.article_link, submission.article_title)"
                        class="text-decoration-none article-title-link"
                        :title="submission.article_link"
                      >
                        {{ submission.article_title }}
                        <i class="fas fa-eye ms-1" style="font-size: 0.8em;"></i>
                      </a>
                      <div
                        v-if="submission.article_word_count && submission.article_word_count > 0"
                        class="text-muted small mt-1"
                      >
                        <i class="fas fa-file-alt me-1"></i>{{ formatWordCount(submission.article_word_count) }}
                      </div>
                      <div v-else-if="submission.article_word_count === 0" class="text-muted small mt-1">
                        <i class="fas fa-file-alt me-1"></i>Size: 0 bytes
                      </div>
                    </td>
                    <td>
                      <div v-if="submission.article_author">
                        <i class="fas fa-user me-1"></i>{{ submission.article_author }}
                      </div>
                      <div v-else class="text-muted small">Unknown</div>
                      <div v-if="submission.article_created_at" class="text-muted small mt-1">
                        <i class="fas fa-calendar me-1"></i>{{ formatDateShort(submission.article_created_at) }}
                      </div>
                    </td>
                    <td>{{ submission.username || 'Unknown' }}</td>
                    <td>
                      <span :class="`badge bg-${getStatusColor(submission.status)}`">
                        {{ submission.status }}
                      </span>
                    </td>
                    <td>{{ submission.score || 0 }}</td>
                    <td>{{ formatDate(submission.submitted_at) }}</td>
                    <td>
                      <button
                        @click="showArticlePreview(submission.article_link, submission.article_title)"
                        class="btn btn-sm btn-outline-primary"
                        title="Preview Article"
                      >
                        <i class="fas fa-eye"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <!-- Debug info and auth status -->
          <div class="me-auto">
            <!-- Warning if user is not loaded -->
            <div
              v-if="contest && !currentUser && !checkingAuth"
              class="alert alert-warning py-1 px-2 mb-2"
              style="font-size: 0.75rem;"
            >
              <i class="fas fa-exclamation-triangle me-1"></i>
              <strong>User not loaded!</strong>
              <button class="btn btn-sm btn-outline-warning ms-2" @click="forceAuthRefresh" style="font-size: 0.7rem;">
                <i class="fas fa-sync-alt me-1"></i>Refresh Auth
              </button>
            </div>
          </div>
          <button
            v-if="canDeleteContest"
            class="btn btn-danger"
            @click="handleDeleteContest"
            :disabled="deletingContest"
          >
            <span v-if="deletingContest" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="fas fa-trash me-2"></i>
            {{ deletingContest ? 'Deleting...' : 'Delete Contest' }}
          </button>
          <button
            v-if="contest?.status === 'current' && isAuthenticated && !canViewSubmissions"
            class="btn btn-primary"
            @click="handleSubmitArticle"
          >
            Submit Article
          </button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Article Preview Modal -->
  <ArticlePreviewModal
    :article-url="previewArticleUrl"
    :article-title="previewArticleTitle"
  />
</template>

<script>
import { computed, ref, watch } from 'vue'
import { useStore } from '../store'
import api from '../services/api'
import { showAlert } from '../utils/alerts'
import ArticlePreviewModal from './ArticlePreviewModal.vue'

export default {
  name: 'ContestModal',
  components: {
    ArticlePreviewModal
  },
  props: {
    contest: {
      type: Object,
      default: null
    }
  },
  emits: ['submit-article', 'contest-deleted'],
  setup(props, { emit }) {
    const store = useStore()
    // Get reactive references to auth state
    // isAuthenticated should only be true if we have a valid user object
    // Use store.state.currentUser directly for better reactivity
    const currentUser = computed(() => {
      // Try multiple sources to get current user
      // Check store.state.currentUser first (direct reactive state access - most reliable)
      // Then check store.currentUser (computed property)
      // This ensures we get the most up-to-date value
      if (store.state && store.state.currentUser) {
        return store.state.currentUser
      }
      if (store.currentUser) {
        return store.currentUser
      }
      return null
    })
    const isAuthenticated = computed(() => {
      // Only authenticated if we have a valid user object
      // This ensures isAuthenticated and currentUser are always in sync
      const user = currentUser.value
      return !!user && !!user.id && !!user.username
    })

    // State for submissions
    const submissions = ref([])
    const loadingSubmissions = ref(false)
    const refreshingMetadata = ref(false)

    // State for delete operation
    const deletingContest = ref(false)

    // State for delete permission (updated after auth check)
    const canDeleteContest = ref(false)

    // State to track if auth check is in progress
    const checkingAuth = ref(false)

    // State for article preview modal
    const previewArticleUrl = ref('')
    const previewArticleTitle = ref('')

    // Check if user can view submissions (jury member or contest creator)
    const canViewSubmissions = computed(() => {
      if (!isAuthenticated.value || !props.contest || !currentUser.value) {
        return false
      }

      const username = (currentUser.value.username || '').trim().toLowerCase()
      const contest = props.contest

      // Check if user is contest creator (case-insensitive)
      const contestCreator = (contest.created_by || '').trim().toLowerCase()
      if (contestCreator && username === contestCreator) {
        return true
      }

      // Check if user is jury member (case-insensitive)
      if (contest.jury_members && Array.isArray(contest.jury_members)) {
        const juryUsernames = contest.jury_members.map(j => (j || '').trim().toLowerCase())
        return juryUsernames.includes(username)
      }

      return false
    })

    /**
     * Check if user can delete contest
     *
     * This works for both regular users and OAuth (Wikimedia) users:
     * - Regular users: username from registration
     * - OAuth users: Wikimedia username stored in username field
     *
     * When a contest is created, the backend stores user.username in created_by field,
     * so the comparison works the same way for both user types.
     */
    const checkDeletePermission = () => {
      // Reset to false initially
      canDeleteContest.value = false

      // Get current user from multiple sources to ensure we get the latest value
      // Try computed property first, then direct state access
      const userFromComputed = currentUser.value
      const userFromStore = store.currentUser
      const userFromState = (store.state && store.state.currentUser) || null

      // Use the first available user source
      const userToCheck = userFromComputed || userFromStore || userFromState

      console.log('=== Delete Permission Check ===')
      console.log('isAuthenticated:', isAuthenticated.value)
      console.log('hasContest:', !!props.contest)
      console.log('currentUser.value (computed):', userFromComputed)
      console.log('store.currentUser:', userFromStore)
      console.log('store.state.currentUser:', userFromState)
      console.log('userToCheck (final):', userToCheck)

      // Check basic requirements
      if (!isAuthenticated.value) {
        console.log('❌ Delete check: Not authenticated')
        canDeleteContest.value = false
        return
      }

      if (!props.contest) {
        console.log('❌ Delete check: No contest')
        canDeleteContest.value = false
        return
      }

      if (!userToCheck) {
        console.log('❌ Delete check: No current user object')
        console.log('Store state:', store.state)
        canDeleteContest.value = false
        return
      }

      // Get username from current user (works for both regular and OAuth users)
      const username = (userToCheck.username || '').trim()
      const contestCreator = (props.contest.created_by || '').trim()

      // If either is empty, can't match
      if (!username) {
        console.log('❌ Delete check: Username is empty', {
          userToCheck,
          currentUser: userFromComputed,
          storeUser: userFromStore,
          stateUser: userFromState
        })
        canDeleteContest.value = false
        return
      }

      if (!contestCreator) {
        console.log('❌ Delete check: Contest creator is empty', { contest: props.contest })
        canDeleteContest.value = false
        return
      }

      // Check if user is contest creator (case-insensitive comparison)
      // This works for both regular users and OAuth users since both use username
      const usernameLower = username.toLowerCase()
      const creatorLower = contestCreator.toLowerCase()
      const canDelete = usernameLower === creatorLower

      // Debug logging to help troubleshoot
      console.log('✅ Delete permission check result:', {
        username,
        contestCreator,
        usernameLower,
        creatorLower,
        match: canDelete,
        canDelete,
        note: 'Works for both regular and OAuth (Wikimedia) users'
      })

      canDeleteContest.value = canDelete
      console.log('=== End Delete Permission Check ===')
    }

    // Format date for display in Indian Standard Time (IST)
    // Converts UTC dates from backend to IST timezone for display
    const formatDate = (dateString) => {
      if (!dateString) return 'No date'
      try {
        // Ensure the date string is treated as UTC
        // If it doesn't end with 'Z', append it to indicate UTC timezone
        // This fixes the issue where naive UTC datetimes were being interpreted as local time
        let utcDateString = dateString
        if (!dateString.endsWith('Z') && !dateString.includes('+') && !dateString.includes('-', 10)) {
          // If no timezone indicator, assume it's UTC and append 'Z'
          utcDateString = dateString + 'Z'
        }
        
        // Convert to IST (Indian Standard Time) timezone
        // IST is UTC+5:30, timezone identifier is 'Asia/Kolkata'
        return new Date(utcDateString).toLocaleString('en-IN', {
          timeZone: 'Asia/Kolkata',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          hour12: true
        })
      } catch (e) {
        return dateString
      }
    }

    // Format date with full date and time in IST (for article creation date)
    // Shows complete date and time information including time in IST timezone
    const formatDateShort = (dateString) => {
      if (!dateString) return ''
      try {
        // Ensure the date string is treated as UTC
        // If it doesn't end with 'Z', append it to indicate UTC timezone
        // This fixes the issue where naive UTC datetimes were being interpreted as local time
        let utcDateString = dateString
        if (!dateString.endsWith('Z') && !dateString.includes('+') && !dateString.includes('-', 10)) {
          // If no timezone indicator, assume it's UTC and append 'Z'
          utcDateString = dateString + 'Z'
        }
        
        // Convert to IST (Indian Standard Time) timezone
        // IST is UTC+5:30, timezone identifier is 'Asia/Kolkata'
        // Show full date and time with month name, day, year, hour, and minute
        return new Date(utcDateString).toLocaleString('en-IN', {
          timeZone: 'Asia/Kolkata',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          hour12: true
        })
      } catch (e) {
        return dateString
      }
    }

    // Format word count for display
    const formatWordCount = (count) => {
      if (!count) return ''
      if (count >= 1000) {
        return `${(count / 1000).toFixed(1)}k words`
      }
      return `${count} words`
    }

    // Show article preview modal
    const showArticlePreview = (url, title) => {
      previewArticleUrl.value = url
      previewArticleTitle.value = title || 'Article'

      // Show modal using Bootstrap
      setTimeout(() => {
        const modalElement = document.getElementById('articlePreviewModal')
        if (modalElement) {
          const modal = new bootstrap.Modal(modalElement)
          modal.show()
        }
      }, 100)
    }

    // Get status badge color
    const getStatusColor = (status) => {
      switch (status?.toLowerCase()) {
        case 'accepted':
          return 'success'
        case 'rejected':
          return 'danger'
        case 'pending':
          return 'warning'
        default:
          return 'secondary'
      }
    }

    // Load submissions for the contest
    const loadSubmissions = async () => {
      if (!props.contest || !canViewSubmissions.value) {
        return
      }

      loadingSubmissions.value = true
      try {
        const data = await api.get(`/contest/${props.contest.id}/submissions`)
        submissions.value = data || []
      } catch (error) {
        console.error('Failed to load submissions:', error)
        showAlert('Failed to load submissions: ' + error.message, 'danger')
        submissions.value = []
      } finally {
        loadingSubmissions.value = false
      }
    }

    // Refresh article metadata for all submissions in the contest
    const refreshMetadata = async () => {
      if (!props.contest || !canViewSubmissions.value || submissions.value.length === 0) {
        return
      }

      refreshingMetadata.value = true
      try {
        const response = await api.post(`/submission/contest/${props.contest.id}/refresh-metadata`)
        showAlert(
          `Metadata refreshed: ${response.updated} updated, ${response.failed} failed`,
          response.failed === 0 ? 'success' : 'warning'
        )
        
        // Reload submissions to show updated data
        await loadSubmissions()
      } catch (error) {
        console.error('Failed to refresh metadata:', error)
        showAlert('Failed to refresh metadata: ' + error.message, 'danger')
      } finally {
        refreshingMetadata.value = false
      }
    }

    // Handle delete contest
    const handleDeleteContest = async () => {
      if (!props.contest) return

      // Confirm deletion
      const confirmed = confirm(
        `Are you sure you want to delete the contest "${props.contest.name}"?\n\n` +
        'This action cannot be undone and will delete all associated submissions.'
      )

      if (!confirmed) return

      deletingContest.value = true
      try {
        await api.delete(`/contest/${props.contest.id}`)
        showAlert('Contest deleted successfully', 'success')

        // Close modal
        const modalElement = document.getElementById('contestModal')
        const modal = bootstrap.Modal.getInstance(modalElement)
        if (modal) {
          modal.hide()
        }

        // Emit event to parent to reload contests
        emit('contest-deleted')
      } catch (error) {
        console.error('Failed to delete contest:', error)
        showAlert('Failed to delete contest: ' + error.message, 'danger')
      } finally {
        deletingContest.value = false
      }
    }

    const handleSubmitArticle = () => {
      emit('submit-article', props.contest.id)
      // Close this modal
      const modalElement = document.getElementById('contestModal')
      const modal = bootstrap.Modal.getInstance(modalElement)
      if (modal) {
        modal.hide()
      }
    }

    // Force auth refresh manually
    const forceAuthRefresh = async () => {
      checkingAuth.value = true
      try {
        console.log('🔄 Manual auth refresh triggered')
        await store.checkAuth()
        await new Promise(resolve => setTimeout(resolve, 200))
        checkDeletePermission()
        console.log('🔄 Auth refresh completed, user:', store.currentUser || (store.state && store.state.currentUser))
      } catch (error) {
        console.error('🔄 Auth refresh failed:', error)
      } finally {
        checkingAuth.value = false
      }
    }

    // Watch for changes in currentUser to update delete permission
    // This ensures permission updates when user data changes
    watch(() => currentUser.value, (newUser, oldUser) => {
      if (newUser && props.contest && !checkingAuth.value) {
        console.log('Current user changed, checking delete permission:', newUser)
        // Small delay to ensure reactivity
        setTimeout(() => {
          checkDeletePermission()
        }, 50)
      } else if (!newUser && oldUser && props.contest) {
        // User was cleared, reset permission
        console.log('User cleared, resetting delete permission')
        canDeleteContest.value = false
      }
    }, { deep: true, immediate: false })

    // Also watch store state directly as backup (only if store.state exists)
    if (store.state) {
      watch(() => store.state.currentUser, (newUser, oldUser) => {
        if (newUser && props.contest && !checkingAuth.value) {
          console.log('Store state user changed, checking delete permission:', newUser)
          setTimeout(() => {
            checkDeletePermission()
          }, 50)
        } else if (!newUser && oldUser && props.contest) {
          // User was cleared, reset permission
          console.log('Store state user cleared, resetting delete permission')
          canDeleteContest.value = false
        }
      }, { deep: true, immediate: false })
    }

    // Also watch store.currentUser computed property
    watch(() => store.currentUser, (newUser, oldUser) => {
      if (newUser && props.contest && !checkingAuth.value) {
        console.log('Store computed user changed, checking delete permission:', newUser)
        setTimeout(() => {
          checkDeletePermission()
        }, 50)
      } else if (!newUser && oldUser && props.contest) {
        // User was cleared, reset permission
        console.log('Store computed user cleared, resetting delete permission')
        canDeleteContest.value = false
      }
    }, { deep: true, immediate: false })

    // Watch for contest changes
    watch(() => props.contest, async (newContest) => {
      if (newContest) {
        // Reset state
        checkingAuth.value = true
        canDeleteContest.value = false

        try {
          console.log('🔍 Modal opened, checking auth for contest:', newContest.name)
          console.log('🔍 Contest created by:', newContest.created_by)

          // First, check if user is already in the store (from login)
          // This is faster and more reliable than calling checkAuth()
          let loadedUser = store.currentUser || (store.state && store.state.currentUser) || currentUser.value

          console.log('📊 Initial user check:', {
            storeCurrentUser: store.currentUser,
            stateCurrentUser: (store.state && store.state.currentUser) || null,
            computedCurrentUser: currentUser.value,
            loadedUser
          })

          // If user is not in store, try to load it via checkAuth
          if (!loadedUser) {
            console.log('⚠️ User not in store, calling checkAuth()...')
            let userLoaded = false
            let retries = 0
            const maxRetries = 3

            while (!userLoaded && retries < maxRetries) {
              try {
                const authResult = await store.checkAuth()

                // Wait for reactive state to update after checkAuth
                await new Promise(resolve => setTimeout(resolve, 150))

                // Check if user is actually loaded now
                const userNow = store.currentUser || (store.state && store.state.currentUser) || currentUser.value
                if (authResult && userNow) {
                  userLoaded = true
                  loadedUser = userNow
                  console.log('✅ User loaded after auth check:', loadedUser)
                  break
                } else {
                  console.log(`Auth check returned ${authResult} but user not loaded, retrying...`)
                }
              } catch (error) {
                console.error(`Auth check attempt ${retries + 1} failed:`, error)
              }

              if (!userLoaded && retries < maxRetries - 1) {
                console.log(`Retrying auth check... (${retries + 1}/${maxRetries})`)
                await new Promise(resolve => setTimeout(resolve, 300))
              }
              retries++
            }
          } else {
            console.log('✅ User already in store, using existing user:', loadedUser)
          }

          // Wait a bit for reactive state to fully propagate
          await new Promise(resolve => setTimeout(resolve, 100))

          // Final user check - try all sources again
          loadedUser = store.currentUser || (store.state && store.state.currentUser) || currentUser.value

          // Log for debugging
          console.log('📊 Final user state:', {
            isAuthenticated: store.isAuthenticated,
            currentUser: store.currentUser,
            stateCurrentUser: (store.state && store.state.currentUser) || null,
            computedCurrentUser: currentUser.value,
            loadedUser,
            contestCreator: newContest.created_by
          })

          // Check if user is loaded - if not, we can't check permissions
          if (!loadedUser) {
            console.error('❌ CRITICAL: User not loaded!')
            console.error('Store currentUser:', store.currentUser)
            console.error('Store state currentUser:', store.state && store.state.currentUser)
            console.error('Computed currentUser:', currentUser.value)
            console.error('This means you are not logged in. Please log in again.')
            canDeleteContest.value = false
            checkingAuth.value = false
            return
          } else {
            console.log('✅ User loaded successfully:', loadedUser)
          }

          // Now check delete permission with the loaded user
          // Give it a moment for reactivity to settle
          await new Promise(resolve => setTimeout(resolve, 100))
          checkDeletePermission()

          // If permission check didn't work, try a few more times
          if (!canDeleteContest.value) {
            console.log('⚠️ Delete permission false, retrying permission check...')
            for (let i = 0; i < 3; i++) {
              await new Promise(resolve => setTimeout(resolve, 150))

              // Re-read user to ensure we have latest state
              const userNow = store.currentUser || (store.state && store.state.currentUser) || currentUser.value
              if (userNow) {
                console.log(`Permission check retry ${i + 1}, user:`, userNow)
                checkDeletePermission()

                // If we got a result, break
                if (canDeleteContest.value) {
                  console.log('✅ Delete permission granted!')
                  break
                }
              }
            }
          }

          // Final check and logging
          if (!canDeleteContest.value) {
            const finalUser = store.currentUser || (store.state && store.state.currentUser) || currentUser.value
            console.error('❌ Delete permission still false after all attempts')
            console.error('Final user check:', finalUser)
            console.error('Contest creator:', newContest.created_by)
            if (finalUser) {
              console.error('User username:', finalUser.username)
              console.error('Contest creator (lowercase):', (newContest.created_by || '').toLowerCase())
              console.error('User username (lowercase):', (finalUser.username || '').toLowerCase())
              console.error('Match:', (finalUser.username || '').toLowerCase() === (newContest.created_by || '').toLowerCase())
            }
          } else {
            console.log('✅ Delete permission check successful!')
          }
        } catch (error) {
          console.error('❌ Failed to check auth:', error)
          canDeleteContest.value = false
        } finally {
          checkingAuth.value = false
        }

        // Load submissions if user can view them
        if (canViewSubmissions.value) {
          loadSubmissions()
        } else {
          submissions.value = []
        }
      } else {
        submissions.value = []
        canDeleteContest.value = false
      }
    }, { immediate: true })

    return {
      store, // Expose store for template access
      isAuthenticated,
      currentUser,
      submissions,
      loadingSubmissions,
      deletingContest,
      checkingAuth,
      canViewSubmissions,
      canDeleteContest,
      formatDate,
      formatDateShort,
      formatWordCount,
      getStatusColor,
      loadSubmissions,
      handleSubmitArticle,
      handleDeleteContest,
      forceAuthRefresh,
      showArticlePreview,
      previewArticleUrl,
      previewArticleTitle
    }
  }
}
</script>

<style scoped>
/* Contest Modal Styling with Wikipedia Colors */

/* Modal header - solid color, no gradient */
.modal-header {
  background-color: var(--wiki-primary);
  color: white;
  border-bottom: none;
  padding: 1.25rem 1.5rem;
  transition: background-color 0.2s ease;
}

.modal-title {
  font-weight: 600;
  font-size: 1.5rem;
}

.modal-header .btn-close {
  filter: invert(1) brightness(1.2);
  opacity: 0.9;
  transition: opacity 0.2s ease;
}

.modal-header .btn-close:hover {
  opacity: 1;
}

/* Modal body styling */
.modal-body {
  padding: 1.5rem;
}

.modal-body h6 {
  color: var(--wiki-primary);
  font-weight: 600;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid rgba(0, 102, 153, 0.2);
  transition: color 0.3s ease;
}

[data-theme="dark"] .modal-body h6 {
  color: #ffffff !important; /* White text for better visibility in dark mode */
  border-bottom-color: rgba(93, 184, 230, 0.3);
}

.modal-body p {
  margin-bottom: 0.75rem;
  color: var(--wiki-text);
  transition: color 0.3s ease;
}

.modal-body strong {
  color: var(--wiki-dark);
  font-weight: 600;
  transition: color 0.3s ease;
}

/* Jury section - white text for visibility */
.jury-section p {
  color: #ffffff !important;
}

[data-theme="dark"] .jury-section p {
  color: #ffffff !important;
}

.jury-section h6 {
  color: #ffffff !important;
}

[data-theme="dark"] .jury-section h6 {
  color: #ffffff !important;
}

/* Description section - preserve formatting and line breaks */
.description-section {
  margin-top: 1.5rem;
}

.description-text {
  white-space: pre-line; /* Preserves line breaks and wraps text */
  line-height: 1.6;
  margin-bottom: 0;
  color: var(--wiki-text);
  word-wrap: break-word; /* Break long words if needed */
  transition: color 0.3s ease;
}

[data-theme="dark"] .description-text {
  color: var(--wiki-text);
}

/* Badge styling */
.badge {
  font-weight: 500;
  padding: 0.4em 0.8em;
  font-size: 0.85em;
}

.badge.bg-primary {
  background-color: var(--wiki-primary) !important;
}

.badge.bg-success {
  background-color: var(--wiki-success) !important;
}

.badge.bg-warning {
  background-color: var(--wiki-warning) !important;
  color: #000000 !important; /* Dark text on bright warning background for better readability */
}

[data-theme="dark"] .badge.bg-warning {
  background-color: var(--wiki-warning) !important;
  color: #000000 !important; /* Dark text on bright orange background for maximum contrast */
}

.badge.bg-danger {
  background-color: var(--wiki-danger) !important;
}

/* Table styling */
.table {
  margin-top: 1rem;
}

.table thead th {
  background-color: rgba(0, 102, 153, 0.1);
  color: var(--wiki-primary);
  font-weight: 600;
  border-bottom: 2px solid var(--wiki-primary);
  padding: 0.75rem;
  transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
}

[data-theme="dark"] .table thead th {
  background-color: rgba(93, 184, 230, 0.15);
  border-bottom-color: var(--wiki-primary);
}

.table tbody td {
  padding: 0.75rem;
  vertical-align: middle;
  color: var(--wiki-text);
  transition: color 0.3s ease;
}

.table tbody tr {
  transition: background-color 0.2s ease;
}

.table tbody tr:hover {
  background-color: var(--wiki-hover-bg);
}

/* Link styling in table */
.table a {
  color: var(--wiki-primary);
  font-weight: 500;
  transition: color 0.2s ease;
}

.table a:hover {
  color: var(--wiki-primary-hover);
  text-decoration: underline;
}

/* Article title link - clickable for preview */
.article-title-link {
  cursor: pointer;
  color: var(--wiki-primary);
  font-weight: 500;
  transition: color 0.2s ease;
}

.article-title-link:hover {
  color: var(--wiki-primary-hover);
  text-decoration: underline;
}

/* Button styling */
.btn-outline-primary {
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
  transition: all 0.2s ease;
}

.btn-outline-primary:hover {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.3);
}

.btn-primary {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background-color: var(--wiki-primary-hover);
  border-color: var(--wiki-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.3);
}

.btn-danger {
  background-color: var(--wiki-danger);
  border-color: var(--wiki-danger);
  color: white;
  transition: all 0.2s ease;
}

.btn-danger:hover {
  background-color: var(--wiki-danger-hover);
  border-color: var(--wiki-danger-hover);
  color: white;
  box-shadow: 0 2px 4px rgba(153, 0, 0, 0.2);
}

/* Ensure proper MediaWiki red in dark mode */
[data-theme="dark"] .btn-danger {
  background-color: #990000;
  border-color: #990000;
  color: white;
}

[data-theme="dark"] .btn-danger:hover {
  background-color: #7a0000;
  border-color: #7a0000;
  color: white;
}

.btn-secondary {
  background-color: var(--wiki-text-muted);
  border-color: var(--wiki-text-muted);
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background-color: var(--wiki-text-muted);
  border-color: var(--wiki-text-muted);
}

[data-theme="dark"] .btn-secondary {
  background-color: #5a6268;
  border-color: #5a6268;
}

[data-theme="dark"] .btn-secondary:hover {
  background-color: #6c757d;
  border-color: #6c757d;
}

/* Alert styling */
.alert {
  border-radius: 0.5rem;
  border-left: 4px solid;
  padding: 0.75rem 1rem;
}

.alert-info {
  background-color: rgba(0, 102, 153, 0.1);
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
  transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}

[data-theme="dark"] .alert-info {
  background-color: rgba(93, 184, 230, 0.2);
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
}

.alert-warning {
  background-color: rgba(153, 0, 0, 0.1);
  border-color: var(--wiki-danger);
  color: var(--wiki-danger);
  transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}

[data-theme="dark"] .alert-warning {
  background-color: rgba(230, 128, 128, 0.2);
  border-color: var(--wiki-danger);
  color: var(--wiki-danger);
}

/* Modal footer */
.modal-footer {
  border-top: 1px solid var(--wiki-border);
  padding: 1rem 1.5rem;
  background-color: var(--wiki-modal-bg);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.modal-footer .text-muted {
  font-size: 0.75rem;
  color: var(--wiki-text-muted);
  transition: color 0.3s ease;
}

/* Debug info styling */
.modal-footer .alert {
  margin-bottom: 0.5rem;
  font-size: 0.75rem;
  padding: 0.5rem 0.75rem;
}

/* Spinner styling */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
}

/* Icon styling */
.fas, .fab {
  transition: transform 0.2s ease;
}

.btn:hover .fas,
.btn:hover .fab {
  transform: scale(1.1);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .modal-body {
    padding: 1rem;
  }

  .table {
    font-size: 0.9rem;
  }

  .table thead th,
  .table tbody td {
    padding: 0.5rem;
  }
}
</style>

