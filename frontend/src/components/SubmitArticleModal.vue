<template>
  <div class="modal fade" id="submitArticleModal" tabindex="-1">
    <div class="modal-dialog modal-fullscreen">
      <div class="modal-content">
        <!-- Modal Header -->
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-paper-plane me-2"></i>Submit Article
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>

        <!-- Modal Body -->
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- Info message about URL submission -->
            <div class="alert alert-info mb-3">
              <i class="fas fa-info-circle me-2"></i>
              <strong>Note:</strong> Please submit the URL of your article.
              The system will automatically fetch article information including title and author.
            </div>

            <!-- Template Enforcement Info (if contest has template) -->
            <div v-if="contest && contest.template_link" class="alert alert-warning mb-3">
              <i class="fas fa-file-code me-2"></i>
              <strong>Contest Template:</strong> This contest requires the
              <a :href="contest.template_link"
target="_blank"
rel="noopener noreferrer"
class="alert-link">
                contest template
                <i class="fas fa-external-link-alt ms-1" style="font-size: 0.8em;"></i>
              </a>
              to be present on submitted articles.
              <br/>
              <small class="text-muted d-block mt-1">
                <i class="fas fa-magic me-1"></i>
                If your article doesn't have this template, it will be automatically added during submission.
              </small>
            </div>

            <!-- Category Enforcement Info (if contest has categories) -->
            <div v-if="contest && contest.categories && contest.categories.length > 0" class="alert alert-info mb-3">
              <i class="fas fa-tags me-2"></i>
              <strong>Contest Categories:</strong> This contest requires articles to belong to the following categories:
              <ul class="mb-0 mt-2">
                <li v-for="(categoryUrl, index) in contest.categories" :key="index">
                  <a :href="categoryUrl"
target="_blank"
rel="noopener noreferrer"
class="alert-link">
                    {{ categoryUrl }}
                    <i class="fas fa-external-link-alt ms-1" style="font-size: 0.8em;"></i>
                  </a>
                </li>
              </ul>
              <small class="text-muted d-block mt-2">
                <i class="fas fa-magic me-1"></i>
                If your article doesn't have these categories, they will be automatically added during submission.
              </small>
            </div>

            <!-- Article URL Input Field -->
            <div class="mb-3">
              <label for="articleUrl" class="form-label">
                <i class="fas fa-link me-2 text-primary"></i>Article URL <span class="text-danger">*</span>
              </label>
              <input
                type="url"
                class="form-control"
                id="articleUrl"
                v-model="formData.article_link"
                placeholder="https://en.wikipedia.org/wiki/Article_Title"
                required
                autofocus
              />
              <small class="form-text text-muted">
                Enter the full URL of your MediaWiki article (e.g., Wikipedia, Wikiversity, etc.)
              </small>
            </div>

            <!-- Real-time Validation Checklist -->
            <div class="mb-3" v-if="contest">
              <label class="form-label">
                <i class="fas fa-check-circle me-2 text-primary"></i>Validation Checklist
              </label>
              <div class="card border-primary">
                <div class="card-body">
                  <!-- Display each validation item with status indicator -->
                  <div class="validation-item mb-2" v-for="(item, index) in validationChecklist" :key="index">
                    <div
                      class="d-flex align-items-center"
                      :class="{
                        'text-success': item.checked,
                        'text-danger': !item.checked && item.detail,
                        'text-muted': !item.checked && !item.detail
                      }"
                    >
                      <!-- Icon indicating validation status -->
                      <i
                        :class="
                          item.checked
                            ? 'fas fa-check-circle text-success me-2'
                            : item.detail
                            ? 'fas fa-times-circle text-danger me-2'
                            : 'fas fa-circle text-muted me-2'
                        "
                      ></i>
                      <span class="flex-grow-1">
                        {{ item.label }}
                        <!-- Additional detail about validation result -->
                        <span
                          v-if="item.detail"
                          :class="{
                            'text-danger small ms-2': !item.checked,
                            'text-muted small ms-2': item.checked
                          }"
                        >({{ item.detail }})</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Submission Progress Indicator -->
            <div v-if="submissionProgress.stage !== 'idle'" class="mb-3">
              <div class="card border-primary">
                <div class="card-body">
                  <h6 class="card-title mb-3">
                    <i class="fas fa-tasks me-2"></i>Submission Progress
                  </h6>

                  <!-- Visual Progress Bar -->
                  <div class="progress mb-3" style="height: 25px;">
                    <div
                      class="progress-bar progress-bar-striped progress-bar-animated"
                      :class="progressBarClass"
                      role="progressbar"
                      :style="{ width: progressPercentage + '%' }"
                    >
                      {{ progressPercentage }}%
                    </div>
                  </div>

                  <!-- Detailed Progress Steps -->
                  <div class="progress-steps">
                    <div
                      v-for="(step, index) in progressSteps"
                      :key="index"
                      class="progress-step mb-2"
                      :class="{ 'active': step.active, 'completed': step.completed, 'failed': step.failed }"
                    >
                      <i
                        :class="step.icon"
                        class="me-2"
                        :style="{ color: step.iconColor }"
                      ></i>
                      <span>{{ step.label }}</span>
                      <span v-if="step.detail" class="text-muted ms-2 small">({{ step.detail }})</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Error Display Section -->
            <div v-if="error"
