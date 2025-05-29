/**
 * Chat Interface for DeepWiki to Markdown Converter
 * 
 * This module provides the interface for interacting with the DeepWiki chat.
 */

const axios = require('axios');
const puppeteer = require('puppeteer');
const { logger } = require('../utils/logger');
const { handleRequestError, retryOnException } = require('../utils/error-handler');
const { convertHtmlToMarkdown } = require('../converters/html-to-md');

/**
 * Interface for interacting with the DeepWiki chat.
 * 
 * This class provides methods for sending messages to the DeepWiki chat
 * and receiving responses.
 */
class ChatInterface {
  /**
   * Initialize the chat interface.
   * 
   * @param {Object} config - Configuration object
   */
  constructor(config) {
    this.config = config;
    this.browser = null;
    this.page = null;
    this.session = axios.create({
      headers: config.headers || {},
      timeout: config.timeout || 30000
    });
    this.conversationId = null;
    
    logger.debug("Initialized ChatInterface");
  }
  
  /**
   * Connect to the DeepWiki chat.
   * 
   * @returns {Promise<boolean>} True if connection successful, False otherwise
   */
  async connect() {
    try {
      // Initialize Puppeteer if needed
      if (this.config.useSelenium) {
        await this._initPuppeteer();
      }
      
      // Create a new conversation
      await this._createConversation();
      
      logger.info("Connected to DeepWiki chat");
      return true;
    } catch (error) {
      logger.error(`Error connecting to DeepWiki chat: ${error.message}`);
      return false;
    }
  }
  
  /**
   * Disconnect from the DeepWiki chat.
   * 
   * @returns {Promise<void>}
   */
  async disconnect() {
    try {
      // Close Puppeteer browser if it was used
      if (this.browser) {
        await this.browser.close();
        this.browser = null;
        this.page = null;
      }
      
      logger.info("Disconnected from DeepWiki chat");
    } catch (error) {
      logger.error(`Error disconnecting from DeepWiki chat: ${error.message}`);
    }
  }
  
  /**
   * Send a message to the DeepWiki chat.
   * 
   * @param {string} message - Message to send
   * @returns {Promise<boolean>} True if message sent successfully, False otherwise
   */
  async sendMessage(message) {
    try {
      if (this.page) {
        return await this._sendMessagePuppeteer(message);
      } else {
        return await this._sendMessageApi(message);
      }
    } catch (error) {
      logger.error(`Error sending message: ${error.message}`);
      return false;
    }
  }
  
  /**
   * Get a response from the DeepWiki chat.
   * 
   * @param {number} [timeout=60000] - Maximum time to wait for a response in milliseconds
   * @returns {Promise<string|null>} Response text or null if no response received
   */
  async getResponse(timeout = 60000) {
    try {
      if (this.page) {
        return await this._getResponsePuppeteer(timeout);
      } else {
        return await this._getResponseApi(timeout);
      }
    } catch (error) {
      logger.error(`Error getting response: ${error.message}`);
      return null;
    }
  }
  
  /**
   * Initialize Puppeteer.
   * 
   * @returns {Promise<void>}
   * @private
   */
  async _initPuppeteer() {
    // Set up Puppeteer options
    const options = {
      headless: !this.config.showBrowser,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
    };
    
    // Initialize browser
    this.browser = await puppeteer.launch(options);
    this.page = await this.browser.newPage();
    
    // Navigate to the chat URL
    await this.page.goto(this.config.url);
    
    // Wait for the page to load
    await this.page.waitForSelector('body');
    
    logger.debug("Initialized Puppeteer");
  }
  
  /**
   * Create a new conversation.
   * 
   * @returns {Promise<void>}
   * @private
   */
  async _createConversation() {
    if (this.page) {
      // Puppeteer-based conversation creation
      // This is a placeholder - actual implementation would depend on the DeepWiki UI
      return;
    } else {
      // API-based conversation creation
      const url = `${this.config.url}/api/conversation`;
      const data = {
        model: this.config.model || 'default',
        messages: []
      };
      
      try {
        const response = await this.session.post(url, data);
        
        if (response.data && response.data.conversation_id) {
          this.conversationId = response.data.conversation_id;
        } else {
          throw new Error("No conversation ID returned");
        }
      } catch (error) {
        handleRequestError(error, url);
        throw error;
      }
    }
  }
  
  /**
   * Send a message using Puppeteer.
   * 
   * @param {string} message - Message to send
   * @returns {Promise<boolean>} True if message sent successfully, False otherwise
   * @private
   */
  async _sendMessagePuppeteer(message) {
    try {
      // Find the input field
      const inputSelector = "textarea[placeholder*='message'], input[placeholder*='message']";
      await this.page.waitForSelector(inputSelector);
      
      // Clear the input field
      await this.page.evaluate((selector) => {
        document.querySelector(selector).value = '';
      }, inputSelector);
      
      // Type the message
      await this.page.type(inputSelector, message);
      
      // Find and click the send button
      const sendButtonSelector = "button[type='submit'], button.send-button";
      await this.page.waitForSelector(sendButtonSelector);
      await this.page.click(sendButtonSelector);
      
      // Wait for the message to be sent
      await this.page.waitForTimeout(1000);
      
      return true;
    } catch (error) {
      logger.error(`Error sending message with Puppeteer: ${error.message}`);
      return false;
    }
  }
  
