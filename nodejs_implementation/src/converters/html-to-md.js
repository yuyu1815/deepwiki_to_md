/**
 * HTML to Markdown Converter for DeepWiki to Markdown Converter
 * 
 * This module provides functionality for converting HTML content to Markdown format.
 */

const cheerio = require('cheerio');
const { logger } = require('../utils/logger');
const { logExecutionTime } = require('../utils/error-handler');

/**
 * Converter for transforming HTML content to Markdown.
 * 
 * This class provides methods for converting HTML to Markdown with customizable options.
 */
class HTMLToMarkdownConverter {
  /**
   * Initialize the converter with options.
   * 
   * @param {Object} [options={}] - Options for the conversion process
   */
  constructor(options = {}) {
    this.options = {
      headingStyle: 'atx',  // Use # style headings
      bulletListMarker: '-',  // Use - for bullet lists
      codeBlockStyle: 'fenced',  // Use ``` for code blocks
      emDelimiter: '*',  // Use * for emphasis
      strongDelimiter: '**',  // Use ** for strong
      linkReferenceStyle: 'inline',  // Use inline links
      includeImageDimensions: false,  // Don't include image dimensions
      ...options
    };
  }
  
  /**
   * Convert HTML to Markdown.
   * 
   * @param {string} html - HTML content to convert
   * @returns {string} Converted Markdown content
   */
  convert(html) {
    // Clean HTML before conversion
    const cleanedHtml = this._cleanHtml(html);
    
    // Load HTML into cheerio
    const $ = cheerio.load(cleanedHtml);
    
    // Remove unwanted elements
    this._removeUnwantedElements($);
    
    // Convert to Markdown
    let markdown = this._convertToMarkdown($);
    
    // Post-process Markdown
    markdown = this._postProcessMarkdown(markdown);
    
    return markdown;
  }
  
  /**
   * Clean HTML before conversion.
   * 
   * @param {string} html - HTML content to clean
   * @returns {string} Cleaned HTML content
   * @private
   */
  _cleanHtml(html) {
    // Replace multiple newlines with a single newline
    let cleaned = html.replace(/\n\s*\n/g, '\n');
    
    // Remove HTML comments
    cleaned = cleaned.replace(/<!--[\s\S]*?-->/g, '');
    
    return cleaned;
  }
  
  /**
   * Remove unwanted elements from the HTML.
   * 
   * @param {Object} $ - Cheerio instance
   * @private
   */
  _removeUnwantedElements($) {
    // Remove script and style tags
    $('script, style').remove();
    
    // Remove other unwanted elements
    $('iframe, noscript, svg, canvas, audio, video').remove();
  }
  
  /**
   * Convert HTML to Markdown using cheerio.
   * 
   * @param {Object} $ - Cheerio instance
   * @returns {string} Converted Markdown content
   * @private
   */
  _convertToMarkdown($) {
    let markdown = '';
    
    // Process the body
    markdown = this._processNode($('body')[0]);
    
    return markdown;
  }
  
  /**
   * Process an HTML node and convert it to Markdown.
   * 
   * @param {Object} node - Cheerio node
   * @param {Object} [options={}] - Processing options
   * @returns {string} Markdown content
   * @private
   */
  _processNode(node, options = {}) {
    if (!node) return '';
    
    const $ = cheerio.load('');
    
    // Text node
    if (node.type === 'text') {
      return node.data;
    }
    
    // Element node
    if (node.type === 'tag') {
      const tagName = node.name.toLowerCase();
      
      // Process children first
      let childContent = '';
      if (node.children && node.children.length > 0) {
        childContent = node.children.map(child => this._processNode(child, options)).join('');
      }
      
      // Process different HTML elements
      switch (tagName) {
        case 'h1':
        case 'h2':
        case 'h3':
        case 'h4':
        case 'h5':
        case 'h6':
          const level = parseInt(tagName.substring(1), 10);
          return `\n${'#'.repeat(level)} ${childContent.trim()}\n\n`;
          
        case 'p':
          return `\n${childContent.trim()}\n\n`;
          
        case 'a':
          const href = node.attribs && node.attribs.href ? node.attribs.href : '';
          return `[${childContent.trim()}](${href})`;
          
        case 'img':
          const src = node.attribs && node.attribs.src ? node.attribs.src : '';
          const alt = node.attribs && node.attribs.alt ? node.attribs.alt : '';
          return `![${alt}](${src})`;
          
        case 'strong':
        case 'b':
          return `**${childContent.trim()}**`;
          
        case 'em':
        case 'i':
          return `*${childContent.trim()}*`;
          
        case 'code':
          return `\`${childContent.trim()}\``;
          
        case 'pre':
          // Check if it contains a code block
          if ($(node).find('code').length > 0) {
            const code = $(node).find('code').text();
            const language = $(node).find('code').attr('class') || '';
            const lang = language.replace('language-', '').replace('lang-', '');
            return `\n\`\`\`${lang}\n${code}\n\`\`\`\n\n`;
          }
          return `\n\`\`\`\n${childContent.trim()}\n\`\`\`\n\n`;
          
        case 'blockquote':
          // Add > to each line
          const lines = childContent.trim().split('\n');
          return `\n${lines.map(line => `> ${line}`).join('\n')}\n\n`;
          
        case 'ul':
          // Process list items
          return `\n${childContent}\n`;
          
        case 'ol':
          // Process ordered list items
          return `\n${childContent}\n`;
          
        case 'li':
          // Use the appropriate list marker
          const marker = options.ordered ? '1. ' : '- ';
          return `${marker}${childContent.trim()}\n`;
          
        case 'br':
          return '\n';
          
        case 'hr':
          return '\n---\n\n';
          
        case 'table':
          // Tables are complex, this is a simplified version
          return this._processTable(node);
          
        default:
          // For other elements, just return the content
          return childContent;
      }
    }
    
    return '';
  }
  
