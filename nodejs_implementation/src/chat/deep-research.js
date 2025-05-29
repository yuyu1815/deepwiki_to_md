/**
 * Deep Research Mode for DeepWiki to Markdown Converter
 * 
 * This module provides functionality for conducting deep research using the DeepWiki chat.
 */

const path = require('path');
const fs = require('fs');
const { logger } = require('../utils/logger');
const { ChatInterface } = require('./chat-interface');
const { saveMarkdownFile, saveJsonFile, saveYamlFile } = require('../utils/file-io');
const { convertMarkdownToYaml, yamlToString } = require('../converters/md-to-yaml');

/**
 * Deep Research Mode for the DeepWiki chat.
 * 
 * This class provides methods for conducting deep research using the DeepWiki chat,
 * including multi-turn conversations and saving results in various formats.
 */
class DeepResearchMode {
  /**
   * Initialize the deep research mode.
   * 
   * @param {Object} config - Configuration object
   */
  constructor(config) {
    this.config = config;
    this.chat = null;
    this.conversationHistory = [];
    this.researchResults = [];
    
    logger.debug("Initialized DeepResearchMode");
  }
  
  /**
   * Start a deep research session.
   * 
   * @returns {Promise<boolean>} True if session started successfully, False otherwise
   */
  async startSession() {
    try {
      // Initialize chat interface
      this.chat = new ChatInterface(this.config);
      const success = await this.chat.connect();
      
      if (success) {
        logger.info("Started deep research session");
        
        // Send initial system message if configured
        const systemPrompt = this.config.systemPrompt;
        if (systemPrompt) {
          this._addToHistory("system", systemPrompt);
          logger.debug(`Set system prompt: ${systemPrompt}`);
        }
      }
      
      return success;
    } catch (error) {
      logger.error(`Error starting deep research session: ${error.message}`);
      return false;
    }
  }
  
  /**
   * End the deep research session.
   * 
   * @returns {Promise<void>}
   */
  async endSession() {
    try {
      if (this.chat) {
        await this.chat.disconnect();
        this.chat = null;
      }
      
      logger.info("Ended deep research session");
    } catch (error) {
      logger.error(`Error ending deep research session: ${error.message}`);
    }
  }
  
  /**
   * Ask a question in the deep research session.
   * 
   * @param {string} question - Question to ask
   * @param {number} [timeout=120000] - Maximum time to wait for a response in milliseconds
   * @returns {Promise<string|null>} Response text or null if no response received
   */
  async askQuestion(question, timeout = 120000) {
    if (!this.chat) {
      logger.error("No active chat session");
      return null;
    }
    
    try {
      // Send the question
      logger.info(`Asking question: ${question}`);
      this._addToHistory("user", question);
      
      if (!await this.chat.sendMessage(question)) {
        logger.error("Failed to send question");
        return null;
      }
      
      // Get the response
      const response = await this.chat.getResponse(timeout);
      
      if (response) {
        logger.info("Received response");
        this._addToHistory("assistant", response);
        this.researchResults.push({
          question,
          response
        });
      } else {
        logger.warning("No response received");
      }
      
      return response;
    } catch (error) {
      logger.error(`Error asking question: ${error.message}`);
      return null;
    }
  }
  
