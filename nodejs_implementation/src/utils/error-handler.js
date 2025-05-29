/**
 * Error Handling Utility for DeepWiki to Markdown Converter
 * 
 * This module provides error handling functionality for the DeepWiki to Markdown converter.
 */

const { logger } = require('./logger');
const { getLocalizedMessage } = require('./localization');

/**
 * Set up global error handling.
 * 
 * This function sets up global exception handlers and other error handling mechanisms.
 */
function setupErrorHandling() {
  // Handle uncaught exceptions
  process.on('uncaughtException', (error) => {
    logger.error(getLocalizedMessage('uncaught_exception'));
    logger.error(error.stack);
    process.exit(1);
  });
  
  // Handle unhandled promise rejections
  process.on('unhandledRejection', (reason, promise) => {
    logger.error(getLocalizedMessage('unhandled_rejection'));
    logger.error(reason);
    process.exit(1);
  });
  
  logger.debug('Global error handling set up');
}

/**
 * Handle a request error.
 * 
 * @param {Error} error - The request error
 * @param {string} url - The URL that caused the error
 */
function handleRequestError(error, url) {
  if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
    logger.error(getLocalizedMessage('connection_error', { url }));
  } else if (error.code === 'ETIMEDOUT') {
    logger.error(getLocalizedMessage('timeout_error', { url }));
  } else if (error.response) {
    const statusCode = error.response.status || 'unknown';
    logger.error(getLocalizedMessage('http_error', { url, statusCode }));
  } else {
    logger.error(getLocalizedMessage('request_error', { url, error: error.message }));
  }
}

/**
 * Retry a function on exception.
 * 
 * @param {Function} func - Function to retry
 * @param {Object} options - Retry options
 * @param {number} [options.maxRetries=3] - Maximum number of retries
 * @param {number} [options.retryDelay=2000] - Delay between retries in milliseconds
 * @param {Array<Function>} [options.retryOn=[Error]] - Errors to retry on
 * @param {Function} [options.onRetry] - Function to call on retry
 * @returns {Function} Wrapped function
 */
function retryOnException(func, options = {}) {
  const {
    maxRetries = 3,
    retryDelay = 2000,
    retryOn = [Error],
    onRetry
  } = options;
  
  return async function(...args) {
    let lastError;
    
    for (let retry = 0; retry <= maxRetries; retry++) {
      try {
        return await func(...args);
      } catch (error) {
        lastError = error;
        
        // Check if we should retry this error
        const shouldRetry = retryOn.some(errorType => error instanceof errorType);
        
        if (shouldRetry && retry < maxRetries) {
          if (onRetry) {
            onRetry(error, retry + 1);
          } else {
            logger.warn(
              getLocalizedMessage('retry_attempt', {
                function: func.name || 'anonymous',
                retry: retry + 1,
                maxRetries,
                error: error.message
              })
            );
          }
          
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, retryDelay));
        } else if (retry === maxRetries) {
          logger.error(
            getLocalizedMessage('max_retries_exceeded', {
              function: func.name || 'anonymous',
              maxRetries,
              error: error.message
            })
          );
          throw error;
        } else {
          throw error;
        }
      }
    }
  };
}

/**
 * Measure and log the execution time of a function.
 * 
 * @param {Function} func - Function to measure
 * @returns {Function} Wrapped function
 */
function logExecutionTime(func) {
  return async function(...args) {
    const startTime = process.hrtime();
    const result = await func(...args);
    const [seconds, nanoseconds] = process.hrtime(startTime);
    const timeInMs = (seconds * 1000) + (nanoseconds / 1000000);
    
    logger.debug(
      getLocalizedMessage('execution_time', {
        function: func.name || 'anonymous',
        time: timeInMs.toFixed(2)
      })
    );
    
    return result;
  };
}

module.exports = {
  setupErrorHandling,
  handleRequestError,
  retryOnException,
  logExecutionTime
};