/**
 * Utility function to convert text to URL-friendly slug format
 * 
 * This function converts contest names to URL-friendly slugs:
 * - Converts to lowercase
 * - Replaces spaces with hyphens
 * - Removes special characters
 * - Handles multiple spaces/hyphens
 * 
 * @param {string} text - Text to convert to slug
 * @returns {string} - URL-friendly slug
 * 
 * Example:
 *   slugify("Price Sanford") => "price-sanford"
 *   slugify("Contest 1!") => "contest-1"
 */
export function slugify(text) {
  if (!text) return ''
  
  return text
    .toString()
    .toLowerCase()
    .trim()
    // Replace spaces with hyphens
    .replace(/\s+/g, '-')
    // Remove special characters except hyphens
    .replace(/[^\w\-]+/g, '')
    // Replace multiple hyphens with single hyphen
    .replace(/\-\-+/g, '-')
    // Remove leading/trailing hyphens
    .replace(/^-+/, '')
    .replace(/-+$/, '')
}

/**
 * Convert slug back to readable format (for display)
 * 
 * @param {string} slug - Slug to convert back
 * @returns {string} - Readable text with spaces
 */
export function unslugify(slug) {
  if (!slug) return ''
  
  return slug
    .toString()
    .replace(/-/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase())
}

