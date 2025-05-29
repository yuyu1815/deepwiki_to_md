/**
 * DeepWiki to Markdown Converter
 * 
 * A Node.js tool to scrape content from deepwiki sites and convert it to Markdown format.
 * This module provides the main functionality for the DeepWiki to Markdown converter.
 * 
 * @module deepwiki-to-md
 * @version 0.3.2
 * @author yuzumican
 * @license MIT
 */

const scraper = require('./scraper');
const converters = require('./converters');
const chat = require('./chat');
const utils = require('./utils');
const models = require('./models');

/**
 * Main function to scrape content from a DeepWiki site and convert it to Markdown.
 * 
 * @param {Object} config - Configuration object
 * @param {string} config.url - URL of the DeepWiki site
 * @param {string} config.libraryName - Name of the library
 * @param {string} [config.outputDir='./output'] - Output directory
 * @param {boolean} [config.verbose=false] - Verbose output
 * @returns {Promise<Array<Object>>} - Array of scraped content items
 */
async function scrapeAndConvert(config) {
  const deepwikiScraper = new scraper.DeepwikiScraper(config);
  return await deepwikiScraper.scrape();
}

/**
 * Convert HTML content to Markdown.
 * 
 * @param {string} html - HTML content to convert
 * @param {Object} [options={}] - Conversion options
 * @returns {string} - Converted Markdown content
 */
function convertHtmlToMarkdown(html, options = {}) {
  return converters.htmlToMd.convert(html, options);
}

/**
 * Convert Markdown content to YAML.
 * 
 * @param {string} markdown - Markdown content to convert
 * @param {string} [title=null] - Title for the content
 * @param {string} [url=null] - URL source of the content
 * @param {Object} [options={}] - Conversion options
 * @returns {Object} - Converted YAML content as an object
 */
function convertMarkdownToYaml(markdown, title = null, url = null, options = {}) {
  return converters.mdToYaml.convert(markdown, title, url, options);
}

/**
 * Send a message to the DeepWiki chat and get a response.
 * 
 * @param {Object} config - Configuration object
 * @param {string} message - Message to send
 * @param {number} [timeout=60] - Maximum time to wait for a response in seconds
 * @returns {Promise<string|null>} - Response text or null if no response received
 */
async function chatWithDeepWiki(config, message, timeout = 60) {
  return await chat.getResponse(config, message, timeout);
}

/**
 * Conduct deep research using the DeepWiki chat.
 * 
 * @param {Object} config - Configuration object
 * @param {Array<string>} questions - List of questions to ask
 * @param {string} [outputDir=null] - Directory to save results in
 * @param {Array<string>} [formats=['md', 'json', 'yaml']] - List of formats to save results in
 * @param {number} [timeout=120] - Maximum time to wait for each response in seconds
 * @returns {Promise<Object>} - Research results and saved file information
 */
async function conductResearch(config, questions, outputDir = null, formats = ['md', 'json', 'yaml'], timeout = 120) {
  return await chat.conductResearch(config, questions, outputDir, formats, timeout);
}

// Export public API
module.exports = {
  scrapeAndConvert,
  convertHtmlToMarkdown,
  convertMarkdownToYaml,
  chatWithDeepWiki,
  conductResearch,
  scraper,
  converters,
  chat,
  utils,
  models,
  version: '0.3.2'
};