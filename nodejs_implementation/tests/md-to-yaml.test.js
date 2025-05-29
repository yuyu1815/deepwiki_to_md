/**
 * Test module for Markdown to YAML conversion.
 * 
 * This module tests the functionality of converting Markdown content to YAML format.
 */

const { MarkdownToYAMLConverter, convertMarkdownToYaml, yamlToString } = require('../src/converters/md-to-yaml');
const yaml = require('js-yaml');

describe('MarkdownToYAMLConverter', () => {
  let converter;

  beforeEach(() => {
    // Create a new converter instance with default options
    converter = new MarkdownToYAMLConverter();
  });

  describe('convert', () => {
    it('should convert Markdown to YAML with metadata and content', () => {
      // Sample Markdown content
      const markdown = `---
title: Test Document
author: Test Author
date: 2023-01-01
---

# Introduction

This is a test document with some Markdown content.

## Section 1

This is section 1 content.

- List item 1
- List item 2

## Section 2

This is section 2 content.

\`\`\`python
def hello_world():
    print("Hello, World!")
\`\`\`

### Subsection 2.1

This is a subsection.

[Link to external site](https://example.com)
`;

      // Convert Markdown to YAML
      const yamlData = converter.convert(markdown);

      // Check that the YAML data has the expected structure
      expect(yamlData).toHaveProperty('metadata');
      expect(yamlData).toHaveProperty('content');

      // Check metadata
      expect(yamlData.metadata).toHaveProperty('title', 'Test Document');
      expect(yamlData.metadata).toHaveProperty('author', 'Test Author');
      expect(yamlData.metadata).toHaveProperty('date', '2023-01-01');

      // Check content structure
      expect(yamlData.content).toHaveProperty('Introduction');
      expect(yamlData.content).toHaveProperty('Section 1');
      expect(yamlData.content).toHaveProperty('Section 2');

      // Check that content is properly nested
      expect(yamlData.content['Section 1']).toHaveProperty('content');
      expect(yamlData.content['Section 2']).toHaveProperty('content');

      // Check that subsections are properly nested
      expect(yamlData.content['Section 2']).toHaveProperty('Subsection 2.1');
    });

    it('should include title and URL when provided', () => {
      const markdown = '# Some content';
      const title = 'Custom Title';
      const url = 'https://example.com/page';

      const yamlData = converter.convert(markdown, title, url);

      expect(yamlData.metadata).toHaveProperty('title', 'Custom Title');
      expect(yamlData.metadata).toHaveProperty('url', 'https://example.com/page');
    });

    it('should respect converter options', () => {
      const markdown = '# Heading\n\nContent';

      // Create converter with custom options
      const customConverter = new MarkdownToYAMLConverter({
        includeMetadata: false,
        includeRawContent: true
      });

      const yamlData = customConverter.convert(markdown);

      // Should not include metadata
      expect(yamlData).not.toHaveProperty('metadata');

      // Should include raw content
      expect(yamlData).toHaveProperty('rawContent', markdown);
    });
  });

  describe('_extractMetadata', () => {
    it('should extract metadata from YAML frontmatter', () => {
      const markdown = `---
title: Test Document
author: Test Author
date: 2023-01-01
---

# Content`;

      const metadata = converter._extractMetadata(markdown);

      expect(metadata).toHaveProperty('title', 'Test Document');
      expect(metadata).toHaveProperty('author', 'Test Author');
      expect(metadata).toHaveProperty('date', '2023-01-01');
    });

    it('should extract title from first heading if not in frontmatter', () => {
      const markdown = '# Document Title\n\nContent';

      const metadata = converter._extractMetadata(markdown);

      expect(metadata).toHaveProperty('title', 'Document Title');
    });

    it('should extract metadata from key-value pairs in content', () => {
      const markdown = '# Document\n\nauthor: John Doe\ndate: 2023-01-01\n\nContent';

      const metadata = converter._extractMetadata(markdown);

      expect(metadata).toHaveProperty('author', 'John Doe');
      expect(metadata).toHaveProperty('date', '2023-01-01');
    });
  });
});

describe('convertMarkdownToYaml', () => {
  it('should convert Markdown to YAML using the converter', () => {
    const markdown = '# Test\n\nContent';

    const yamlData = convertMarkdownToYaml(markdown);

    expect(yamlData).toHaveProperty('metadata');
    expect(yamlData).toHaveProperty('content');
    expect(yamlData.metadata).toHaveProperty('title', 'Test');
  });

  it('should accept custom options', () => {
    const markdown = '# Test\n\nContent';

    const yamlData = convertMarkdownToYaml(markdown, null, null, {
      includeRawContent: true
    });

    expect(yamlData).toHaveProperty('rawContent', markdown);
  });
});

describe('yamlToString', () => {
  it('should convert YAML data to a string', () => {
    const yamlData = {
      metadata: {
        title: 'Test Document'
      },
      content: {
        Introduction: {
          content: [{ type: 'paragraph', text: 'This is an introduction.' }]
        }
      }
    };

    const yamlString = yamlToString(yamlData);

    // Parse the string back to an object to verify it's valid YAML
    const parsedYaml = yaml.load(yamlString);

    expect(parsedYaml).toEqual(yamlData);
  });

  it('should respect custom options', () => {
    const yamlData = { key: 'value' };

    const yamlString = yamlToString(yamlData, { indent: 4 });

    // Check that the indentation is 4 spaces
    expect(yamlString).toContain('key:');
    expect(yamlString).toContain('    value');
  });
});
