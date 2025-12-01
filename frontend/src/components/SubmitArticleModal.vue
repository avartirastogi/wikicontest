<template>
  <div class="modal fade" id="submitArticleModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header bg-primary text-white">
          <h5 class="modal-title">
            <i class="fas fa-paper-plane me-2"></i>Submit Article
          </h5>
          <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label for="articleTitle" class="form-label">
                <i class="fas fa-heading me-2 text-primary"></i>Article Title <span class="text-danger">*</span>
              </label>
              <input 
                type="text" 
                class="form-control" 
                id="articleTitle" 
                v-model="formData.article_title"
                placeholder="Enter the title of your article"
                required
                autofocus
              >
            </div>
            
            <div class="mb-3">
              <label for="articleUrl" class="form-label">
                <i class="fas fa-link me-2 text-primary"></i>Article URL <span class="text-danger">*</span>
              </label>
              <input 
                type="url" 
                class="form-control" 
                id="articleUrl" 
                v-model="formData.article_link"
                placeholder="https://example.com/article"
                required
              >
            </div>
            
            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            <i class="fas fa-times me-2"></i>Cancel
          </button>
          <button 
            type="button" 
            class="btn btn-primary" 
            @click="handleSubmit"
            :disabled="loading"
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
import { ref, reactive } from 'vue'
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
    const loading = ref(false)
    const error = ref('')
    
    const formData = reactive({
      article_title: '',
      article_link: ''
    })

    const handleSubmit = async () => {
      error.value = ''
      
      // Validation
      if (!formData.article_title.trim()) {
        error.value = 'Please enter an article title'
        return
      }
      if (!formData.article_link.trim()) {
        error.value = 'Please enter an article URL'
        return
      }
      if (!formData.article_link.startsWith('http://') && !formData.article_link.startsWith('https://')) {
        error.value = 'Article URL must start with http:// or https://'
        return
      }

      loading.value = true
      try {
        await api.post(`/contest/${props.contestId}/submit`, {
          article_title: formData.article_title.trim(),
          article_link: formData.article_link.trim()
        })

        showAlert('Article submitted successfully!', 'success')
        emit('submitted')
        
        // Close modal
        const modalElement = document.getElementById('submitArticleModal')
        const modal = bootstrap.Modal.getInstance(modalElement)
        if (modal) {
          modal.hide()
        }
        
        // Reset form
        formData.article_title = ''
        formData.article_link = ''
      } catch (err) {
        error.value = 'Failed to submit article: ' + err.message
        showAlert(error.value, 'danger')
      } finally {
        loading.value = false
      }
    }

    return {
      formData,
      loading,
      error,
      handleSubmit
    }
  }
}
</script>

<style scoped>
/* Submit Article Modal Styling with Wikipedia Colors */

/* Modal header */
.modal-header {
  background: linear-gradient(135deg, var(--wiki-primary) 0%, var(--wiki-primary-hover) 100%);
  color: white;
  border-bottom: none;
  padding: 1.25rem 1.5rem;
  transition: background 0.3s ease;
}

.modal-title {
  font-weight: 600;
  font-size: 1.5rem;
}

.modal-header .btn-close {
  filter: invert(1) brightness(1.2);
  opacity: 0.9;
}

/* Form styling */
.form-label {
  color: var(--wiki-dark);
  font-weight: 500;
  margin-bottom: 0.5rem;
  transition: color 0.3s ease;
}

.form-label .text-primary {
  color: var(--wiki-primary) !important;
}

.form-label .text-danger {
  color: var(--wiki-danger) !important;
}

.form-control {
  border-color: var(--wiki-input-border);
  background-color: var(--wiki-input-bg);
  color: var(--wiki-text);
  transition: all 0.2s ease;
}

.form-control:focus {
  border-color: var(--wiki-primary);
  box-shadow: 0 0 0 0.2rem rgba(0, 102, 153, 0.25);
  background-color: var(--wiki-input-bg);
  color: var(--wiki-text);
}

[data-theme="dark"] .form-control:focus {
  box-shadow: 0 0 0 0.2rem rgba(93, 184, 230, 0.3);
}

/* Alert styling */
.alert-danger {
  background-color: rgba(153, 0, 0, 0.1);
  border: 1px solid var(--wiki-danger);
  border-left: 4px solid var(--wiki-danger);
  color: var(--wiki-danger);
  border-radius: 0.5rem;
  transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease;
}

[data-theme="dark"] .alert-danger {
  background-color: rgba(230, 128, 128, 0.2);
}

/* Button styling */
.btn-primary {
  background-color: var(--wiki-primary);
  border-color: var(--wiki-primary);
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background-color: var(--wiki-primary-hover);
  border-color: var(--wiki-primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 102, 153, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

/* Modal footer */
.modal-footer {
  border-top: 1px solid var(--wiki-border);
  padding: 1rem 1.5rem;
  background-color: var(--wiki-modal-bg);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

/* Icon styling */
.fas {
  transition: transform 0.2s ease;
}

.btn:hover .fas {
  transform: scale(1.1);
}

/* Spinner */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.15em;
  border-color: currentColor;
  border-right-color: transparent;
}
</style>

