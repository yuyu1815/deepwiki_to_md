/**
 * Configuration Model for DeepWiki to Markdown Converter
 * 
 * This module provides the configuration data model for the DeepWiki to Markdown converter.
 */

const path = require('path');

/**
 * Configuration settings for the DeepWiki to Markdown converter.
 * 
 * This class stores configuration settings for the scraper, converter, and other components.
 */
class Config {
  /**
   * Create a configuration object.
   * 
   * @param {Object} options - Configuration options
   * @param {string} options.url - URL of the DeepWiki site
   * @param {string} options.libraryName - Name of the library
   * @param {string} [options.outputDir='./output'] - Output directory
   * @param {boolean} [options.verbose=false] - Verbose output
   * @param {number} [options.maxDepth=5] - Maximum depth for recursive scraping
   * @param {number} [options.timeout=30000] - Timeout for requests in milliseconds
   * @param {Object} [options.headers={}] - HTTP headers for requests
   * @param {number} [options.retryCount=3] - Number of retries for failed requests
   * @param {number} [options.retryDelay=2000] - Delay between retries in milliseconds
   */
  constructor(options) {
    // Required settings
    this.url = options.url;
    this.libraryName = options.libraryName;
    
    // Optional settings with defaults
    this.outputDir = options.outputDir || './output';
    this.verbose = options.verbose || false;
    this.maxDepth = options.maxDepth || 5;
    this.timeout = options.timeout || 30000;
    
    // Advanced settings
    this.headers = options.headers || {};
    this.retryCount = options.retryCount || 3;
    this.retryDelay = options.retryDelay || 2000;
    
    // Normalize settings
    this._normalize();
  }
  
  /**
   * Normalize configuration settings.
   * 
   * @private
   */
  _normalize() {
    // Normalize URL (ensure it ends with a slash)
    if (!this.url.endsWith('/')) {
      this.url = `${this.url}/`;
    }
    
    // Normalize output directory (convert to absolute path)
    this.outputDir = path.resolve(this.outputDir);
    
    // Set default User-Agent if not provided
    if (!this.headers['User-Agent']) {
      this.headers['User-Agent'] = 'DeepWiki-to-MD/0.3.2 (https://github.com/yuyu1815/deepwiki_to_md)';
    }
  }
  
  /**
   * Convert the configuration to a plain object.
   * 
   * @returns {Object} Plain object representation of the configuration
   */
  toObject() {
    return {
      url: this.url,
      libraryName: this.libraryName,
      outputDir: this.outputDir,
      verbose: this.verbose,
      maxDepth: this.maxDepth,
      timeout: this.timeout,
      headers: this.headers,
      retryCount: this.retryCount,
      retryDelay: this.retryDelay
    };
  }
  
  /**
   * Create a configuration from a plain object.
   * 
   * @param {Object} obj - Plain object containing configuration settings
   * @returns {Config} Configuration object
   */
  static fromObject(obj) {
    return new Config(obj);
  }
  
  /**
   * Get a string representation of the configuration.
   * 
   * @returns {string} String representation of the configuration
   */
  toString() {
    return `Config(url='${this.url}', libraryName='${this.libraryName}', outputDir='${this.outputDir}')`;
  }
  
  /**
   * Get a configuration value.
   * 
   * @param {string} key - Configuration key
   * @param {*} [defaultValue=null] - Default value if key is not found
   * @returns {*} Configuration value
   */
  get(key, defaultValue = null) {
    return this[key] !== undefined ? this[key] : defaultValue;
  }
  
  /**
   * Set a configuration value.
   * 
   * @param {string} key - Configuration key
   * @param {*} value - Configuration value
   */
  set(key, value) {
    this[key] = value;
    
    // Re-normalize if needed
    if (key === 'url' || key === 'outputDir') {
      this._normalize();
    }
  }
  
  /**
   * Create a new configuration with updated values.
   * 
   * @param {Object} updates - Configuration updates
   * @returns {Config} New configuration object
   */
  update(updates) {
    return new Config({
      ...this.toObject(),
      ...updates
    });
  }
}

module.exports = {
  Config
};