class="alert alert-danger"
role="alert"
style="white-space: pre-wrap; word-wrap: break-word;">
              <strong>Error:</strong><br/>{{ error }}
            </div>
          </form>
        </div>

        <!-- Modal Footer with Action Buttons -->
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            <i class="fas fa-times me-2"></i>Cancel
          </button>
          <button
            type="button"
            class="btn btn-primary"
            @click="handleSubmit"
            :disabled="loading || !canSubmit"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="fas fa-paper-plane me-2"></i>Submit Article
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { showAlert } from '../utils/alerts'
import api from '../services/api'

export default {
  name: 'SubmitArticleModal',
  props: {
    contestId: {
      type: Number,
      required: true
    }
  },
  emits: ['submitted'],
  setup(props, { emit }) {
    // Component state management
    const loading = ref(false)
    const error = ref('')
    const contest = ref(null)

    // Form data model
    const formData = reactive({
      article_link: ''
    })

    // Real-time validation checklist tracking
    const validationChecklist = reactive([
      {
        label: 'Article URL is valid',
        checked: false,
        detail: null
      },
      {
        label: 'Article byte count is within required range',
        checked: false,
        detail: null
      },
      {
        label: 'Article reference count meets requirement',
        checked: false,
        detail: null
      }
    ])

    // Submission progress tracking state
    const submissionProgress = reactive({
      stage: 'idle', // 'idle', 'fetching', 'validating', 'submitting', 'success', 'error'
      articleByteCount: null,
      articleReferenceCount: null,
      contestByteRequirements: null,
      contestReferenceRequirements: null
    })

    // Fetch contest details including byte count and reference count requirements
    const loadContest = async () => {
      try {
        const data = await api.get(`/contest/${props.contestId}`)
        contest.value = data
        submissionProgress.contestByteRequirements = {
          min: data.min_byte_count
        }
        // Ensure min_reference_count is properly converted to number
        // Handle null, undefined, or string values
        const minRefCount = data.min_reference_count != null ? Number(data.min_reference_count) : 0
        submissionProgress.contestReferenceRequirements = {
          min: isNaN(minRefCount) ? 0 : minRefCount
        }
      } catch (err) {
        console.error('Error loading contest:', err)
      }
    }

    // Initialize contest data on component mount
    onMounted(() => {
      loadContest()
    })

    // Debounce timer reference for URL validation
    let validationTimer = null

    // Watch for URL changes and trigger automatic validation
    watch(
      () => formData.article_link,
      (newUrl) => {
        // Clear any existing timer
        if (validationTimer) {
          clearTimeout(validationTimer)
        }

        // Reset checklist when URL is cleared
        if (!newUrl || !newUrl.trim()) {
          validationChecklist[0].checked = false
          validationChecklist[0].detail = null
          validationChecklist[1].checked = false
          validationChecklist[1].detail = null
          validationChecklist[2].checked = false
          validationChecklist[2].detail = null
          return
        }

        // Debounce validation to prevent too many API calls while typing
        validationTimer = setTimeout(async () => {
          // Only validate if URL looks like a valid URL
          if (newUrl.trim().startsWith('http://') || newUrl.trim().startsWith('https://')) {
            // Ensure contest is loaded before validating
            if (!contest.value) {
              await loadContest()
            }
            // Validate silently without showing progress indicators
            await validateArticle(false)
          } else {
            // URL format is invalid
            validationChecklist[0].checked = false
            validationChecklist[0].detail = 'URL must start with http:// or https://'
            validationChecklist[1].checked = false
            validationChecklist[1].detail = null
          }
        }, 800)
      }
    )

    // Computed progress steps based on current submission stage
    const progressSteps = computed(() => {
      const steps = [
        {
          label: 'Fetching article information',
          icon: 'fas fa-spinner fa-spin',
          iconColor: '#006699',
          active: submissionProgress.stage === 'fetching',
          completed: ['validating', 'submitting', 'success'].includes(submissionProgress.stage),
          failed: false,
          detail: submissionProgress.stage === 'fetching' ? 'Getting article details from MediaWiki...' : null
        },
        {
          label: 'Checking byte count requirements',
          icon: 'fas fa-check-circle',
          iconColor: '#28a745',
          active: submissionProgress.stage === 'validating',
          completed: ['submitting', 'success'].includes(submissionProgress.stage),
          failed: submissionProgress.stage === 'error' && error.value.includes('byte count'),
          detail: getByteCountDetail()
        },
        {
          label: 'Submitting article',
          icon: 'fas fa-paper-plane',
          iconColor: '#006699',
          active: submissionProgress.stage === 'submitting',
          completed: submissionProgress.stage === 'success',
          failed: submissionProgress.stage === 'error' && !error.value.includes('byte count'),
          detail: submissionProgress.stage === 'submitting' ? 'Creating submission...' : null
        }
      ]
      return steps
    })

    // Generate human-readable byte count detail text
    const getByteCountDetail = () => {
      if (submissionProgress.stage === 'idle' || submissionProgress.stage === 'fetching') {
        return null
      }

      const req = submissionProgress.contestByteRequirements
      const count = submissionProgress.articleByteCount

      if (count !== null && req && req.min !== null && req.min !== undefined) {
        const minText = `min: ${req.min.toLocaleString()}`
        return `Article: ${count.toLocaleString()} bytes | Required: ${minText}`
      }

      return 'Checking...'
    }

    // Calculate progress percentage based on current stage
    const progressPercentage = computed(() => {
      switch (submissionProgress.stage) {
        case 'fetching':
          return 33
        case 'validating':
          return 66
        case 'submitting':
          return 90
        case 'success':
          return 100
        case 'error':
          return 0
        default:
          return 0
      }
    })

    // Determine progress bar color class based on stage
    const progressBarClass = computed(() => {
      if (submissionProgress.stage === 'error') {
        return 'bg-danger'
      }
      if (submissionProgress.stage === 'success') {
        return 'bg-success'
      }
      return 'bg-primary'
    })

    // Check if all validations have passed to enable submit button
    const canSubmit = computed(() => {
      // Both URL and byte count validations must pass
      return validationChecklist[0].checked && validationChecklist[1].checked
    })

    // Validate article URL and byte count requirements
    const validateArticle = async (showProgress = true) => {
      // Reset checklist before validation
      validationChecklist[0].checked = false
      validationChecklist[0].detail = null
      validationChecklist[1].checked = false
      validationChecklist[1].detail = null
      validationChecklist[2].checked = false
      validationChecklist[2].detail = null

      // Validate URL format
      if (!formData.article_link.trim()) {
        validationChecklist[0].checked = false
        validationChecklist[0].detail = 'URL is required'
        return false
      }
      if (!formData.article_link.startsWith('http://') && !formData.article_link.startsWith('https://')) {
        validationChecklist[0].checked = false
        validationChecklist[0].detail = 'URL must start with http:// or https://'
        return false
      }

      // URL format is valid
      validationChecklist[0].checked = true
      validationChecklist[0].detail = 'Valid URL format'

      // Fetch article info and validate byte count
      try {
        if (showProgress) {
          submissionProgress.stage = 'fetching'
        }
        // Make API call to fetch article information
        const articleInfo = await api.get('/mediawiki/article-info', {
          params: { url: formData.article_link.trim() }
        })

        // Check if API returned an error in the response
        if (articleInfo.error) {
          throw new Error(articleInfo.error)
        }

        // Extract byte count from article info
        const articleByteCount = articleInfo.word_count || articleInfo.size || null
        submissionProgress.articleByteCount = articleByteCount

        // Extract reference count from article info
        const articleReferenceCount = articleInfo.reference_count || null
        submissionProgress.articleReferenceCount = articleReferenceCount

        // Ensure contest is loaded before validating requirements
        // Check both byte and reference requirements to ensure all data is loaded
        if (
          !contest.value ||
          !submissionProgress.contestByteRequirements ||
          !submissionProgress.contestReferenceRequirements
        ) {
          await loadContest()
        }

        const byteReq = submissionProgress.contestByteRequirements
        const refReq = submissionProgress.contestReferenceRequirements

        // Validate byte count
        // Cannot validate if article byte count is unavailable
        if (articleByteCount === null) {
          validationChecklist[1].checked = false
          validationChecklist[1].detail = 'Could not determine article size'
          return false
        }

        // Validate byte count against contest requirements
        if (byteReq && byteReq.min !== null && byteReq.min !== undefined) {
          // Check minimum byte count requirement
          if (articleByteCount < byteReq.min) {
            validationChecklist[1].checked = false
            validationChecklist[1].detail = `Article byte count (${articleByteCount.toLocaleString()}) is below the minimum required (${byteReq.min.toLocaleString()} bytes)`
            return false
          }

          // Byte count meets the requirement
          validationChecklist[1].checked = true
          validationChecklist[1].detail = `${articleByteCount.toLocaleString()} bytes (Required: min: ${byteReq.min.toLocaleString()})`
        } else {
          // Contest should always have min_byte_count
          validationChecklist[1].checked = false
          validationChecklist[1].detail = 'Contest byte count requirement not found'
          return false
        }

        // Validate reference count (only if contest requires it)
        // Check if refReq exists and has a valid min value > 0
        const minRefRequired = refReq && refReq.min != null && Number(refReq.min) > 0
        if (minRefRequired) {
          // Contest requires a minimum reference count
          // Convert to number to ensure proper comparison
          const minRefCount = Number(refReq.min)

          if (articleReferenceCount === null || articleReferenceCount === undefined) {
            validationChecklist[2].checked = false
            validationChecklist[2].detail = 'Could not determine article reference count'
            return false
          }

          // Convert article reference count to number for comparison
          const articleRefCountNum = Number(articleReferenceCount)

          // Check minimum reference count requirement
          if (isNaN(articleRefCountNum) || articleRefCountNum < minRefCount) {
            validationChecklist[2].checked = false
            validationChecklist[2].detail = `Article reference count (${articleRefCountNum}) is below the minimum required (${minRefCount} references)`
            return false
          }

          // Reference count meets the requirement
          validationChecklist[2].checked = true
          validationChecklist[2].detail = `${articleRefCountNum} references (Required: min: ${minRefCount})`
        } else {
          // No reference count requirement (min_reference_count = 0 or not set)
          validationChecklist[2].checked = true
          validationChecklist[2].detail = 'No reference count requirement'
        }

        // All validations passed
        return true
      } catch (err) {
        validationChecklist[1].checked = false
        if (showProgress) {
          submissionProgress.stage = 'error'
        }

        // Build user-friendly error message
        let errorMsg = 'Failed to fetch article information'

        // Extract error details from response
        const status = err.status || err.response?.status
        const errorData = err.response?.data || {}
        const errorMessage = errorData.error || err.message || ''

        // Log error for debugging
        console.error('Article validation error:', {
          status,
          message: errorMessage,
          error: err
        })

        // Provide specific error messages based on error type
        if (status === 404) {
          if (errorMessage.toLowerCase().includes('article not found') ||
              errorMessage.toLowerCase().includes('page not found')) {
            errorMsg = 'Article not found - please check the URL'
          } else {
            errorMsg = 'Article not found or endpoint unavailable'
          }
        } else if (status === 0 || err.message?.includes('Network Error') ||
                   err.message?.includes('Failed to fetch') ||
                   err.message?.includes('Network request failed')) {
          errorMsg = 'Network error - please check your connection'
        } else if (status === 502 || status === 503 || status === 504) {
          errorMsg = 'Server error - please try again later'
        } else if (errorMessage) {
          errorMsg = errorMessage
        } else if (err.message) {
          errorMsg = err.message
        }

        validationChecklist[1].detail = errorMsg
        return false
      }
    }

    // Handle article submission
    const handleSubmit = async () => {
      // Clear any previous errors
      error.value = ''

      // Check if validation has already passed to avoid duplicate API calls
      const alreadyValidated = canSubmit.value

      if (!alreadyValidated) {
        // Validation hasn't passed yet
        const failedChecks = validationChecklist.filter(item => !item.checked)
        if (failedChecks.length > 0) {
          error.value = `Validation failed: ${failedChecks.map(item => item.label).join(', ')}`
        } else {
          error.value = 'Please wait for validation to complete or check the requirements.'
        }
        return
      }

      // Set loading state immediately to prevent multiple clicks
      loading.value = true
      submissionProgress.stage = 'submitting'

      try {
        // Submit the article since validation already passed
        await api.post(`/contest/${props.contestId}/submit`, {
          article_link: formData.article_link.trim()
        })

        // Update stage to success
        submissionProgress.stage = 'success'

        // Reset loading state
        loading.value = false

        showAlert('Article submitted successfully!', 'success')

        // Emit event to parent to refresh data
        emit('submitted')

        // Close modal and reset form
        const modalElement = document.getElementById('submitArticleModal')
        const modal = bootstrap.Modal.getInstance(modalElement)
        if (modal) {
          modal.hide()
        }

        // Reset form state
        formData.article_link = ''
        submissionProgress.stage = 'idle'
        submissionProgress.articleByteCount = null
        validationChecklist[0].checked = false
        validationChecklist[0].detail = null
        validationChecklist[1].checked = false
        validationChecklist[1].detail = null
        error.value = ''
      } catch (err) {
        submissionProgress.stage = 'error'

        // Extract error details from response
        const errorData = err.response?.data || {}
        const errorMessage = errorData.error || err.message || 'Failed to submit article'

        // Build detailed error message
        let detailedError = errorMessage
        if (errorData.details) {
          detailedError += `\n\nDetails: ${errorData.details}`
        }
        if (errorData.error_type) {
          detailedError += `\n\nError Type: ${errorData.error_type}`
        }
        if (errorData.traceback && process.env.NODE_ENV === 'development') {
          detailedError += `\n\nTraceback:\n${errorData.traceback}`
        }

        // Log full error for debugging
        console.error('Submission error:', {
          status: err.response?.status,
          error: errorData,
          fullError: err
        })

        error.value = detailedError

        // Update validation checklist if error is about byte count
        if (errorMessage.toLowerCase().includes('byte count')) {
          validationChecklist[1].checked = false
          validationChecklist[1].detail = errorMessage
          // Try to extract byte count from error message
          const byteMatch = errorMessage.match(/(\d+)\s*bytes?/i)
          if (byteMatch) {
            submissionProgress.articleByteCount = parseInt(byteMatch[1])
          }
        }

        showAlert(error.value, 'danger')
      } finally {
        loading.value = false
      }
    }

    return {
      formData,
      loading,
      error,
      handleSubmit,
      submissionProgress,
      progressSteps,
      progressPercentage,
      progressBarClass,
      contest,
      validationChecklist,
      canSubmit
    }
  }
}
</script>

