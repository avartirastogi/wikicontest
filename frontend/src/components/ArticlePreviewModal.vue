<template>
  <div class="modal fade" id="articlePreviewModal" tabindex="-1">
    <div class="modal-dialog modal-fullscreen">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-eye me-2"></i>Article Preview: {{ actualArticleTitle }}
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <!-- Loading state -->
          <div v-if="loading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading article...</span>
            </div>
            <p class="mt-3 text-muted">Loading article preview...</p>
          </div>

          <!-- Error state -->
          <div v-else-if="error" class="alert alert-danger">
            <i class="fas fa-exclamation-circle me-2"></i>
            {{ error }}
            <div class="mt-3">
              <a
                :href="articleUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="btn btn-sm btn-outline-primary"
              >
                <i class="fas fa-external-link-alt me-2"></i>Open Article in New Tab
              </a>
            </div>
          </div>

          <!-- MediaWiki content preview -->
          <!-- Content is from MediaWiki API parse action, which sanitizes HTML for safe display -->
          <div v-else-if="mediaWikiContent" class="article-preview-container mediawiki-content">
            <!-- Article metadata card - shows author and creation date -->
            <div v-if="articleMetadata && (articleMetadata.author || articleMetadata.article_created_at)" class="article-metadata-card">
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
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div class="mediawiki-preview" v-html="mediaWikiContent"></div>
          </div>

          <!-- Article preview iframe (for non-MediaWiki pages) -->
          <div v-else class="article-preview-container">
            <iframe
              :src="articleUrl"
              class="article-preview-iframe"
              frameborder="0"
              allowfullscreen
              @load="handleIframeLoad"
              @error="handleIframeError"
            ></iframe>
          </div>
        </div>
        <div class="modal-footer">
          <a
            :href="articleUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="btn btn-outline-primary"
          >
            <i class="fas fa-external-link-alt me-2"></i>Open in New Tab
          </a>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            <i class="fas fa-times me-2"></i>Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onUnmounted } from 'vue'

