<template>
  <!-- Fullscreen modal for article preview with dynamic content loading -->
  <div class="modal fade" id="articlePreviewModal" tabindex="-1">
    <div class="modal-dialog modal-fullscreen">
      <div class="modal-content">
        <!-- Modal header with article title and close button -->
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-eye me-2"></i>Article Preview: {{ actualArticleTitle }}
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <!-- Loading state with spinner -->
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading article...</span>
            </div>
            <p class="mt-3 text-muted">Loading article preview...</p>
          </div>

          <!-- Error state with fallback link to open article externally -->
          <div v-else-if="error" class="alert alert-danger">
            <i class="fas fa-exclamation-circle me-2"></i>
            {{ error }}
            <div class="mt-3">
              <a :href="articleUrl"
target="_blank"
rel="noopener noreferrer"
class="btn btn-sm btn-outline-primary">
                <i class="fas fa-external-link-alt me-2"></i>Open Article in New Tab
              </a>
            </div>
          </div>

          <!-- MediaWiki content preview with article metadata -->
          <div v-else-if="mediaWikiContent" class="article-preview-container mediawiki-content">
            <!-- Article metadata card showing author and creation date -->
            <div v-if="articleMetadata && (articleMetadata.author || articleMetadata.article_created_at)"
              class="article-metadata-card">
              <h6 class="article-metadata-title">Article Author</h6>
              <div class="article-metadata-content">
                <div v-if="articleMetadata.author" class="metadata-item">
                  <i class="fas fa-user me-2"></i>
                  <span>{{ articleMetadata.author }}</span>
                </div>
                <div v-if="articleMetadata.article_created_at" class="metadata-item">
                  <i class="fas fa-calendar me-2"></i>
                  <span>{{ formatDateShort(articleMetadata.article_created_at) }}</span>
                </div>
              </div>
            </div>
            <!-- Render MediaWiki HTML content - sanitized by backend -->
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div class="mediawiki-preview" v-html="mediaWikiContent"></div>
          </div>

          <!-- Iframe fallback for non-MediaWiki pages -->
          <div v-else class="article-preview-container">
            <iframe :src="articleUrl"
class="article-preview-iframe"
frameborder="0"
allowfullscreen
              @load="handleIframeLoad"
@error="handleIframeError"></iframe>
          </div>
        </div>
        <div class="modal-footer">
          <!-- Warning alert if submission already reviewed -->
          <div v-if="canReviewSubmission && isAlreadyReviewed" class="alert alert-warning m-3 flex-grow-1">
            <i class="fas fa-check-circle me-2"></i>
            <strong>This submission has already been reviewed.</strong>
            <div v-if="submission?.review_comment" class="mt-2 small">
              <strong>Comment:</strong> {{ submission.review_comment }}
            </div>
          </div>

          <!-- Review button - disabled if already reviewed -->
          <button class="btn btn-primary"
v-if="canReviewSubmission"
:disabled="isAlreadyReviewed"
            @click="openReviewModal">
            <i class="fas fa-gavel me-2"></i>
            {{ isAlreadyReviewed ? 'Already Reviewed' : 'Review Submission' }}
          </button>

          <!-- External link button to open article in new tab -->
          <a :href="articleUrl"
target="_blank"
rel="noopener noreferrer"
class="btn btn-outline-primary">
            <i class="fas fa-external-link-alt me-2"></i>Open in New Tab
          </a>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            <i class="fas fa-times me-2"></i>Close
          </button>
        </div>
      </div>
    </div>
    <!-- Review submission modal component -->
    <ReviewSubmissionModal :submission-id="submissionId"
:contest-scoring-config="contestScoringConfig"
      @reviewed="onReviewed" />
  </div>
</template>

<script>
import { ref, watch, onUnmounted, computed } from 'vue'
import ReviewSubmissionModal from './ReviewSubmissionModal.vue'
import { showAlert } from '../utils/alerts'

