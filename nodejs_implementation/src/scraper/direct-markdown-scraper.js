/**
 * Direct Markdown Scraper for DeepWiki to Markdown Converter
 * 
 * This module provides functionality for directly scraping Markdown content from DeepWiki sites.
 */

const axios = require('axios');
const { URL } = require('url');
const cheerio = require('cheerio');
const { BaseScraper } = require('./base-scraper');
const { Content } = require('../models/content');
const { logger } = require('../utils/logger');
const { handleRequestError, retryOnException } = require('../utils/error-handler');
const { fixMarkdownLinks } = require('../utils/link-processor');

/**
 * Scraper for directly extracting Markdown content from DeepWiki sites.
 * 
 * This scraper assumes that the DeepWiki site provides Markdown content directly,
 * without the need for HTML-to-Markdown conversion.
 */
class DirectMarkdownScraper extends BaseScraper {
  /**
   * Initialize the DirectMarkdownScraper.
   * 
   * @param {Object} config - Configuration object containing scraper settings
   */
  constructor(config) {
    super(config);
    this.session = axios.create({
      headers: config.headers,
      timeout: config.timeout
    });
    this.visitedUrls = new Set();
  }
  
  /**
   * Scrape Markdown content directly from the DeepWiki site.
   * 
   * @returns {Promise<Array<Object>>} List of scraped content items
   */
  async scrape() {
    const results = [];
    
    // Start with the main URL
    const mainUrl = this.config.url;
    if (!this._validateUrl(mainUrl)) {
      logger.error(`Invalid URL: ${mainUrl}`);
      return results;
    }
    
    // Process the main page
    logger.info(`Scraping content from ${mainUrl}`);
    const content = await this._fetchContent(mainUrl);
    
    if (content) {
      // Process the main content
      const result = {
        url: mainUrl,
        title: this._extractTitle(content),
        content: this._cleanContent(content),
        library: this.config.libraryName
      };
      results.push(result);
      this.visitedUrls.add(mainUrl);
      
      // Extract and process navigation links
      const navItems = this.extractNavigation(content);
      for (const navItem of navItems) {
        if (!this.visitedUrls.has(navItem.url)) {
          // Recursively process navigation items
          const navResults = await this._processNavigationItem(navItem);
          results.push(...navResults);
        }
      }
    }
    
    return results;
  }
  
  /**
   * Process a navigation item by scraping its content.
   * 
   * @param {Object} navItem - Navigation item with title and url
   * @returns {Promise<Array<Object>>} List of scraped content items
   * @private
   */
  async _processNavigationItem(navItem) {
    const results = [];
    const url = navItem.url;
    
    if (this.visitedUrls.has(url)) {
      return results;
    }
    
    logger.debug(`Processing navigation item: ${navItem.title} (${url})`);
    
    // Fetch content for the navigation item
    const content = await this._fetchContent(url);
    if (content) {
      // Process the content
      const result = {
        url: url,
        title: navItem.title || this._extractTitle(content),
        content: this._cleanContent(content),
        library: this.config.libraryName
      };
      results.push(result);
      this.visitedUrls.add(url);
      
      // Extract and process nested navigation links
      const nestedNavItems = this.extractNavigation(content);
      for (const nestedItem of nestedNavItems) {
        if (!this.visitedUrls.has(nestedItem.url)) {
          const nestedResults = await this._processNavigationItem(nestedItem);
          results.push(...nestedResults);
        }
      }
    }
    
    return results;
  }
  
  /**
   * Fetch content from the specified URL.
   * 
   * @param {string} url - URL to fetch content from
   * @returns {Promise<string|null>} Fetched content or null if an error occurred
   * @private
   */
  async _fetchContent(url) {
    try {
      const response = await this._fetchWithRetry(url);
      return response.data;
    } catch (error) {
      handleRequestError(error, url);
      return null;
    }
  }
  
  /**
   * Fetch content with retry logic.
   * 
   * @param {string} url - URL to fetch content from
   * @returns {Promise<Object>} Axios response object
   * @private
   */
  _fetchWithRetry = retryOnException(
    async (url) => {
      return await this.session.get(url);
    },
    {
      maxRetries: this.config.retryCount,
      retryDelay: this.config.retryDelay,
      retryOn: [axios.AxiosError]
    }
  );
  
  /**
   * Extract title from the content.
   * 
   * @param {string} content - Content to extract title from
   * @returns {string} Extracted title or default title
   * @private
   */
  _extractTitle(content) {
    // Try to extract title from the first heading
    const match = content.match(/^#\s+(.+)$/m);
    if (match) {
      return match[1].trim();
    }
    
    // Fallback to a default title
    return 'Untitled Document';
  }
  
  /**
   * Extract navigation links from Markdown content.
   * 
   * @param {string} content - Markdown content to extract navigation from
   * @returns {Array<Object>} List of navigation items with title and url
   */
  extractNavigation(content) {
    const navItems = [];
    
    // Extract Markdown links
    const linkPattern = /\[([^\]]+)\]\(([^)]+)\)/g;
    let match;
    
    while ((match = linkPattern.exec(content)) !== null) {
      const title = match[1].trim();
      const url = match[2].trim();
      
      // Skip empty or anchor links
      if (!url || url.startsWith('#')) {
        continue;
      }
      
      // Handle relative URLs
      let fullUrl = url;
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        fullUrl = new URL(url, this.config.url).href;
      }
      
      navItems.push({
        title: title,
        url: fullUrl
      });
    }
    
    return navItems;
  }
  
  /**
   * Clean the scraped content.
   * 
   * @param {string} content - Content to clean
   * @returns {string} Cleaned content
   */
  _cleanContent(content) {
    // Basic cleaning
    let cleaned = super._cleanContent(content);
    
    // Fix Markdown links
    cleaned = fixMarkdownLinks(cleaned);
    
    return cleaned;
  }
  
  /**
   * Create Content objects from scraped data.
   * 
   * @param {Array<Object>} scrapedItems - List of scraped items
   * @returns {Array<Content>} List of Content objects
   */
  createContentObjects(scrapedItems) {
    return scrapedItems.map(item => new Content({
      title: item.title,
      content: item.content,
      url: item.url,
      library: item.library,
      filePath: this._createFilePath(item)
    }));
  }
}

module.exports = {
  DirectMarkdownScraper
};