<style scoped>
/* Submit Article Modal Styling with Wikipedia Colors */

/* Modal header styling */
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
  color: white;
}

.modal-header .btn-close {
  filter: invert(1) brightness(1.2);
  opacity: 0.9;
  transition: opacity 0.2s ease;
}

.modal-header .btn-close:hover {
  opacity: 1;
}

/* Form label styling */
.form-label {
  color: var(--wiki-dark);
  font-weight: 500;
  margin-bottom: 0.5rem;
  transition: color 0.3s ease;
}

.form-label .text-primary {
  color: var(--wiki-primary) !important;
}

/* Required field indicator styling */
.form-label .text-danger {
  color: var(--wiki-danger) !important;
}

/* Dark mode required field styling */
[data-theme="dark"] .form-label .text-danger {
  color: #990000 !important;
}

/* Form control input styling */
.form-control {
  border-color: var(--wiki-input-border);
  background-color: var(--wiki-input-bg);
  color: var(--wiki-text);
  transition: all 0.2s ease;
}

/* Input focus state styling */
.form-control:focus {
  border-color: var(--wiki-primary);
  box-shadow: 0 0 0 0.2rem rgba(0, 102, 153, 0.25);
  background-color: var(--wiki-input-bg);
  color: var(--wiki-text);
}

