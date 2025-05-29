/**
 * Markdown to YAML Converter for DeepWiki to Markdown Converter
 * 
 * This module provides functionality for converting Markdown content to YAML format.
 */

const yaml = require('js-yaml');
const { logger } = require('../utils/logger');
const { logExecutionTime } = require('../utils/error-handler');

/**
 * Converter for transforming Markdown content to YAML.
 * 
 * This class provides methods for converting Markdown to YAML with customizable options.
 */
class MarkdownToYAMLConverter {
  /**
   * Initialize the converter with options.
   * 
   * @param {Object} [options={}] - Options for the conversion process
   */
  constructor(options = {}) {
    this.options = {
      includeMetadata: true,  // Include metadata in YAML output
      includeContent: true,   // Include content in YAML output
      structureHeadings: true,  // Structure content by headings
      maxHeadingDepth: 3,    // Maximum heading depth to structure
      includeRawContent: false,  // Include raw Markdown content
      ...options
    };
  }
  
  /**
   * Convert Markdown to YAML.
   * 
   * @param {string} markdown - Markdown content to convert
   * @param {string} [title=null] - Title for the content
   * @param {string} [url=null] - URL source of the content
   * @returns {Object} Converted YAML content as an object
   */
  convert(markdown, title = null, url = null) {
    // Parse Markdown content
    const parsedContent = this._parseMarkdownContent(markdown);
    
    // Extract metadata
    const metadata = this._extractMetadata(markdown);
    
    // Create YAML structure
    const yamlData = {};
    
    // Add metadata if requested
    if (this.options.includeMetadata) {
      yamlData.metadata = metadata;
      
      // Add title and URL if provided
      if (title) {
        yamlData.metadata.title = title;
      }
      if (url) {
        yamlData.metadata.url = url;
      }
    }
    
    // Add content if requested
    if (this.options.includeContent) {
      if (this.options.structureHeadings) {
        yamlData.content = this._structureContent(parsedContent);
      } else {
        yamlData.content = parsedContent;
      }
    }
    
    // Add raw content if requested
    if (this.options.includeRawContent) {
      yamlData.rawContent = markdown;
    }
    
    return yamlData;
  }
  
  /**
   * Parse Markdown content into a structured format.
   * 
   * @param {string} markdown - Markdown content to parse
   * @returns {Array<Object>} Parsed content as a list of elements
   * @private
   */
  _parseMarkdownContent(markdown) {
    const elements = [];
    const lines = markdown.split('\n');
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
    return this._postProcessElements(elements);
  }
  
  /**
   * Post-process parsed elements.
   * 
   * @param {Array<Object>} elements - Parsed elements
   * @returns {Array<Object>} Post-processed elements
   * @private
   */
  _postProcessElements(elements) {
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
        if (!currentList || currentList.type !== element.listType) {
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
   * @param {string} markdown - Markdown content to extract metadata from
   * @returns {Object} Extracted metadata
   * @private
   */
  _extractMetadata(markdown) {
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
   * Structure content by headings.
   * 
   * @param {Array<Object>} parsedContent - Parsed Markdown content
   * @returns {Object} Structured content
   * @private
   */
  _structureContent(parsedContent) {
    const structuredContent = {};
    let currentSection = structuredContent;
    const sectionStack = [structuredContent];
    
    for (const item of parsedContent) {
      if (item.type === 'heading' && item.level <= this.options.maxHeadingDepth) {
        // Reset to appropriate level in the hierarchy
        while (sectionStack.length > item.level) {
          sectionStack.pop();
        }
        
        // Create new section
        const parent = sectionStack[sectionStack.length - 1];
        const sectionTitle = item.text;
        parent[sectionTitle] = {};
        currentSection = parent[sectionTitle];
        
        // Add to stack
        sectionStack.push(currentSection);
      } else {
        // Add content to current section
        if (!currentSection.content) {
          currentSection.content = [];
        }
        
        currentSection.content.push(item);
      }
    }
    
    return structuredContent;
  }
}

/**
 * Convert Markdown content to YAML.
 * 
 * @param {string} markdown - Markdown content to convert
 * @param {string} [title=null] - Title for the content
 * @param {string} [url=null] - URL source of the content
 * @param {Object} [options={}] - Options for the conversion process
 * @returns {Object} Converted YAML content as an object
 */
const convertMarkdownToYaml = logExecutionTime(function(markdown, title = null, url = null, options = {}) {
  const converter = new MarkdownToYAMLConverter(options);
  return converter.convert(markdown, title, url);
});

/**
 * Convert YAML data to a YAML string.
 * 
 * @param {Object} yamlData - YAML data to convert
 * @param {Object} [options={}] - Options for the YAML dumper
 * @returns {string} YAML string
 */
function yamlToString(yamlData, options = {}) {
  const dumpOptions = {
    indent: 2,
    lineWidth: -1,
    noRefs: true,
    sortKeys: false,
    ...options
  };
  
  return yaml.dump(yamlData, dumpOptions);
}

module.exports = {
  MarkdownToYAMLConverter,
  convertMarkdownToYaml,
  yamlToString
};