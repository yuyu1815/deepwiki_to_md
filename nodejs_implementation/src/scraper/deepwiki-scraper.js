/**
 * DeepWiki Scraper for DeepWiki to Markdown Converter
 * 
 * This module provides the main scraper for DeepWiki sites, coordinating the scraping process.
 */

const path = require('path');
const fs = require('fs');
const { BaseScraper } = require('./base-scraper');
const { DirectMarkdownScraper } = require('./direct-markdown-scraper');
const { Content } = require('../models/content');
const { logger } = require('../utils/logger');
const { saveMarkdownFile } = require('../utils/file-io');
const { fixMarkdownLinks, processMarkdownLinks } = require('../utils/link-processor');

/**
 * Main scraper for DeepWiki sites.
 * 
 * This class coordinates the scraping process, delegating to specialized scrapers
 * and handling the saving of scraped content.
 */
class DeepwikiScraper extends BaseScraper {
  /**
   * Initialize the DeepwikiScraper.
   * 
   * @param {Object} config - Configuration object containing scraper settings
   */
  constructor(config) {
    super(config);
    this.directScraper = new DirectMarkdownScraper(config);
  }
  
  /**
   * Scrape content from the DeepWiki site.
   * 
   * This method coordinates the scraping process and saves the results.
   * 
   * @returns {Promise<Array<Object>>} List of scraped content items
   */
  async scrape() {
    logger.info(`Starting scraping process for ${this.config.libraryName}`);
    
    // Use the direct markdown scraper to get content
    const results = await this.directScraper.scrape();
    
    // Process and save the results
    const processedResults = [];
    
    for (let i = 0; i < results.length; i++) {
      const item = results[i];
      
      // Log progress
      this._logProgress(i + 1, results.length, 'Processing');
      
      // Fix markdown links
      item.content = fixMarkdownLinks(item.content);
      
      // Save the content to a file
      const outputPath = this._getOutputPath(item);
      const success = saveMarkdownFile(outputPath, item.content);
      
      if (success) {
        // Add the file path to the result
        item.filePath = outputPath;
        processedResults.push(item);
        
        logger.info(`Saved ${item.title} to ${outputPath}`);
      } else {
        logger.error(`Failed to save ${item.title}`);
      }
    }
    
    // Process all markdown links in the output directory
    const outputDir = path.join(this.config.outputDir, this.config.libraryName);
    processMarkdownLinks(outputDir);
    
    logger.info(`Scraping completed. Processed ${processedResults.length} documents.`);
    return processedResults;
  }
  
  /**
   * Extract navigation links from content.
   * 
   * This method delegates to the direct markdown scraper.
   * 
   * @param {string} content - Content to extract navigation from
   * @returns {Array<Object>} List of navigation items with title and url
   */
  extractNavigation(content) {
    return this.directScraper.extractNavigation(content);
  }
  
  /**
   * Get the output file path for a scraped item.
   * 
   * @param {Object} item - Scraped content item
   * @returns {string} Output file path
   * @private
   */
  _getOutputPath(item) {
    // Create the output directory if it doesn't exist
    const libraryDir = path.join(this.config.outputDir, this.config.libraryName);
    fs.mkdirSync(libraryDir, { recursive: true });
    
    // Sanitize the title for use as a filename
    const filename = this._sanitizeFilename(item.title);
    
    // Return the full path
    return path.join(libraryDir, `${filename}.md`);
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
      library: this.config.libraryName,
      filePath: item.filePath || this._getOutputPath(item)
    }));
  }
  
  /**
   * Check if a URL is from a DeepWiki site.
   * 
   * @param {string} url - URL to check
   * @returns {Promise<boolean>} True if URL is from a DeepWiki site, False otherwise
   */
  async isDeepWikiSite(url) {
    try {
      // Check if the domain is reachable
      if (!await this._isDomainReachable(url)) {
        return false;
      }
      
      // Fetch the main page
      const content = await this.directScraper._fetchContent(url);
      
      // Check for DeepWiki markers in the content
      if (!content) {
        return false;
      }
      
      // Look for typical DeepWiki patterns
      // This is a simple heuristic and might need to be adjusted
      const hasMarkdownHeadings = /^#\s+.+$/m.test(content);
      const hasMarkdownLinks = /\[.+\]\(.+\)/.test(content);
      
      return hasMarkdownHeadings && hasMarkdownLinks;
    } catch (error) {
      logger.error(`Error checking if ${url} is a DeepWiki site: ${error.message}`);
      return false;
    }
  }
}

module.exports = {
  DeepwikiScraper
};