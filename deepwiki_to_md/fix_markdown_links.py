import logging
import os
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_markdown_links(directory):
    """
    Find all markdown files in the specified directory and replace links with URLs
    with links with empty parentheses.
    
    Args:
        directory (str): The directory containing markdown files to process
    """
    # Check if directory exists
    if not os.path.isdir(directory):
        logger.error(f"Directory not found: {directory}")
        return
    
    # Find all markdown files in the directory
    # ディレクトリ内のすべてのマークダウンファイルを検索
    md_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    logger.info(f"Found {len(md_files)} markdown files to process")

    # Regular expression to match markdown links containing URLs
    # This pattern matches [text](url) where url is not empty
    # URLを含むマークダウンリンクに一致する正規表現
    # このパターンは [text](url) に一致し、urlは空ではありません
    link_pattern = re.compile(r'\[([^\]]+)\]\((?![s\)])[^\)]+\)')

    # Process each file
    # 各ファイルを処理
    # Process each file
    for file_path in md_files:
        logger.info(f"Processing {file_path}")
        
        # Read file content
        # ファイルの内容を読み込む
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count original links
        # 元のリンク数をカウント
        # Count the number of original links
        original_links = len(link_pattern.findall(content))
        
        # Replace links with URLs with links with empty parentheses
        # URL付きのリンクを空の括弧を持つリンクに置き換える
        # Replace links with URLs with links having empty parentheses
        modified_content = link_pattern.sub(r'[\1]()', content)
        
        # Count modified links
        # 変更されたリンク数をカウント
        # Count the number of modified links
        modified_links = original_links - len(link_pattern.findall(modified_content))
        
        # Write modified content back to file
        # 変更された内容をファイルに書き戻す
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        logger.info(f"Modified {modified_links} links in {file_path}")

if __name__ == "__main__":
    # Path to the directory containing markdown files
    # マークダウンファイルを含むディレクトリへのパス
    # Path to the directory containing markdown files
    md_directory = os.path.join(os.getcwd(), "Documents", "cpython", "md")
    
    logger.info(f"Starting to fix markdown links in {md_directory}")
    fix_markdown_links(md_directory)
