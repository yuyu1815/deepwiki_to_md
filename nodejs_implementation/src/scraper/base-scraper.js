/**
 * Base Scraper for DeepWiki to Markdown Converter
 * 
 * This module provides the base abstract class for all scrapers.
 */

const { logger } = require('../utils/logger');

/**
 * Abstract base class for all scrapers.
 * 
 * This class defines the interface that all scrapers must implement.
 */
class BaseScraper {
  /**
   * Initialize the scraper with configuration.
   * 
   * @param {Object} config - Configuration object containing scraper settings
   */
  constructor(config) {
    if (new.target === BaseScraper) {
      throw new TypeError('Cannot instantiate abstract BaseScraper directly');
    }
    
    this.config = config;
    logger.debug(`Initialized ${this.constructor.name} with config: ${config}`);
  }
  
  /**
   * Scrape content from the source.
   * 
   * This method must be implemented by all subclasses.
   * 
   * @returns {Promise<Array<Object>>} List of scraped content items
   */
  async scrape() {
    throw new Error('Method scrape() must be implemented by subclass');
  }
  
  /**
   * Extract navigation links from content.
   * 
   * This method must be implemented by all subclasses.
   * 
   * @param {string} content - Content to extract navigation from
   * @returns {Array<Object>} List of navigation items with title and url
   */
  extractNavigation(content) {
    throw new Error('Method extractNavigation() must be implemented by subclass');
  }
  
  /**
   * Validate if the URL is properly formatted.
   * 
   * @param {string} url - URL to validate
   * @returns {boolean} True if URL is valid, False otherwise
   */
  _validateUrl(url) {
    // Basic validation - can be extended in subclasses
    try {
      new URL(url);
      return url.startsWith('http://') || url.startsWith('https://');
    } catch (e) {
      return false;
    }
  }
  
  /**
   * Clean the scraped content.
   * 
   * @param {string} content - Content to clean
   * @returns {string} Cleaned content
   */
  _cleanContent(content) {
    // Basic cleaning - can be extended in subclasses
    return content.trim();
  }
  
  /**
   * Check if a domain is reachable.
   * 
   * @param {string} domain - Domain to check
   * @param {number} [timeout=5000] - Timeout in milliseconds
   * @returns {Promise<boolean>} True if domain is reachable, False otherwise
   */
  async _isDomainReachable(domain, timeout = 5000) {
    try {
      const url = domain.startsWith('http') ? domain : `https://${domain}`;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);
      
      const response = await fetch(url, { 
        method: 'HEAD',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      logger.debug(`Domain ${domain} is not reachable: ${error.message}`);
      return false;
    }
  }
  
  /**
   * Create a file path for a scraped item.
   * 
   * @param {Object} item - Scraped content item
   * @returns {string} File path
   */
  _createFilePath(item) {
    const path = require('path');
    const sanitizedTitle = this._sanitizeFilename(item.title || 'untitled');
    return path.join(this.config.outputDir, item.library || 'default', `${sanitizedTitle}.md`);
  }
  
  /**
   * Sanitize a string for use as a filename.
   * 
   * @param {string} filename - String to sanitize
   * @returns {string} Sanitized filename
   */
  _sanitizeFilename(filename) {
    // Replace invalid characters with underscores
    const sanitized = filename.replace(/[<>:"/\\|?*]/g, '_');
    
    // Limit the length
    return sanitized.length > 255 ? sanitized.substring(0, 255) : sanitized;
  }
  
  /**
   * Log the scraping progress.
   * 
   * @param {number} current - Current item number
   * @param {number} total - Total number of items
   * @param {string} [message='Processing'] - Progress message
   */
  _logProgress(current, total, message = 'Processing') {
    const percent = Math.round((current / total) * 100);
    logger.info(`${message}: ${current}/${total} (${percent}%)`);
  }
}

module.exports = {
  BaseScraper
};