export default {
  name: 'ArticlePreviewModal',
  components: {
    ReviewSubmissionModal
  },

  props: {
    articleUrl: {
      type: String,
      default: ''
    },
    articleTitle: {
      type: String,
      default: 'Article'
    },
    submissionId: {
      type: Number,
      required: true
    },
    submission: {
      type: Object,
      required: true
    },
    canReview: {
      type: Boolean,
      default: false
    },
    contestScoringConfig: {
      type: Object,
      default: null
    }
  },

  emits: ['reviewed'],

  setup(props, { emit }) {
    // Component state
    const loading = ref(true)
    const error = ref('')
    const mediaWikiContent = ref('')
    const actualArticleTitle = ref(props.articleTitle || 'Article')
    const articleMetadata = ref(null)
    // Timeout for iframe loading fallback
    let loadTimeout = null
    const iframeCheckInterval = null
    const canReviewSubmission = computed(() => props.canReview === true)

    // Computed property to check if submission already reviewed
    const isAlreadyReviewed = computed(() => {
      return props.submission?.already_reviewed === true ||
        props.submission?.reviewed_at !== null
    })

    // Check if URL is a MediaWiki site
    const isMediaWikiUrl = (url) => {
      if (!url) return false
      try {
        const urlObj = new URL(url)
        // Check for common MediaWiki URL patterns
        return (
          urlObj.hostname.includes('wiki') ||
          urlObj.pathname.includes('/wiki/') ||
          urlObj.pathname.includes('/w/index.php') ||
          urlObj.searchParams.has('title')
        )
      } catch (e) {
        return false
      }
    }

    // Open review modal for judges to score submission
    const openReviewModal = () => {
      // Verify user has review permission
      if (!canReviewSubmission.value) {
        showAlert('No permission', 'warning')
        return
      }

      // Prevent reviewing if already reviewed
      if (isAlreadyReviewed.value) {
        showAlert('This submission has already been reviewed.')
        return
      }

      if (!props.submissionId) {
        console.error('submissionId missing')
        showAlert('Submission ID not found')
        return
      }

      const modalEl = document.getElementById('reviewSubmissionModal')
      if (!modalEl) {
        console.error('ReviewSubmissionModal DOM not found')
        return
      }

      new window.bootstrap.Modal(modalEl).show()
    }

    // Handle review completion event from child modal
    const onReviewed = (reviewData) => {
      console.log('ArticlePreviewModal received reviewed event:', reviewData)

      // Propagate event to parent component (ContestView)
      emit('reviewed', reviewData)

      // Close the article preview modal after review
      const modalEl = document.getElementById('articlePreviewModal')
      if (modalEl) {
        const modal = window.bootstrap.Modal.getInstance(modalEl)
        if (modal) {
          modal.hide()
        }
      }
    }

    // Fetch article metadata (author and creation date) from backend
    const fetchArticleMetadata = async (articleUrl) => {
      try {
        // Validate that we have a valid URL
        if (!articleUrl) return null
        // Only fetch metadata for MediaWiki URLs
        if (!isMediaWikiUrl(articleUrl)) return null
        // Use backend endpoint to fetch article metadata
        // This includes author and creation date information
        const response = await fetch(`/api/mediawiki/article-info?url=${encodeURIComponent(articleUrl)}`, {
          method: 'GET',
          headers: {
            Accept: 'application/json'
          }
        })
        // If request fails, don't throw error - just return null
        // Metadata is optional, so we don't want to break the preview if metadata fetch fails
        if (!response.ok) return null

        const data = await response.json()
        if (data.error) return null

        return {
          author: data.author || null,
          article_created_at: data.article_created_at || null
        }
      } catch (err) {
        console.warn('Error fetching article metadata:', err)
        return null
      }
    }

    // Fetch MediaWiki content via backend proxy API
    // This avoids CORS issues by making the request through our backend server
    const fetchMediaWikiContent = async (articleUrl) => {
      try {
        if (!articleUrl) {
          throw new Error('Article URL is required')
        }

        // Call backend proxy endpoint to fetch article HTML
        const response = await fetch(`/api/mediawiki/preview?url=${encodeURIComponent(articleUrl)}`, {
          method: 'GET',
          headers: {
            Accept: 'application/json'
          }
        })

        if (!response.ok) {
          let errorMessage = `Request failed: ${response.status} ${response.statusText}`
          try {
            const errorData = await response.json()
            errorMessage = errorData.error || errorMessage
          } catch (e) {
            // If JSON parsing fails, use default message
          }
          throw new Error(errorMessage)
        }

        const data = await response.json()

        if (data.error) {
          throw new Error(data.error)
        }

        if (data.htmlContent) {
          return {
            htmlContent: data.htmlContent,
            actualPageTitle: data.actualPageTitle || null
          }
        } else {
          throw new Error('No content found in API response')
        }
      } catch (err) {
        console.error('Error fetching MediaWiki content:', err)
        throw err
      }
    }

    // Load article preview based on URL type
    const loadPreview = async () => {
      if (!props.articleUrl) return

      // Reset state for new preview
      loading.value = true
      error.value = ''
      mediaWikiContent.value = ''
      articleMetadata.value = null
      actualArticleTitle.value = props.articleTitle || 'Article'

      if (loadTimeout) {
        clearTimeout(loadTimeout)
      }

      // Handle MediaWiki URLs with backend API
      if (isMediaWikiUrl(props.articleUrl)) {
        try {
          // Fetch content and metadata in parallel for better performance
          const [contentResult, metadata] = await Promise.all([
            fetchMediaWikiContent(props.articleUrl),
            fetchArticleMetadata(props.articleUrl)
          ])

          if (typeof contentResult === 'object' && contentResult.htmlContent) {
            mediaWikiContent.value = contentResult.htmlContent
            if (contentResult.actualPageTitle) {
              actualArticleTitle.value = contentResult.actualPageTitle
            }
          } else {
            mediaWikiContent.value = contentResult
          }

          articleMetadata.value = metadata
          loading.value = false
        } catch (err) {
          console.error('MediaWiki API fetch failed:', err)
          loading.value = false
          const errorMessage = err.message || err.toString()
          // Provide user-friendly error messages
          if (errorMessage && !errorMessage.includes('Failed to fetch') && !errorMessage.includes('NetworkError')) {
            error.value = `Unable to load article preview: ${errorMessage}. Please use "Open in New Tab" to view the article.`
          } else {
            error.value = 'Unable to load MediaWiki article preview. Please use "Open in New Tab" to view the article.'
          }
        }
      } else {
        // For non-MediaWiki URLs, use iframe with timeout fallback
        loadTimeout = setTimeout(() => {
          if (loading.value) {
            loading.value = false
            error.value = 'The article preview is taking too long to load. Please use "Open in New Tab" to view the article.'
          }
        }, 10000)
      }
    }

    // Handle successful iframe load
    const handleIframeLoad = () => {
      if (loadTimeout) {
        clearTimeout(loadTimeout)
        loadTimeout = null
      }
      loading.value = false
      error.value = ''
    }

    // Handle iframe loading error
    const handleIframeError = () => {
      if (loadTimeout) {
        clearTimeout(loadTimeout)
        loadTimeout = null
      }
      loading.value = false
      error.value = 'Failed to load article preview.'
    }

    // Format date to IST timezone with readable format
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

    // Watch for URL changes and reload preview
    watch(() => props.articleUrl, (newUrl) => {
      if (newUrl) {
        loadPreview()
      }
    }, { immediate: true })

    // Watch for title changes
    watch(() => props.articleTitle, (newTitle) => {
      if (newTitle) {
        actualArticleTitle.value = newTitle
      }
    }, { immediate: true })

    // Watch for changes in submission review status
    watch(() => props.submission?.already_reviewed, (newValue) => {
      console.log('Watched already_reviewed changed to:', newValue)
    })

    // Cleanup on component unmount
    onUnmounted(() => {
      if (loadTimeout) {
        clearTimeout(loadTimeout)
      }
      if (iframeCheckInterval) {
        clearInterval(iframeCheckInterval)
      }
    })

    return {
      loading,
      error,
      mediaWikiContent,
      actualArticleTitle,
      articleMetadata,
      isAlreadyReviewed,
      handleIframeLoad,
      handleIframeError,
      formatDateShort,
      openReviewModal,
      onReviewed,
      canReviewSubmission
    }
  }
}
</script>

