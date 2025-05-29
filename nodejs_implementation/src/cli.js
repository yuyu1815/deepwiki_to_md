#!/usr/bin/env node

/**
 * Command Line Interface for DeepWiki to Markdown Converter
 * 
 * This module provides the command-line interface for the DeepWiki to Markdown converter.
 * It parses command-line arguments and delegates to the appropriate functionality.
 */

const { program } = require('commander');
const path = require('path');
const fs = require('fs');
const { scrapeAndConvert } = require('./index');
const { logger } = require('./utils/logger');
const { Config } = require('./models/config');
const { getLocalizedMessage, setLanguage } = require('./utils/localization');

// Set up version and description
program
  .name('deepwiki-to-md')
  .description(getLocalizedMessage('cli_description'))
  .version('0.3.2');

// Define command-line options
program
  .requiredOption('-u, --url <url>', getLocalizedMessage('url_help'))
  .requiredOption('-l, --library <name>', getLocalizedMessage('library_help'))
  .option('-o, --output <directory>', getLocalizedMessage('output_help'), './output')
  .option('-v, --verbose', getLocalizedMessage('verbose_help'))
  .option('--lang <language>', getLocalizedMessage('language_help'), 'en');

// Parse arguments
program.parse(process.argv);
const options = program.opts();

// Set language
setLanguage(options.lang);

// Configure logging level
if (options.verbose) {
  logger.level = 'debug';
  logger.debug(getLocalizedMessage('verbose_mode_enabled'));
}

/**
 * Main function to run the CLI.
 */
async function main() {
  try {
    // Create configuration
    const config = new Config({
      url: options.url,
      libraryName: options.library,
      outputDir: options.output,
      verbose: options.verbose
    });
    
    // Run scraper
    logger.info(getLocalizedMessage('scraping_started', { url: options.url }));
    const results = await scrapeAndConvert(config);
    
    // Log results
    logger.info(getLocalizedMessage('scraping_complete', { count: results.length }));
    
    // Return success
    process.exit(0);
  } catch (error) {
    logger.error(getLocalizedMessage('unexpected_error', { error: error.message }));
    if (options.verbose) {
      logger.error(error.stack);
    }
    process.exit(1);
  }
}

// Run the main function
main();