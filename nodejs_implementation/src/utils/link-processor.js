/**
 * Link Processing Utility for DeepWiki to Markdown Converter
 * 
 * This module provides link processing functionality for the DeepWiki to Markdown converter.
 */

const path = require('path');
const url = require('url');
const fs = require('fs');
const { logger } = require('./logger');

/**
 * Fix Markdown links in content.
 * 
 * This function replaces URLs in Markdown links with empty brackets,
 * which is a common convention for some Markdown processors.
 * 
 * @param {string} content - Markdown content to process
 * @returns {string} Processed Markdown content
 */
function fixMarkdownLinks(content) {
  // Regular expression to match Markdown links
  const linkPattern = /\[([^\]]+)\]\(([^)]+)\)/g;
  
  // Replace links
  const processedContent = content.replace(linkPattern, (match, title, url) => {
    // Skip anchor links
    if (url.startsWith('#')) {
      return match;
    }
    
    // Replace URL with empty brackets
    return `[${title}]()`;
  });
  
  return processedContent;
}

/**
 * Extract links from Markdown content.
 * 
 * @param {string} content - Markdown content to extract links from
 * @returns {Array<Object>} List of links with title and url
 */
function extractLinks(content) {
  const links = [];
  
  // Regular expression to match Markdown links
  const linkPattern = /\[([^\]]+)\]\(([^)]+)\)/g;
  let match;
  
  while ((match = linkPattern.exec(content)) !== null) {
    const title = match[1].trim();
    const url = match[2].trim();
    
    // Skip empty or anchor links
    if (!url || url.startsWith('#')) {
      continue;
    }
    
    links.push({
      title,
      url
    });
  }
  
  return links;
}

/**
 * Normalize a URL.
 * 
 * @param {string} urlStr - URL to normalize
 * @param {string} [baseUrl=null] - Base URL for resolving relative URLs
 * @returns {string} Normalized URL
 */
function normalizeUrl(urlStr, baseUrl = null) {
  // Handle relative URLs
  if (baseUrl && !urlStr.startsWith('http://') && !urlStr.startsWith('https://')) {
    urlStr = new URL(urlStr, baseUrl).href;
  }
  
  // Parse the URL
  const parsedUrl = new URL(urlStr);
  
  // Normalize the URL
  let normalizedUrl = `${parsedUrl.protocol}//${parsedUrl.hostname}${parsedUrl.pathname}`;
  
  // Add query parameters if present
  if (parsedUrl.search) {
    normalizedUrl += parsedUrl.search;
  }
  
  // Add fragment if present
  if (parsedUrl.hash) {
    normalizedUrl += parsedUrl.hash;
  }
  
  return normalizedUrl;
}

/**
 * Get the relative path from basePath to targetPath.
 * 
 * @param {string} targetPath - Target path
 * @param {string} basePath - Base path
 * @returns {string} Relative path
 */
function getRelativePath(targetPath, basePath) {
  // Convert to absolute paths
  const targetAbs = path.resolve(targetPath);
  const baseAbs = path.resolve(basePath);
  
  // Get the relative path
  const relPath = path.relative(path.dirname(baseAbs), targetAbs);
  
  // Convert to forward slashes for Markdown
  return relPath.replace(/\\/g, '/');
}

/**
 * Update internal links in Markdown content.
 * 
 * @param {string} content - Markdown content to update
 * @param {Object} fileMapping - Mapping from URLs to local file paths
 * @param {string} currentFile - Path to the current file
 * @returns {string} Updated Markdown content
 */
function updateInternalLinks(content, fileMapping, currentFile) {
  // Regular expression to match Markdown links
  const linkPattern = /\[([^\]]+)\]\(([^)]+)\)/g;
  
  // Replace links
  const updatedContent = content.replace(linkPattern, (match, title, url) => {
    // Skip anchor links
    if (url.startsWith('#')) {
      return match;
    }
    
    // Check if the URL is in the mapping
    if (fileMapping[url]) {
      const targetFile = fileMapping[url];
      const relPath = getRelativePath(targetFile, currentFile);
      return `[${title}](${relPath})`;
    }
    
    // Keep external links as is
    return match;
  });
  
  return updatedContent;
}

/**
 * Process all Markdown files in a directory to fix links.
 * 
 * @param {string} directory - Directory containing Markdown files
 * @returns {boolean} True if successful, false otherwise
 */
function processMarkdownLinks(directory) {
  try {
    // Check if directory exists
    if (!fs.existsSync(directory)) {
      logger.error(`Directory does not exist: ${directory}`);
      return false;
    }
    
    // Find all Markdown files
    const files = [];
    findMarkdownFiles(directory, files);
    
    if (files.length === 0) {
      logger.warn(`No Markdown files found in ${directory}`);
      return false;
    }
    
    // Process each file
    let successCount = 0;
    
    for (const file of files) {
      try {
        // Read file
        const content = fs.readFileSync(file, 'utf8');
        
        // Fix links
        const processedContent = fixMarkdownLinks(content);
        
        // Write file
        fs.writeFileSync(file, processedContent, 'utf8');
        
        successCount++;
        logger.debug(`Processed links in ${file}`);
      } catch (error) {
        logger.error(`Error processing ${file}: ${error.message}`);
      }
    }
    
    logger.info(`Processed links in ${successCount} of ${files.length} files`);
    return successCount > 0;
  } catch (error) {
    logger.error(`Error processing Markdown links: ${error.message}`);
    return false;
  }
}

/**
 * Find all Markdown files in a directory.
 * 
 * @param {string} directory - Directory to search
 * @param {Array<string>} files - Array to store found files
 */
function findMarkdownFiles(directory, files) {
  const items = fs.readdirSync(directory);
  
  for (const item of items) {
    const itemPath = path.join(directory, item);
    const stat = fs.statSync(itemPath);
    
    if (stat.isDirectory()) {
      findMarkdownFiles(itemPath, files);
    } else if (stat.isFile() && (item.endsWith('.md') || item.endsWith('.markdown'))) {
      files.push(itemPath);
    }
  }
}

module.exports = {
  fixMarkdownLinks,
  extractLinks,
  normalizeUrl,
  getRelativePath,
  updateInternalLinks,
  processMarkdownLinks
};