/* Dark mode input focus styling */
[data-theme="dark"] .form-control:focus {
  box-shadow: 0 0 0 0.2rem rgba(93, 184, 230, 0.3);
}

/* Error alert styling */
.alert-danger {
  background-color: rgba(153, 0, 0, 0.1);
  border: 1px solid var(--wiki-danger);
  border-left: 4px solid var(--wiki-danger);
  color: var(--wiki-danger);
  border-radius: 0.5rem;
  transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}

/* Dark mode error alert styling */
[data-theme="dark"] .alert-danger {
  background-color: rgba(230, 128, 128, 0.2);
}

/* Primary button styling */
.btn-primary {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  font-weight: 500;
  transition: all 0.2s ease;
}

/* Primary button hover state */
.btn-primary:hover {
  background-color: var(--wiki-primary-hover);
  border-color: var(--wiki-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.3);
}

/* Disabled button styling */
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Secondary button styling */
.btn-secondary {
  background-color: var(--wiki-text-muted);
  border-color: var(--wiki-text-muted);
  transition: all 0.2s ease;
}

/* Secondary button hover state */
.btn-secondary:hover {
  background-color: var(--wiki-text-muted);
  border-color: var(--wiki-text-muted);
}

/* Dark mode secondary button styling */
[data-theme="dark"] .btn-secondary {
  background-color: #5a6268;
  border-color: #5a6268;
}

