"""
Test script to verify that the DeepwikiScraper correctly converts HTML to Markdown
and automatically fixes the links.
"""
import os
import shutil
import tempfile
from deepwiki_to_md.deepwiki_to_md import DeepwikiScraper

def test_scraper():
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a DeepwikiScraper instance with the temporary directory as output
        scraper = DeepwikiScraper(output_dir=temp_dir)
        
        # Create a simple HTML content with links
        html_content = """
        <html>
        <body>
            <main>
                <article>
                    <h1>Test Page</h1>
                    <p>This is a test page with links:</p>
                    <ul>
                        <li><a href="https://example.com/file1.py">file1.py</a></li>
                        <li><a href="https://example.com/file2.py">file2.py</a></li>
                    </ul>
                </article>
            </main>
        </body>
        </html>
        """
        
        # Extract the main content
        main_content = scraper.extract_content(html_content, "https://example.com")
        
        # Convert to Markdown
        markdown = scraper.html_to_markdown(main_content)
        
        # Save the Markdown content
        scraper.save_markdown("test", "Test Page", markdown, "test")
        
        # Check if the markdown file was created
        md_file_path = os.path.join(temp_dir, "test", "md", "Test_Page.md")
        if os.path.exists(md_file_path):
            print(f"Markdown file created: {md_file_path}")
            
            # Read the content of the markdown file
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check if the links were fixed
            if "[file1.py]()" in content and "[file2.py]()" in content:
                print("Links were successfully fixed!")
            else:
                print("Links were not fixed properly.")
                print("Content:", content)
        else:
            print(f"Markdown file was not created at {md_file_path}")
    
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_scraper()