/**
 * Content Parser for DeepWiki to Markdown Converter
 * 
 * This module provides functionality for parsing Markdown content.
 */

const yaml = require('js-yaml');
const { logger } = require('../utils/logger');

/**
 * Parse Markdown content into a structured format.
 * 
 * @param {string} markdown - Markdown content to parse
 * @returns {Array<Object>} Parsed content as a list of elements
 */
function parseMarkdownContent(markdown) {
  // Split content into lines
  const lines = markdown.split('\n');
  
  // Parse lines into elements
  const elements = [];
  let currentElement = null;
  
  for (const line of lines) {
    // Check for headings
    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const text = headingMatch[2].trim();
      elements.push({
        type: 'heading',
        level,
        text
      });
      currentElement = null;
      continue;
    }
    
    // Check for list items
    const listMatch = line.match(/^(\s*)([-*+]|\d+\.)\s+(.+)$/);
    if (listMatch) {
      const indent = listMatch[1].length;
      const marker = listMatch[2];
      const text = listMatch[3].trim();
      
      const listType = marker.match(/[-*+]/) ? 'unordered' : 'ordered';
      
      elements.push({
        type: 'list_item',
        listType,
        indent,
        text
      });
      currentElement = null;
      continue;
    }
    
    // Check for code blocks
    if (line.startsWith('```')) {
      if (currentElement && currentElement.type === 'code_block') {
        // End of code block
        currentElement = null;
      } else {
        // Start of code block
        const language = line.substring(3).trim();
        currentElement = {
          type: 'code_block',
          language,
          content: []
        };
        elements.push(currentElement);
      }
      continue;
    }
    
    // Add line to current code block
    if (currentElement && currentElement.type === 'code_block') {
      currentElement.content.push(line);
      continue;
    }
    
    // Check for blank lines
    if (!line.trim()) {
      if (currentElement && currentElement.type === 'paragraph') {
        currentElement = null;
      }
      continue;
    }
    
    // Default: paragraph text
    if (currentElement && currentElement.type === 'paragraph') {
      currentElement.text += '\n' + line;
    } else {
      currentElement = {
        type: 'paragraph',
        text: line
      };
      elements.push(currentElement);
    }
  }
  
  // Post-process elements
  return postProcessElements(elements);
}

/**
 * Post-process parsed elements.
 * 
 * @param {Array<Object>} elements - Parsed elements
 * @returns {Array<Object>} Post-processed elements
 */
function postProcessElements(elements) {
  // Join code block content
  for (const element of elements) {
    if (element.type === 'code_block') {
      element.content = element.content.join('\n');
    }
  }
  
  // Group list items into lists
  const processedElements = [];
  let currentList = null;
  
  for (const element of elements) {
    if (element.type === 'list_item') {
      if (!currentList || currentList.listType !== element.listType) {
        // Start a new list
        currentList = {
          type: 'list',
          listType: element.listType,
          items: []
        };
        processedElements.push(currentList);
      }
      
      // Add item to the current list
      currentList.items.push({
        text: element.text,
        indent: element.indent
      });
    } else {
      // Non-list element
      currentList = null;
      processedElements.push(element);
    }
  }
  
  return processedElements;
}

/**
 * Extract metadata from Markdown content.
 * 
 * This function looks for YAML frontmatter or other metadata patterns.
 * 
 * @param {string} markdown - Markdown content to extract metadata from
 * @returns {Object} Extracted metadata
 */
function extractMetadata(markdown) {
  const metadata = {};
  
  // Check for YAML frontmatter
  const frontmatterMatch = markdown.match(/^---\s*\n([\s\S]*?)\n---\s*\n/);
  if (frontmatterMatch) {
    try {
      const frontmatterText = frontmatterMatch[1];
      const yamlMetadata = yaml.load(frontmatterText);
      if (yamlMetadata && typeof yamlMetadata === 'object') {
        Object.assign(metadata, yamlMetadata);
      }
    } catch (error) {
      logger.warn(`Error parsing YAML frontmatter: ${error.message}`);
    }
  }
  
  // Extract title from first heading if not already set
  if (!metadata.title) {
    const titleMatch = markdown.match(/^#\s+(.+)$/m);
    if (titleMatch) {
      metadata.title = titleMatch[1].trim();
    }
  }
  
  // Extract other metadata patterns (e.g., key: value)
  const metadataPattern = /^([A-Za-z0-9_-]+):\s*(.+)$/gm;
  let match;
  while ((match = metadataPattern.exec(markdown)) !== null) {
    const key = match[1].trim().toLowerCase();
    const value = match[2].trim();
    
    // Don't overwrite existing metadata
    if (!metadata[key]) {
      metadata[key] = value;
    }
  }
  
  return metadata;
}

/**
 * Extract sections from Markdown content based on headings.
 * 
 * @param {string} markdown - Markdown content to extract sections from
 * @returns {Object} Dictionary of section title to section content
 */
function extractSections(markdown) {
  const sections = {};
  
  // Split content by headings
  const headingPattern = /^(#{1,6})\s+(.+)$/m;
  const splits = markdown.split(new RegExp(`(${headingPattern.source})`, 'gm'));
  
  if (splits.length < 3) {
    // No headings found
    return sections;
  }
  
  // Process splits
  let currentTitle = null;
  let currentContent = [];
  
  for (let i = 1; i < splits.length; i += 3) {
    if (i + 1 < splits.length) {
      const level = splits[i].length;
      const title = splits[i + 1].trim();
      
      if (currentTitle) {
        sections[currentTitle] = currentContent.join('\n').trim();
      }
      
      currentTitle = title;
      currentContent = [];
      
      if (i + 2 < splits.length) {
        currentContent.push(splits[i + 2]);
      }
    }
  }
  
  // Add the last section
  if (currentTitle) {
    sections[currentTitle] = currentContent.join('\n').trim();
  }
  
  return sections;
}

/**
 * Extract links from Markdown content.
 * 
 * @param {string} markdown - Markdown content to extract links from
 * @returns {Array<Object>} List of links with title and url
 */
function extractLinks(markdown) {
  const links = [];
  
  // Extract Markdown links
  const linkPattern = /\[([^\]]+)\]\(([^)]+)\)/g;
  let match;
  
  while ((match = linkPattern.exec(markdown)) !== null) {
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
 * Extract images from Markdown content.
 * 
 * @param {string} markdown - Markdown content to extract images from
 * @returns {Array<Object>} List of images with alt text and url
 */
function extractImages(markdown) {
  const images = [];
  
  // Extract Markdown images
  const imagePattern = /!\[([^\]]*)\]\(([^)]+)\)/g;
  let match;
  
  while ((match = imagePattern.exec(markdown)) !== null) {
    const alt = match[1].trim();
    const url = match[2].trim();
    
    images.push({
      alt,
      url
    });
  }
  
  return images;
}

/**
 * Extract code blocks from Markdown content.
 * 
 * @param {string} markdown - Markdown content to extract code blocks from
 * @returns {Array<Object>} List of code blocks with language and content
 */
function extractCodeBlocks(markdown) {
  const codeBlocks = [];
  
  // Extract Markdown code blocks
  const codeBlockPattern = /```([^\n]*)\n([\s\S]*?)```/g;
  let match;
  
  while ((match = codeBlockPattern.exec(markdown)) !== null) {
    const language = match[1].trim();
    const content = match[2];
    
    codeBlocks.push({
      language,
      content
    });
  }
  
  return codeBlocks;
}

module.exports = {
  parseMarkdownContent,
  extractMetadata,
  extractSections,
  extractLinks,
  extractImages,
  extractCodeBlocks
};