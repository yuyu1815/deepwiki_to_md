/**
 * Content Model for DeepWiki to Markdown Converter
 * 
 * This module provides the content data model for the DeepWiki to Markdown converter.
 */

/**
 * Content data model for storing scraped content.
 * 
 * This class stores the content scraped from DeepWiki sites, including metadata.
 */
class Content {
  /**
   * Create a content object.
   * 
   * @param {Object} options - Content options
   * @param {string} options.title - Title of the content
   * @param {string} options.content - Content text
   * @param {string} options.url - URL source of the content
   * @param {string} [options.library=''] - Library name
   * @param {string} [options.filePath=null] - Path to the saved file
   * @param {Object} [options.metadata={}] - Metadata for the content
   * @param {Array<Object>} [options.navigation=[]] - Navigation links
   * @param {Date} [options.createdAt=new Date()] - Creation timestamp
   * @param {Date} [options.updatedAt=null] - Update timestamp
   */
  constructor(options) {
    // Required fields
    this.title = options.title;
    this.content = options.content;
    this.url = options.url;
    
    // Optional fields with defaults
    this.library = options.library || '';
    this.filePath = options.filePath || null;
    
    // Metadata
    this.metadata = options.metadata || {};
    this.navigation = options.navigation || [];
    
    // Timestamps
    this.createdAt = options.createdAt || new Date();
    this.updatedAt = options.updatedAt || this.createdAt;
  }
  
  /**
   * Update the content and update timestamp.
   * 
   * @param {string} newContent - New content to set
   */
  updateContent(newContent) {
    this.content = newContent;
    this.updatedAt = new Date();
  }
  
  /**
   * Add a navigation item.
   * 
   * @param {string} title - Title of the navigation item
   * @param {string} url - URL of the navigation item
   */
  addNavigationItem(title, url) {
    this.navigation.push({ title, url });
  }
  
  /**
   * Convert the content to a plain object.
   * 
   * @returns {Object} Plain object representation of the content
   */
  toObject() {
    return {
      title: this.title,
      content: this.content,
      url: this.url,
      library: this.library,
      filePath: this.filePath,
      metadata: this.metadata,
      navigation: this.navigation,
      createdAt: this.createdAt.toISOString(),
      updatedAt: this.updatedAt.toISOString()
    };
  }
  
  /**
   * Create a content object from a plain object.
   * 
   * @param {Object} obj - Plain object containing content data
   * @returns {Content} Content object
   */
  static fromObject(obj) {
    // Handle date fields
    const options = { ...obj };
    
    if (typeof options.createdAt === 'string') {
      options.createdAt = new Date(options.createdAt);
    }
    
    if (typeof options.updatedAt === 'string') {
      options.updatedAt = new Date(options.updatedAt);
    }
    
    return new Content(options);
  }
  
  /**
   * Get a string representation of the content.
   * 
   * @returns {string} String representation of the content
   */
  toString() {
    return `Content(title='${this.title}', url='${this.url}', library='${this.library}')`;
  }
  
  /**
   * Get a summary of the content.
   * 
   * @param {number} [maxLength=100] - Maximum length of the summary
   * @returns {string} Content summary
   */
  getSummary(maxLength = 100) {
    // Remove Markdown formatting
    let plainText = this.content
      .replace(/#+\s+/g, '') // Remove headings
      .replace(/\*\*|__/g, '') // Remove bold
      .replace(/\*|_/g, '') // Remove italic
      .replace(/`/g, '') // Remove inline code
      .replace(/```[\s\S]*?```/g, '') // Remove code blocks
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Replace links with just the text
      .replace(/!\[([^\]]*)\]\([^)]+\)/g, '') // Remove images
      .replace(/\n+/g, ' ') // Replace newlines with spaces
      .trim();
    
    // Truncate if needed
    if (plainText.length > maxLength) {
      plainText = plainText.substring(0, maxLength - 3) + '...';
    }
    
    return plainText;
  }
  
  /**
   * Extract keywords from the content.
   * 
   * @param {number} [maxKeywords=5] - Maximum number of keywords to extract
   * @returns {Array<string>} Extracted keywords
   */
  extractKeywords(maxKeywords = 5) {
    // Simple keyword extraction based on word frequency
    // In a real implementation, this would use more sophisticated NLP techniques
    
    // Remove Markdown formatting and convert to lowercase
    const plainText = this.content
      .replace(/#+\s+/g, '')
      .replace(/\*\*|__/g, '')
      .replace(/\*|_/g, '')
      .replace(/`/g, '')
      .replace(/```[\s\S]*?```/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/!\[([^\]]*)\]\([^)]+\)/g, '')
      .toLowerCase();
    
    // Split into words and count frequency
    const words = plainText.split(/\W+/);
    const wordCounts = {};
    const stopWords = new Set(['the', 'and', 'a', 'an', 'in', 'to', 'for', 'of', 'on', 'with', 'is', 'are', 'that', 'this', 'it', 'as', 'by', 'be', 'or', 'at', 'from']);
    
    for (const word of words) {
      if (word.length > 3 && !stopWords.has(word)) {
        wordCounts[word] = (wordCounts[word] || 0) + 1;
      }
    }
    
    // Sort by frequency and return top keywords
    return Object.entries(wordCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, maxKeywords)
      .map(entry => entry[0]);
  }
}

module.exports = {
  Content
};