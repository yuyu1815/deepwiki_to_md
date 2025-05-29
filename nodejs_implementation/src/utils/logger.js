/**
 * Logger Utility for DeepWiki to Markdown Converter
 * 
 * This module provides logging functionality for the DeepWiki to Markdown converter.
 */

const winston = require('winston');

// Create logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.printf(({ level, message, timestamp }) => {
      return `${timestamp} - ${level.toUpperCase()}: ${message}`;
    })
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    })
  ]
});

/**
 * Set the logging level.
 * 
 * @param {string} level - Logging level (error, warn, info, verbose, debug, silly)
 */
function setLogLevel(level) {
  logger.level = level;
}

/**
 * Add a file transport to the logger.
 * 
 * @param {string} filename - Path to the log file
 * @param {string} [level='info'] - Logging level for the file
 */
function addFileTransport(filename, level = 'info') {
  logger.add(new winston.transports.File({
    filename,
    level,
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.json()
    )
  }));
}

module.exports = {
  logger,
  setLogLevel,
  addFileTransport
};