  /**
   * Send a message using the API.
   * 
   * @param {string} message - Message to send
   * @returns {Promise<boolean>} True if message sent successfully, False otherwise
   * @private
   */
  _sendMessageApi = retryOnException(
    async (message) => {
      if (!this.conversationId) {
        throw new Error("No active conversation");
      }
      
      const url = `${this.config.url}/api/conversation/${this.conversationId}/message`;
      const data = {
        content: message,
        role: "user"
      };
      
      const response = await this.session.post(url, data);
      return true;
    },
    {
      maxRetries: this.config.retryCount || 3,
      retryDelay: this.config.retryDelay || 2000,
      retryOn: [axios.AxiosError]
    }
  );
  
  /**
   * Get a response using Puppeteer.
   * 
   * @param {number} timeout - Maximum time to wait for a response in milliseconds
   * @returns {Promise<string|null>} Response text or null if no response received
   * @private
   */
  async _getResponsePuppeteer(timeout) {
    try {
      // Wait for the response to appear
      const responseSelector = "div.assistant-message, div.response-content";
      
      // Wait for the response to stop changing (indicating it's complete)
      let lastResponse = null;
      const startTime = Date.now();
      
      while (Date.now() - startTime < timeout) {
        try {
          // Wait for the response element to be present
          await this.page.waitForSelector(responseSelector, { timeout: 5000 });
          
          // Get the current response text
          const currentResponse = await this.page.evaluate((selector) => {
            return document.querySelector(selector).innerHTML;
          }, responseSelector);
          
          // If the response hasn't changed for 2 seconds, consider it complete
          if (currentResponse === lastResponse) {
            // Convert HTML to Markdown
            return convertHtmlToMarkdown(currentResponse);
          }
          
          // Update last response
          lastResponse = currentResponse;
          
          // Wait a bit before checking again
          await this.page.waitForTimeout(2000);
        } catch (error) {
          // Response element not found yet, continue waiting
          await this.page.waitForTimeout(1000);
        }
      }
      
      // Timeout reached
      logger.warning(`Timeout reached while waiting for response`);
      return lastResponse ? convertHtmlToMarkdown(lastResponse) : null;
    } catch (error) {
      logger.error(`Error getting response with Puppeteer: ${error.message}`);
      return null;
    }
  }
  
  /**
   * Get a response using the API.
   * 
   * @param {number} timeout - Maximum time to wait for a response in milliseconds
   * @returns {Promise<string|null>} Response text or null if no response received
   * @private
   */
  _getResponseApi = retryOnException(
    async (timeout) => {
      if (!this.conversationId) {
        throw new Error("No active conversation");
      }
      
      const url = `${this.config.url}/api/conversation/${this.conversationId}/messages`;
      
      const startTime = Date.now();
      let lastMessageId = null;
      
      while (Date.now() - startTime < timeout) {
        const response = await this.session.get(url);
        const messages = response.data.messages || [];
        
        // Find the latest assistant message
        for (let i = messages.length - 1; i >= 0; i--) {
          const message = messages[i];
          if (message.role === 'assistant') {
            const messageId = message.id;
            
            // If this is a new message or the message has been updated
            if (messageId !== lastMessageId) {
              lastMessageId = messageId;
              
              // Check if the message is complete
              if (!message.is_incomplete) {
                return message.content || '';
              }
            }
            
            break;
          }
        }
        
        // Wait before checking again
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
      
      // Timeout reached
      logger.warning(`Timeout reached while waiting for response`);
      return null;
    },
    {
      maxRetries: this.config.retryCount || 3,
      retryDelay: this.config.retryDelay || 2000,
      retryOn: [axios.AxiosError]
    }
  );
}

/**
 * Send a message to the DeepWiki chat.
 * 
 * @param {Object} config - Configuration object
 * @param {string} message - Message to send
 * @returns {Promise<boolean>} True if message sent successfully, False otherwise
 */
async function sendMessage(config, message) {
  const chat = new ChatInterface(config);
  
  try {
    await chat.connect();
    const result = await chat.sendMessage(message);
    return result;
  } finally {
    await chat.disconnect();
  }
}

/**
 * Send a message and get a response from the DeepWiki chat.
 * 
 * @param {Object} config - Configuration object
 * @param {string} message - Message to send
 * @param {number} [timeout=60000] - Maximum time to wait for a response in milliseconds
 * @returns {Promise<string|null>} Response text or null if no response received
 */
async function getResponse(config, message, timeout = 60000) {
  const chat = new ChatInterface(config);
  
  try {
    await chat.connect();
    
    if (await chat.sendMessage(message)) {
      return await chat.getResponse(timeout);
    }
    
    return null;
  } finally {
    await chat.disconnect();
  }
}

module.exports = {
  ChatInterface,
  sendMessage,
  getResponse
};