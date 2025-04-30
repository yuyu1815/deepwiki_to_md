import re
from urllib.parse import urlparse

# Path to the navigation_links.md file
nav_links_file = "NavigationExtractionTest/navigation_links.md"

# Read the file content
with open(nav_links_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Regular expression to match deepwiki URLs
deepwiki_pattern = re.compile(r'\[([^\]]+)\]\((https?://deepwiki\.com/[^/]+/[^/]+/[^)]+)\)')


# Function to transform URLs
def transform_url(match):
    title = match.group(1)
    url = match.group(2)
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) > 2:  # Ensure we have enough parts
        # Get the last part of the path (e.g., "2-code-execution-pipeline")
        last_part = path_parts[-1]
        return f"[{title}](md/{last_part})"
    return f"[{title}]({url})"  # Return unchanged if not matching expected format


# Apply the transformation
modified_content = deepwiki_pattern.sub(transform_url, content)

# Write the modified content back to the file
with open(nav_links_file, 'w', encoding='utf-8') as f:
    f.write(modified_content)

print(f"Transformed URLs in {nav_links_file}")
