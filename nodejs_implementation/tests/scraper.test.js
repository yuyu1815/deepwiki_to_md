/**
 * Test module for the scraper functionality.
 * 
 * This module contains tests for the scraper components of the deepwiki-to-md package.
 */

const path = require('path');
const fs = require('fs');
const os = require('os');
const { expect } = require('chai');
const sinon = require('sinon');
const axios = require('axios');

const { Config } = require('../src/models/config');
const { DeepwikiScraper } = require('../src/scraper/deepwiki-scraper');
const { DirectMarkdownScraper } = require('../src/scraper/direct-markdown-scraper');

describe('DirectMarkdownScraper', () => {
  let scraper;
  let tempDir;
  let config;
  
  beforeEach(() => {
    // Create a temporary directory for testing
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'deepwiki-test-'));
    
    // Create a configuration
    config = new Config({
      url: 'https://example.com/wiki',
      libraryName: 'test_library',
      outputDir: tempDir
    });
    
    // Create a scraper
    scraper = new DirectMarkdownScraper(config);
  });
  
  afterEach(() => {
    // Clean up temporary directory
    fs.rmSync(tempDir, { recursive: true, force: true });
    
    // Restore all stubs
    sinon.restore();
  });
  
  describe('extractNavigation', () => {
    it('should extract navigation items from Markdown content', () => {
      // Mock content with links
      const content = `
      # Test Page
      
      This is a [link to page 1](page1.md) and [another link](https://example.com/page2).
      
      ## Section
      
      More [links](relative/path.md) here.
      `;
      
      // Test navigation extraction
      const navItems = scraper.extractNavigation(content);
      
      // Verify results
      expect(navItems).to.have.lengthOf(3);
      expect(navItems[0].title).to.equal('link to page 1');
      expect(navItems[0].url).to.equal('https://example.com/wiki/page1.md');
      expect(navItems[1].title).to.equal('another link');
      expect(navItems[1].url).to.equal('https://example.com/page2');
      expect(navItems[2].title).to.equal('links');
      expect(navItems[2].url).to.equal('https://example.com/wiki/relative/path.md');
    });
  });
  
  describe('_extractTitle', () => {
    it('should extract title from Markdown content with heading', () => {
      const contentWithHeading = '# Page Title\n\nContent here.';
      const title = scraper._extractTitle(contentWithHeading);
      expect(title).to.equal('Page Title');
    });
    
    it('should return default title for Markdown content without heading', () => {
      const contentWithoutHeading = 'Content without heading.';
      const title = scraper._extractTitle(contentWithoutHeading);
      expect(title).to.equal('Untitled Document');
    });
  });
  
  describe('scrape', () => {
    it('should scrape content from a URL', async () => {
      // Stub the _fetchContent method
      const fetchContentStub = sinon.stub(scraper, '_fetchContent');
      fetchContentStub.resolves('# Test Page\n\nThis is test content.');
      
      // Stub the extractNavigation method to return no navigation items
      const extractNavigationStub = sinon.stub(scraper, 'extractNavigation');
      extractNavigationStub.returns([]);
      
      // Call the method
      const results = await scraper.scrape();
      
      // Verify results
      expect(results).to.have.lengthOf(1);
      expect(results[0].title).to.equal('Test Page');
      expect(results[0].content).to.equal('# Test Page\n\nThis is test content.');
      expect(results[0].url).to.equal('https://example.com/wiki');
      expect(results[0].library).to.equal('test_library');
    });
  });
});

describe('DeepwikiScraper', () => {
  let scraper;
  let tempDir;
  let config;
  
  beforeEach(() => {
    // Create a temporary directory for testing
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'deepwiki-test-'));
    
    // Create a configuration
    config = new Config({
      url: 'https://example.com/wiki',
      libraryName: 'test_library',
      outputDir: tempDir
    });
    
    // Create a scraper
    scraper = new DeepwikiScraper(config);
  });
  
  afterEach(() => {
    // Clean up temporary directory
    fs.rmSync(tempDir, { recursive: true, force: true });
    
    // Restore all stubs
    sinon.restore();
  });
  
  describe('scrape', () => {
    it('should scrape and save content', async () => {
      // Stub the direct scraper's scrape method
      const directScrapeStub = sinon.stub(scraper.directScraper, 'scrape');
      directScrapeStub.resolves([
        {
          title: 'Page 1',
          content: '# Page 1\n\nContent for page 1.',
          url: 'https://example.com/wiki/page1',
          library: 'test_library'
        },
        {
          title: 'Page 2',
          content: '# Page 2\n\nContent for page 2.',
          url: 'https://example.com/wiki/page2',
          library: 'test_library'
        }
      ]);
      
      // Call the method
      const results = await scraper.scrape();
      
      // Verify results
      expect(results).to.have.lengthOf(2);
      
      // Check that files were created
      const page1Path = path.join(tempDir, 'test_library', 'Page_1.md');
      const page2Path = path.join(tempDir, 'test_library', 'Page_2.md');
      
      expect(fs.existsSync(page1Path)).to.be.true;
      expect(fs.existsSync(page2Path)).to.be.true;
      
      // Check file contents
      const page1Content = fs.readFileSync(page1Path, 'utf8');
      const page2Content = fs.readFileSync(page2Path, 'utf8');
      
      expect(page1Content).to.equal('# Page 1\n\nContent for page 1.');
      expect(page2Content).to.equal('# Page 2\n\nContent for page 2.');
    });
  });
});