  /**
   * Process an HTML table and convert it to Markdown.
   * 
   * @param {Object} tableNode - Cheerio table node
   * @returns {string} Markdown table
   * @private
   */
  _processTable(tableNode) {
    const $ = cheerio.load(tableNode);
    let markdown = '\n';
    
    // Process header row
    const headerRow = $('thead tr').first();
    const headers = [];
    headerRow.find('th').each((i, cell) => {
      headers.push($(cell).text().trim());
    });
    
    if (headers.length === 0) {
      // If no header row, use the first row as header
      $('tr').first().find('td').each((i, cell) => {
        headers.push($(cell).text().trim());
      });
    }
    
    // Add header row to markdown
    markdown += `| ${headers.join(' | ')} |\n`;
    
    // Add separator row
    markdown += `| ${headers.map(() => '---').join(' | ')} |\n`;
    
    // Process data rows
    $('tbody tr').each((i, row) => {
      const cells = [];
      $(row).find('td').each((j, cell) => {
        cells.push($(cell).text().trim());
      });
      
      if (cells.length > 0) {
        markdown += `| ${cells.join(' | ')} |\n`;
      }
    });
    
    return markdown + '\n';
  }
  
  /**
   * Post-process Markdown after conversion.
   * 
   * @param {string} markdown - Converted Markdown content
   * @returns {string} Post-processed Markdown content
   * @private
   */
  _postProcessMarkdown(markdown) {
    // Fix consecutive newlines (more than 2)
    let processed = markdown.replace(/\n{3,}/g, '\n\n');
    
    // Fix code blocks (ensure proper spacing)
    processed = processed.replace(/```(\w*)\n/g, '```$1\n');
    
    // Fix list items (ensure proper spacing)
    processed = processed.replace(/(\n[*-] .*\n)([*-] )/g, '$1\n$2');
    
    return processed.trim();
  }
}

/**
 * Convert HTML content to Markdown.
 * 
 * @param {string} html - HTML content to convert
 * @param {Object} [options={}] - Options for the conversion process
 * @returns {string} Converted Markdown content
 */
const convertHtmlToMarkdown = logExecutionTime(function(html, options = {}) {
  const converter = new HTMLToMarkdownConverter(options);
  return converter.convert(html);
});

/**
 * Extract title from HTML content.
 * 
 * @param {string} html - HTML content to extract title from
 * @returns {string|null} Extracted title or null if not found
 */
function extractTitleFromHtml(html) {
  try {
    const $ = cheerio.load(html);
    
    // Try to get title from title tag
    const titleTag = $('title');
    if (titleTag.length > 0 && titleTag.text().trim()) {
      return titleTag.text().trim();
    }
    
    // Try to get title from first h1
    const h1Tag = $('h1').first();
    if (h1Tag.length > 0 && h1Tag.text().trim()) {
      return h1Tag.text().trim();
    }
    
    // Try to get title from first h2
    const h2Tag = $('h2').first();
    if (h2Tag.length > 0 && h2Tag.text().trim()) {
      return h2Tag.text().trim();
    }
    
    return null;
  } catch (error) {
    logger.error(`Error extracting title from HTML: ${error.message}`);
    return null;
  }
}

module.exports = {
  HTMLToMarkdownConverter,
  convertHtmlToMarkdown,
  extractTitleFromHtml
};