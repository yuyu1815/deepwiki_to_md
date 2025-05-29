/**
 * Localization Utility for DeepWiki to Markdown Converter
 * 
 * This module provides localization functionality for the DeepWiki to Markdown converter.
 */

const fs = require('fs');
const path = require('path');
const { logger } = require('./logger');

// Default language
const DEFAULT_LANGUAGE = 'en';

// Current language
let currentLanguage = null;

// Messages cache
const messages = {};

/**
 * Get the directory containing locale files.
 * 
 * @returns {string} Path to the locale directory
 */
function getLocaleDir() {
  // Get the package directory
  const packageDir = path.resolve(__dirname, '..', '..', '..');
  return path.join(packageDir, 'locales');
}

/**
 * Load messages for the specified language.
 * 
 * @param {string} language - Language code (e.g., "en", "ja")
 * @returns {Object} Dictionary of messages
 */
function loadMessages(language) {
  // Check if messages are already loaded
  if (messages[language]) {
    return messages[language];
  }
  
  // Load messages from file
  const localeDir = getLocaleDir();
  const localeFile = path.join(localeDir, `${language}.json`);
  
  try {
    const data = fs.readFileSync(localeFile, 'utf8');
    const loadedMessages = JSON.parse(data);
    
    // Cache messages
    messages[language] = loadedMessages;
    
    return loadedMessages;
  } catch (error) {
    // If messages couldn't be loaded, try the default language
    if (language !== DEFAULT_LANGUAGE) {
      logger.warn(`Could not load messages for language '${language}'. Falling back to '${DEFAULT_LANGUAGE}'.`);
      return loadMessages(DEFAULT_LANGUAGE);
    } else {
      // If default language couldn't be loaded, use empty object
      logger.error(`Could not load messages for default language '${DEFAULT_LANGUAGE}'.`);
      messages[language] = {};
      return {};
    }
  }
}

/**
 * Set the current language.
 * 
 * @param {string} language - Language code (e.g., "en", "ja")
 */
function setLanguage(language) {
  currentLanguage = language;
  logger.debug(`Set language to '${language}'`);
}

/**
 * Get the current language.
 * 
 * @returns {string} Current language code
 */
function getCurrentLanguage() {
  // If language is not set, try to detect it
  if (!currentLanguage) {
    try {
      // Try to get the system language
      const osLocale = require('os-locale').sync();
      if (osLocale) {
        const language = osLocale.split('_')[0];
        
        // Check if we have messages for this language
        const localeDir = getLocaleDir();
        const localeFile = path.join(localeDir, `${language}.json`);
        
        if (fs.existsSync(localeFile)) {
          currentLanguage = language;
          logger.debug(`Detected language: '${language}'`);
        } else {
          currentLanguage = DEFAULT_LANGUAGE;
          logger.debug(`No messages for detected language '${language}'. Using default: '${DEFAULT_LANGUAGE}'`);
        }
      } else {
        currentLanguage = DEFAULT_LANGUAGE;
        logger.debug(`Could not detect system language. Using default: '${DEFAULT_LANGUAGE}'`);
      }
    } catch (error) {
      currentLanguage = DEFAULT_LANGUAGE;
      logger.error(`Error detecting language: ${error.message}. Using default: '${DEFAULT_LANGUAGE}'`);
    }
  }
  
  return currentLanguage;
}

/**
 * Get a localized message.
 * 
 * @param {string} key - Message key
 * @param {Object} [params={}] - Format parameters for the message
 * @returns {string} Localized message
 */
function getLocalizedMessage(key, params = {}) {
  const language = getCurrentLanguage();
  const messageDict = loadMessages(language);
  
  // Get message for the key
  let message = messageDict[key];
  
  // If message is not found, try the default language
  if (!message && language !== DEFAULT_LANGUAGE) {
    const defaultMessages = loadMessages(DEFAULT_LANGUAGE);
    message = defaultMessages[key];
  }
  
  // If message is still not found, use the key
  if (!message) {
    logger.warn(`No message found for key '${key}' in any language.`);
    message = key;
  }
  
  // Format the message with parameters
  try {
    if (Object.keys(params).length > 0) {
      message = message.replace(/\{(\w+)\}/g, (match, paramName) => {
        return params[paramName] !== undefined ? params[paramName] : match;
      });
    }
  } catch (error) {
    logger.error(`Error formatting message '${key}': ${error.message}`);
  }
  
  return message;
}

module.exports = {
  getLocalizedMessage,
  setLanguage,
  getCurrentLanguage,
  loadMessages
};