  /**
   * Conduct research by asking a series of questions.
   * 
   * @param {Array<string>} questions - List of questions to ask
   * @param {number} [timeout=120000] - Maximum time to wait for each response in milliseconds
   * @returns {Promise<Array<Object>>} List of question-response pairs
   */
  async conductResearch(questions, timeout = 120000) {
    const results = [];
    
    // Start the session
    if (!await this.startSession()) {
      logger.error("Failed to start research session");
      return results;
    }
    
    try {
      for (let i = 0; i < questions.length; i++) {
        const question = questions[i];
        logger.info(`Research question ${i+1}/${questions.length}`);
        
        const response = await this.askQuestion(question, timeout);
        
        if (response) {
          results.push({
            question,
            response
          });
        }
        
        // Wait between questions to avoid rate limiting
        if (i < questions.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
      }
    } finally {
      // End the session
      await this.endSession();
    }
    
    return results;
  }
  
  /**
   * Save research results in various formats.
   * 
   * @param {string} outputDir - Directory to save results in
   * @param {Array<string>} [formats=['md', 'json', 'yaml']] - List of formats to save results in
   * @returns {Promise<Object>} Dictionary mapping format to list of saved file paths
   */
  async saveResults(outputDir, formats = ['md', 'json', 'yaml']) {
    const savedFiles = {};
    formats.forEach(fmt => { savedFiles[fmt] = []; });
    
    // Create output directory if it doesn't exist
    fs.mkdirSync(outputDir, { recursive: true });
    
    // Save each result
    for (let i = 0; i < this.researchResults.length; i++) {
      const result = this.researchResults[i];
      const question = result.question;
      const response = result.response;
      
      // Create a filename based on the question
      const baseFilename = this._createFilename(question, i);
      
      // Save in each requested format
      for (const fmt of formats) {
        if (fmt.toLowerCase() === 'md') {
          // Save as Markdown
          const filename = `${baseFilename}.md`;
          const filepath = path.join(outputDir, filename);
          
          const content = `# ${question}\n\n${response}`;
          if (saveMarkdownFile(filepath, content)) {
            savedFiles.md.push(filepath);
          }
        } else if (fmt.toLowerCase() === 'json') {
          // Save as JSON
          const filename = `${baseFilename}.json`;
          const filepath = path.join(outputDir, filename);
          
          if (saveJsonFile(filepath, result)) {
            savedFiles.json.push(filepath);
          }
        } else if (fmt.toLowerCase() === 'yaml') {
          // Save as YAML
          const filename = `${baseFilename}.yaml`;
          const filepath = path.join(outputDir, filename);
          
          // Convert to YAML structure
          const yamlData = convertMarkdownToYaml(
            response,
            question,
            null,
            { includeRawContent: true }
          );
          
          // Convert to YAML string and save
          const yamlStr = yamlToString(yamlData);
          
          fs.writeFileSync(filepath, yamlStr, 'utf8');
          savedFiles.yaml.push(filepath);
        }
      }
    }
    
    // Save conversation history
    if (this.conversationHistory.length > 0) {
      const historyFile = path.join(outputDir, "conversation_history.json");
      saveJsonFile(historyFile, { history: this.conversationHistory });
    }
    
    return savedFiles;
  }
  
  /**
   * Add a message to the conversation history.
   * 
   * @param {string} role - Role of the message sender (user, assistant, system)
   * @param {string} content - Message content
   * @private
   */
  _addToHistory(role, content) {
    this.conversationHistory.push({
      role,
      content,
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Create a filename based on a question.
   * 
   * @param {string} question - Question to create filename from
   * @param {number} index - Index of the question
   * @returns {string} Sanitized filename
   * @private
   */
  _createFilename(question, index) {
    // Truncate and sanitize the question for use as a filename
    let sanitized = question.replace(/[<>:"/\\|?*]/g, '_');
    sanitized = sanitized.replace(/\s+/g, '_').toLowerCase();
    
    // Truncate if too long
    if (sanitized.length > 50) {
      sanitized = sanitized.substring(0, 47) + '...';
    }
    
    // Add index to ensure uniqueness
    return `${index+1}_${sanitized}`;
  }
}

/**
 * Conduct deep research and save results.
 * 
 * @param {Object} config - Configuration object
 * @param {Array<string>} questions - List of questions to ask
 * @param {string} [outputDir=null] - Directory to save results in
 * @param {Array<string>} [formats=['md', 'json', 'yaml']] - List of formats to save results in
 * @param {number} [timeout=120000] - Maximum time to wait for each response in milliseconds
 * @returns {Promise<Object>} Research results and saved file information
 */
async function conductResearch(
  config,
  questions,
  outputDir = null,
  formats = ['md', 'json', 'yaml'],
  timeout = 120000
) {
  const research = new DeepResearchMode(config);
  
  // Conduct research
  const results = await research.conductResearch(questions, timeout);
  
  // Save results if output directory is provided
  let savedFiles = {};
  if (outputDir) {
    savedFiles = await research.saveResults(outputDir, formats);
  }
  
  return {
    results,
    savedFiles
  };
}

module.exports = {
  DeepResearchMode,
  conductResearch
};