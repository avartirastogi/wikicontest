/**
 * Alert Utility Functions
 *
 * This module provides a simple alert system for showing notifications.
 * It manages a global list of alerts that are displayed in AlertContainer.
 */

import { reactive } from 'vue'

// Global reactive state for all active alerts
const alertState = reactive({
  alerts: []
})

/**
 * Show an alert message
 * @param {string} message - The message to display
 * @param {string} type - Alert type: 'success', 'danger', 'warning', 'info'
 */
export function showAlert(message, type = 'info') {
  // Create unique alert with timestamp and random number to prevent collisions
  const alert = {
    id: Date.now() + Math.random(),
    message,
    type
  }

  alertState.alerts.push(alert)

  // Auto-dismiss alert after 5 seconds
  setTimeout(() => {
    removeAlert(alert.id)
  }, 5000)
}

/**
 * Remove an alert by ID
 * @param {number} id - The alert ID to remove
 */
export function removeAlert(id) {
  const index = alertState.alerts.findIndex(a => a.id === id)
  if (index > -1) {
    alertState.alerts.splice(index, 1)
  }
}

/**
 * Get the alert state (for AlertContainer component)
 */
export function getAlertState() {
  return alertState
}