export default {
  name: 'ArticlePreviewModal',
  props: {
    articleUrl: {
      type: String,
      default: ''
    },
    articleTitle: {
      type: String,
      default: 'Article'
    }
  },
  setup(props) {
    const loading = ref(true)
    const error = ref('')
    const mediaWikiContent = ref('')
    const actualArticleTitle = ref(props.articleTitle || 'Article')
    const articleMetadata = ref(null) // Store article metadata (author, creation date)
    let loadTimeout = null
    const iframeCheckInterval = null

    // Check if URL is a MediaWiki page
    const isMediaWikiUrl = (url) => {
      if (!url) return false
      try {
        const urlObj = new URL(url)
        // Check for common MediaWiki patterns
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

    // Fetch article metadata (author, creation date) from backend API
    // This uses the article-info endpoint which returns comprehensive metadata
    const fetchArticleMetadata = async (articleUrl) => {
      try {
        // Validate that we have a valid URL
        if (!articleUrl) {
          return null
        }

        // Only fetch metadata for MediaWiki URLs
        if (!isMediaWikiUrl(articleUrl)) {
          return null
        }

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
        if (!response.ok) {
          return null
        }

        const data = await response.json()

        // Check for error in response
        if (data.error) {
          return null
        }

        // Return metadata if available
        return {
          author: data.author || null,
          article_created_at: data.article_created_at || null
        }
      } catch (err) {
        // Silently fail - metadata is optional
        console.warn('Error fetching article metadata:', err)
        return null
      }
    }

    // Fetch MediaWiki content via backend proxy API
    // This avoids CORS issues by making the request through our backend server
    const fetchMediaWikiContent = async (articleUrl) => {
      try {
        // Validate that we have a valid URL
        if (!articleUrl) {
          throw new Error('Article URL is required')
        }

        // Use backend proxy endpoint to fetch MediaWiki content
        // The backend makes the request to MediaWiki API, avoiding CORS restrictions
        const response = await fetch(`/api/mediawiki/preview?url=${encodeURIComponent(articleUrl)}`, {
          method: 'GET',
          headers: {
            Accept: 'application/json'
          }
        })

        if (!response.ok) {
          // Try to get error message from response
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

        // Check for error in response
        if (data.error) {
          throw new Error(data.error)
        }

        // Return the content and title from backend response
        // Backend already processes the HTML and makes links absolute
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

    // Load article preview
    const loadPreview = async () => {
      if (!props.articleUrl) return

      loading.value = true
      error.value = ''
      mediaWikiContent.value = ''
      articleMetadata.value = null // Reset metadata when loading new article
      // Reset title to prop value (will be updated if API provides better title)
      actualArticleTitle.value = props.articleTitle || 'Article'

      // Clear any existing timeouts
      if (loadTimeout) {
        clearTimeout(loadTimeout)
      }

      // Check if it's a MediaWiki URL
      if (isMediaWikiUrl(props.articleUrl)) {
        try {
          // Fetch article content and metadata in parallel
          // This improves performance by making both requests simultaneously
          const [contentResult, metadata] = await Promise.all([
            fetchMediaWikiContent(props.articleUrl),
            fetchArticleMetadata(props.articleUrl)
          ])

          // Update content and title
          if (typeof contentResult === 'object' && contentResult.htmlContent) {
            mediaWikiContent.value = contentResult.htmlContent
            // Use actual page title from API if available, otherwise use prop
            if (contentResult.actualPageTitle) {
              actualArticleTitle.value = contentResult.actualPageTitle
            }
          } else {
            // Fallback for old format (string)
            mediaWikiContent.value = contentResult
          }

          // Store metadata for display
          articleMetadata.value = metadata

          loading.value = false
        } catch (err) {
          console.error('MediaWiki API fetch failed:', err)
          // If API fails, show error message with details from backend if available
          loading.value = false
          // Try to extract error message from the error object
          const errorMessage = err.message || err.toString()
          // Show more specific error if available, otherwise show generic message
          if (errorMessage && !errorMessage.includes('Failed to fetch') && !errorMessage.includes('NetworkError')) {
            error.value = `Unable to load article preview: ${errorMessage}. Please use "Open in New Tab" to view the article.`
          } else {
            error.value = 'Unable to load MediaWiki article preview. This may be due to CORS restrictions or the page not being accessible. Please use "Open in New Tab" to view the article.'
          }
        }
      } else {
        // For non-MediaWiki pages, use iframe with timeout
        loadTimeout = setTimeout(() => {
          if (loading.value) {
            loading.value = false
            error.value = 'The article preview is taking too long to load. The page may block embedding. Please use "Open in New Tab" to view the article.'
          }
        }, 10000) // 10 second timeout
      }
    }

    // Handle iframe load event
    const handleIframeLoad = () => {
      if (loadTimeout) {
        clearTimeout(loadTimeout)
        loadTimeout = null
      }
      loading.value = false
      error.value = ''
    }

    // Handle iframe error event
    const handleIframeError = () => {
      if (loadTimeout) {
        clearTimeout(loadTimeout)
        loadTimeout = null
      }
      loading.value = false
      error.value = 'Failed to load article preview. The article may not be accessible or may have security restrictions that prevent embedding.'
    }

    // Format date with full date and time (for article creation date)
    // Shows complete date and time information including time
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

    // Watch for URL changes
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

    // Cleanup on unmount
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
      handleIframeLoad,
      handleIframeError,
      formatDateShort
    }
  }
}
</script>

<style scoped>
/* Article Preview Modal Styling with Wikipedia Colors */

/* Modal header - solid color, no gradient - matches theme */
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

/* Modal body - matches theme - fullscreen */
.modal-body {
  padding: 0;
  background-color: var(--wiki-modal-bg);
  color: var(--wiki-text);
  transition: background-color 0.3s ease, color 0.3s ease;
  min-height: calc(100vh - 140px); /* Full height minus header and footer */
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

/* Article preview container - fullscreen */
.article-preview-container {
  width: 100%;
  height: 100%;
  min-height: calc(100vh - 140px); /* Full height minus header and footer */
  position: relative;
  overflow: hidden; /* Keep hidden for iframe */
  flex: 1;
}

/* MediaWiki content preview - fullscreen with scrolling */
/* When container has both classes, allow vertical scrolling for long content */
.article-preview-container.mediawiki-content {
  overflow-y: auto; /* Allow scrolling for MediaWiki content */
  overflow-x: hidden; /* Prevent horizontal scrolling */
  padding: 1.5rem;
  background-color: white;
  height: 100%;
  flex: 1;
}

/* Article metadata card - displays author and creation date */
.article-metadata-card {
  background-color: #f8f9fa;
  border: 1px solid var(--wiki-border);
  border-radius: 0.5rem;
  padding: 1rem 1.25rem;
  margin-bottom: 1.5rem;
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

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

[data-theme="dark"] .mediawiki-content {
  background-color: #1a1a1a;
}

.mediawiki-preview {
  max-width: 100%;
  color: var(--wiki-text);
  line-height: 1.6;
  /* Ensure all content is visible and can expand */
  min-height: fit-content;
  width: 100%;
}

/* Style MediaWiki content to match Wikipedia appearance */
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

.mediawiki-preview :deep(a) {
  color: var(--wiki-primary);
  text-decoration: none;
}

.mediawiki-preview :deep(a:hover) {
  text-decoration: underline;
}

.mediawiki-preview :deep(img) {
  max-width: 100%;
  height: auto;
  margin: 1rem 0;
}

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

.mediawiki-preview :deep(ul),
.mediawiki-preview :deep(ol) {
  margin: 1rem 0;
  padding-left: 2rem;
}

.mediawiki-preview :deep(li) {
  margin-bottom: 0.5rem;
}

/* Article preview iframe - fullscreen */
.article-preview-iframe {
  width: 100%;
  height: 100%;
  min-height: calc(100vh - 140px); /* Full height minus header and footer */
  border: none;
  background-color: white;
  transition: opacity 0.3s ease;
}

/* Dark mode iframe background */
[data-theme="dark"] .article-preview-iframe {
  background-color: #1a1a1a;
}

/* Loading spinner */
.spinner-border.text-primary {
  color: var(--wiki-primary) !important;
  width: 3rem;
  height: 3rem;
  border-width: 0.3em;
}

/* Alert styling */
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

[data-theme="dark"] .alert-danger {
  background-color: rgba(230, 128, 128, 0.2);
}

/* Button styling */
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

/* Modal footer - matches theme */
.modal-footer {
  border-top: 1px solid var(--wiki-border);
  padding: 1rem 1.5rem;
  background-color: var(--wiki-modal-bg);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

/* Modal content - ensures proper background - fullscreen */
.modal-content {
  background-color: var(--wiki-modal-bg);
  border-color: var(--wiki-border);
  transition: background-color 0.3s ease, border-color 0.3s ease;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Icon styling */
.fas {
  transition: transform 0.2s ease;
}

.btn:hover .fas {
  transform: scale(1.1);
}

/* Text muted */
.text-muted {
  color: var(--wiki-text-muted);
  transition: color 0.3s ease;
}

/* Responsive adjustments - fullscreen on mobile too */
@media (max-width: 768px) {
  .modal-body {
    min-height: calc(100vh - 120px); /* Slightly less on mobile due to smaller header/footer */
  }

  .article-preview-iframe {
    min-height: calc(100vh - 120px);
  }

  .article-preview-container {
    min-height: calc(100vh - 120px);
  }
}
</style>
