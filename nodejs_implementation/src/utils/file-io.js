/**
 * File I/O Utility for DeepWiki to Markdown Converter
 * 
 * This module provides file I/O functionality for the DeepWiki to Markdown converter.
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');
const { logger } = require('./logger');

/**
 * Save content to a Markdown file.
 * 
 * @param {string} filePath - Path to save the file
 * @param {string} content - Content to save
 * @returns {boolean} True if successful, false otherwise
 */
function saveMarkdownFile(filePath, content) {
  try {
    // Create directory if it doesn't exist
    const dirPath = path.dirname(filePath);
    fs.mkdirSync(dirPath, { recursive: true });
    
    // Save the file
    fs.writeFileSync(filePath, content, 'utf8');
    
    logger.debug(`Saved Markdown file: ${filePath}`);
    return true;
  } catch (error) {
    logger.error(`Error saving Markdown file ${filePath}: ${error.message}`);
    return false;
  }
}

/**
 * Read content from a Markdown file.
 * 
 * @param {string} filePath - Path to the file
 * @returns {string|null} File content or null if an error occurred
 */
function readMarkdownFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    
    logger.debug(`Read Markdown file: ${filePath}`);
    return content;
  } catch (error) {
    logger.error(`Error reading Markdown file ${filePath}: ${error.message}`);
    return null;
  }
}

/**
 * Save data to a JSON file.
 * 
 * @param {string} filePath - Path to save the file
 * @param {Object} data - Data to save
 * @returns {boolean} True if successful, false otherwise
 */
function saveJsonFile(filePath, data) {
  try {
    // Create directory if it doesn't exist
    const dirPath = path.dirname(filePath);
    fs.mkdirSync(dirPath, { recursive: true });
    
    // Save the file
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
    
    logger.debug(`Saved JSON file: ${filePath}`);
    return true;
  } catch (error) {
    logger.error(`Error saving JSON file ${filePath}: ${error.message}`);
    return false;
  }
}

/**
 * Read data from a JSON file.
 * 
 * @param {string} filePath - Path to the file
 * @returns {Object|null} File data or null if an error occurred
 */
function readJsonFile(filePath) {
  try {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    
    logger.debug(`Read JSON file: ${filePath}`);
    return data;
  } catch (error) {
    logger.error(`Error reading JSON file ${filePath}: ${error.message}`);
    return null;
  }
}

/**
 * Save data to a YAML file.
 * 
 * @param {string} filePath - Path to save the file
 * @param {Object} data - Data to save
 * @returns {boolean} True if successful, false otherwise
 */
function saveYamlFile(filePath, data) {
  try {
    // Create directory if it doesn't exist
    const dirPath = path.dirname(filePath);
    fs.mkdirSync(dirPath, { recursive: true });
    
    // Save the file
    const yamlStr = yaml.dump(data, {
      indent: 2,
      lineWidth: -1,
      noRefs: true,
      sortKeys: false
    });
    fs.writeFileSync(filePath, yamlStr, 'utf8');
    
    logger.debug(`Saved YAML file: ${filePath}`);
    return true;
  } catch (error) {
    logger.error(`Error saving YAML file ${filePath}: ${error.message}`);
    return false;
  }
}

/**
 * Read data from a YAML file.
 * 
 * @param {string} filePath - Path to the file
 * @returns {Object|null} File data or null if an error occurred
 */
function readYamlFile(filePath) {
  try {
    const data = yaml.load(fs.readFileSync(filePath, 'utf8'));
    
    logger.debug(`Read YAML file: ${filePath}`);
    return data;
  } catch (error) {
    logger.error(`Error reading YAML file ${filePath}: ${error.message}`);
    return null;
  }
}

/**
 * Check if a file exists.
 * 
 * @param {string} filePath - Path to the file
 * @returns {boolean} True if the file exists, false otherwise
 */
function fileExists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch (error) {
    logger.error(`Error checking if file exists ${filePath}: ${error.message}`);
    return false;
  }
}

/**
 * List files in a directory.
 * 
 * @param {string} dirPath - Path to the directory
 * @param {Object} [options={}] - Options
 * @param {boolean} [options.recursive=false] - Whether to list files recursively
 * @param {string} [options.extension=null] - Filter by file extension
 * @returns {Array<string>} List of file paths
 */
function listFiles(dirPath, options = {}) {
  const { recursive = false, extension = null } = options;
  
  try {
    if (!fs.existsSync(dirPath)) {
      logger.warn(`Directory does not exist: ${dirPath}`);
      return [];
    }
    
    if (!fs.statSync(dirPath).isDirectory()) {
      logger.warn(`Path is not a directory: ${dirPath}`);
      return [];
    }
    
    let files = [];
    
    const items = fs.readdirSync(dirPath);
    
    for (const item of items) {
      const itemPath = path.join(dirPath, item);
      const stat = fs.statSync(itemPath);
      
      if (stat.isDirectory() && recursive) {
        files = files.concat(listFiles(itemPath, options));
      } else if (stat.isFile()) {
        if (!extension || path.extname(itemPath) === extension) {
          files.push(itemPath);
        }
      }
    }
    
    return files;
  } catch (error) {
    logger.error(`Error listing files in ${dirPath}: ${error.message}`);
    return [];
  }
}

module.exports = {
  saveMarkdownFile,
  readMarkdownFile,
  saveJsonFile,
  readJsonFile,
  saveYamlFile,
  readYamlFile,
  fileExists,
  listFiles
};