/* Dark mode secondary button hover state */
[data-theme="dark"] .btn-secondary:hover {
  background-color: #6c757d;
  border-color: #6c757d;
}

/* Modal body styling */
.modal-body {
  padding: 1.5rem;
  background-color: var(--wiki-modal-bg);
  color: var(--wiki-text);
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Modal footer styling */
.modal-footer {
  border-top: 1px solid var(--wiki-border);
  padding: 1rem 1.5rem;
  background-color: var(--wiki-modal-bg);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

/* Modal content container styling */
.modal-content {
  background-color: var(--wiki-modal-bg);
  border-color: var(--wiki-border);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

/* Icon animation on interaction */
.fas {
  transition: transform 0.2s ease;
}

.btn:hover .fas {
  transform: scale(1.1);
}

/* Loading spinner styling */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
  border-color: currentColor;
  border-right-color: transparent;
}

/* Progress steps container styling */
.progress-steps {
  font-size: 0.9rem;
}

/* Individual progress step styling */
.progress-step {
  padding: 0.5rem;
  border-radius: 0.25rem;
  transition: all 0.3s ease;
}

/* Active progress step highlighting */
.progress-step.active {
  background-color: rgba(0, 102, 153, 0.1);
  font-weight: 500;
}

/* Completed step styling */
.progress-step.completed {
  color: #28a745;
}

.progress-step.completed .fas {
  color: #28a745 !important;
}

/* Failed step styling */
.progress-step.failed {
  color: #dc3545;
}

.progress-step.failed .fas {
  color: #dc3545 !important;
}

/* Progress step icon styling */
.progress-step .fas {
  transition: color 0.3s ease;
}

/* Progress bar container styling */
.progress {
  background-color: rgba(0, 102, 153, 0.1);
  border-radius: 0.5rem;
  overflow: hidden;
}

/* Progress bar fill styling */
.progress-bar {
  transition: width 0.6s ease;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Progress card border styling */
.card.border-primary {
  border-color: var(--wiki-primary) !important;
  background-color: var(--wiki-card-bg);
  transition: background-color 0.3s ease;
}

/* Card title styling */
.card-title {
  color: var(--wiki-text);
  font-weight: 600;
}

/* Dark mode active progress step styling */
[data-theme="dark"] .progress-step.active {
  background-color: rgba(93, 184, 230, 0.15);
}

/* Dark mode progress bar styling */
[data-theme="dark"] .progress {
  background-color: rgba(93, 184, 230, 0.1);
}

/* Validation checklist item styling */
.form-check {
  padding: 0.75rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s ease;
}

/* Checklist item hover effect */
.form-check:hover {
  background-color: rgba(0, 102, 153, 0.05);
}

/* Dark mode checklist hover effect */
[data-theme="dark"] .form-check:hover {
  background-color: rgba(93, 184, 230, 0.1);
}

/* Checklist input styling */
.form-check-input {
  margin-top: 0.35rem;
  cursor: not-allowed;
}

/* Checklist label styling */
.form-check-label {
  cursor: default;
  display: flex;
  align-items: center;
  font-weight: 500;
  transition: color 0.2s ease;
}

/* Success state label styling */
.form-check-label.text-success {
  color: #28a745 !important;
}

/* Muted state label styling */
.form-check-label.text-muted {
  color: var(--wiki-text-muted) !important;
}

/* Checklist icon styling */
.form-check-label .fas {
  font-size: 1rem;
  transition: transform 0.2s ease;
}

/* Success icon color styling */
.form-check-label.text-success .fas {
  color: #28a745 !important;
}

/* Card body content styling */
.card.border-primary .card-body {
  padding: 1rem;
  background-color: var(--wiki-card-bg);
  transition: background-color 0.3s ease;
}
</style>