<style scoped>
/* Modal header with brand color background */
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

/* Close button styling for dark header */
.modal-header .btn-close {
  filter: invert(1) brightness(1.2);
  opacity: 0.9;
  transition: opacity 0.2s ease;
}

.modal-header .btn-close:hover {
  opacity: 1;
}

/* Modal body - fullscreen with theme support */
.modal-body {
  padding: 0;
  background-color: var(--wiki-modal-bg);
  color: var(--wiki-text);
  transition: background-color 0.3s ease, color 0.3s ease;
  min-height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

/* Article preview container - fullscreen */
.article-preview-container {
  width: 100%;
  height: 100%;
  min-height: calc(100vh - 140px);
  position: relative;
  overflow: hidden;
  flex: 1;
}

/* MediaWiki content preview with scrolling enabled */
.article-preview-container.mediawiki-content {
  overflow-y: auto;
  overflow-x: hidden;
  padding: 1.5rem;
  background-color: white;
  height: 100%;
  flex: 1;
}

/* Article metadata card displays author and creation date */
.article-metadata-card {
  background-color: #f8f9fa;
  border: 1px solid var(--wiki-border);
  border-radius: 0.5rem;
  padding: 1rem 1.25rem;
  margin-bottom: 1.5rem;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

/* Dark mode metadata card styling */
[data-theme="dark"] .article-metadata-card {
  background-color: #2d2d2d;
  border-color: #555;
}

.article-metadata-title {
  color: var(--wiki-primary);
  font-weight: 600;
  font-size: 1rem;
  margin: 0 0 0.75rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--wiki-primary);
}

.article-metadata-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.metadata-item {
  display: flex;
  align-items: center;
  color: var(--wiki-text);
  font-size: 0.95rem;
}

.metadata-item i {
  color: var(--wiki-text-muted);
  width: 1.25rem;
  text-align: center;
}

/* Dark mode background for MediaWiki content */
[data-theme="dark"] .mediawiki-content {
  background-color: #1a1a1a;
}

/* MediaWiki preview container with proper sizing */
.mediawiki-preview {
  max-width: 100%;
  color: var(--wiki-text);
  line-height: 1.6;
  min-height: fit-content;
  width: 100%;
}

/* Style MediaWiki content headings to match Wikipedia appearance */
.mediawiki-preview :deep(h1),
.mediawiki-preview :deep(h2),
.mediawiki-preview :deep(h3),
.mediawiki-preview :deep(h4),
.mediawiki-preview :deep(h5),
.mediawiki-preview :deep(h6) {
  color: var(--wiki-dark);
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  border-bottom: 1px solid var(--wiki-border);
  padding-bottom: 0.5rem;
}

/* Dark mode heading styles */
[data-theme="dark"] .mediawiki-preview :deep(h1),
[data-theme="dark"] .mediawiki-preview :deep(h2),
[data-theme="dark"] .mediawiki-preview :deep(h3),
[data-theme="dark"] .mediawiki-preview :deep(h4),
[data-theme="dark"] .mediawiki-preview :deep(h5),
[data-theme="dark"] .mediawiki-preview :deep(h6) {
  color: #ffffff;
  border-bottom-color: #555;
}

.mediawiki-preview :deep(p) {
  margin-bottom: 1rem;
  color: var(--wiki-text);
}

/* Link styling within MediaWiki content */
.mediawiki-preview :deep(a) {
  color: var(--wiki-primary);
  text-decoration: none;
}

.mediawiki-preview :deep(a:hover) {
  text-decoration: underline;
}

/* Responsive image sizing */
.mediawiki-preview :deep(img) {
  max-width: 100%;
  height: auto;
  margin: 1rem 0;
}

/* Table styling for MediaWiki content */
.mediawiki-preview :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.mediawiki-preview :deep(table th),
.mediawiki-preview :deep(table td) {
  border: 1px solid var(--wiki-border);
  padding: 0.5rem;
}

.mediawiki-preview :deep(table th) {
  background-color: var(--wiki-hover-bg);
  font-weight: 600;
}

/* List styling for MediaWiki content */
.mediawiki-preview :deep(ul),
.mediawiki-preview :deep(ol) {
  margin: 1rem 0;
  padding-left: 2rem;
}

.mediawiki-preview :deep(li) {
  margin-bottom: 0.5rem;
}

/* Article preview iframe for non-MediaWiki pages */
.article-preview-iframe {
  width: 100%;
  height: 100%;
  min-height: calc(100vh - 140px);
  border: none;
  background-color: white;
  transition: opacity 0.3s ease;
}

/* Dark mode iframe background */
[data-theme="dark"] .article-preview-iframe {
  background-color: #1a1a1a;
}

/* Loading spinner styling */
.spinner-border.text-primary {
  color: var(--wiki-primary) !important;
  width: 3rem;
  height: 3rem;
  border-width: 0.3em;
}

/* Error alert styling with left border accent */
.alert-danger {
  background-color: rgba(153, 0, 0, 0.1);
  border: 1px solid var(--wiki-danger);
  border-left: 4px solid var(--wiki-danger);
  color: var(--wiki-danger);
  border-radius: 0.5rem;
  margin: 1.5rem;
  padding: 1rem;
  transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}

.alert-danger .btn {
  margin-top: 0.5rem;
}

/* Dark mode error alert */
[data-theme="dark"] .alert-danger {
  background-color: rgba(230, 128, 128, 0.2);
}

/* Outline button with hover effects */
.btn-outline-primary {
  border-color: var(--wiki-primary);
  color: var(--wiki-primary);
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-outline-primary:hover {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.3);
}

/* Secondary button styling */
.btn-secondary {
  background-color: var(--wiki-text-muted);
  border-color: var(--wiki-text-muted);
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background-color: var(--wiki-text-muted);
  border-color: var(--wiki-text-muted);
}

/* Dark mode secondary button */
[data-theme="dark"] .btn-secondary {
  background-color: #5a6268;
  border-color: #5a6268;
}

[data-theme="dark"] .btn-secondary:hover {
  background-color: #6c757d;
  border-color: #6c757d;
}

/* Modal footer with theme support */
.modal-footer {
  border-top: 1px solid var(--wiki-border);
  padding: 1rem 1.5rem;
  background-color: var(--wiki-modal-bg);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

/* Modal content fullscreen layout */
.modal-content {
  background-color: var(--wiki-modal-bg);
  border-color: var(--wiki-border);
  transition: background-color 0.3s ease, border-color 0.3s ease;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Icon hover animation */
.fas {
  transition: transform 0.2s ease;
}

.btn:hover .fas {
  transform: scale(1.1);
}

/* Muted text color */
.text-muted {
  color: var(--wiki-text-muted);
  transition: color 0.3s ease;
}

/* Responsive adjustments for mobile devices */
@media (max-width: 768px) {
  .modal-body {
    min-height: calc(100vh - 120px);
  }

  .article-preview-iframe {
    min-height: calc(100vh - 120px);
  }

  .article-preview-container {
    min-height: calc(100vh - 120px);
  }
}
</style>
