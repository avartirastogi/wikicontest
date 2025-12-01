/**
 * API Service for WikiContest Backend Communication
 * 
 * This module handles all HTTP requests to the Flask backend API.
 * It includes:
 * - CSRF token management
 * - Cookie handling for JWT authentication
 * - Error handling
 * - Request/response interceptors
 */

import axios from 'axios'

// Create axios instance with default configuration
const api = axios.create({
  baseURL: '/api',
  withCredentials: true, // Include cookies for JWT authentication
  headers: {
    'Content-Type': 'application/json'
  }
})

// Helper function to get cookie value
function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    return parts.pop().split(';').shift()
  }
  return null
}

// Request interceptor - Add CSRF token to requests
api.interceptors.request.use(
  (config) => {
    // Add CSRF token if available
    const csrfToken = getCookie('csrf_access_token')
    if (csrfToken) {
      config.headers['X-CSRF-TOKEN'] = csrfToken
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors globally
api.interceptors.response.use(
  (response) => {
    // Return response data directly
    return response.data
  },
  (error) => {
    // For 401 errors (unauthorized), don't show alert automatically
    // This is normal for unauthenticated users and shouldn't always trigger an alert
    // The calling code should handle 401 errors appropriately
    if (error.response?.status === 401) {
      const apiError = new Error('Unauthorized')
      apiError.status = 401
      apiError.response = error.response
      // Don't show alert for 401 - let the calling code decide
      // This prevents "Unauthorized" alerts from showing during normal auth checks
      return Promise.reject(apiError)
    }
    
    // Extract error message from response
    const message = error.response?.data?.error || error.message || 'Request failed'
    
    // Create a new error with the message
    const apiError = new Error(message)
    apiError.status = error.response?.status
    apiError.response = error.response
    
    return Promise.reject(apiError)
  }
)

// Export API methods
export default {
  // GET request
  get: (url, config = {}) => api.get(url, config),
  
  // POST request
  post: (url, data = {}, config = {}) => api.post(url, data, config),
  
  // PUT request
  put: (url, data = {}, config = {}) => api.put(url, data, config),
  
  // DELETE request
  delete: (url, config = {}) => api.delete(url, config),
  
  // PATCH request
  patch: (url, data = {}, config = {}) => api.patch(url, data, config)
}

