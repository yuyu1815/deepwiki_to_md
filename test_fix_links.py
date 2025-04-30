import os

from deepwiki_to_md.fix_markdown_links import fix_markdown_links

# Path to the directory containing markdown files
md_directory = os.path.join(os.getcwd(), "NavigationExtractionTest", "python", "md")

print(f"Starting to fix markdown links in {md_directory}")
fix_markdown_links(md_directory)
print("Finished fixing markdown links")
