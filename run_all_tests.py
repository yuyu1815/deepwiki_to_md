import logging
import os
import subprocess
import sys
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_test(test_script, report_file):
    """Run a test script and append results to the report file."""
    print(f"\n{'=' * 80}")
    print(f"Running test: {test_script}")
    print(f"{'=' * 80}")

    # Run the test script and capture output
    start_time = time.time()
    result = subprocess.run([sys.executable, test_script], capture_output=True, text=True)
    end_time = time.time()

    # Determine if the test passed or failed
    passed = result.returncode == 0
    status = "PASS" if passed else "FAIL"
    duration = end_time - start_time

    # Print the output
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    # Append results to the report file
    with open(report_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{'=' * 80}\n")
        f.write(f"Test: {test_script}\n")
        f.write(f"Status: {status}\n")
        f.write(f"Duration: {duration:.2f} seconds\n")
        f.write(f"{'=' * 80}\n\n")
        f.write("STDOUT:\n")
        f.write(result.stdout)
        if result.stderr:
            f.write("\nSTDERR:\n")
            f.write(result.stderr)
        f.write("\n")

    return passed, duration


def create_report_header(report_file):
    """Create the header for the test report."""
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# deepwiki_to_md Test Report\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Test Results Summary\n\n")
        f.write("| Test | Status | Duration |\n")
        f.write("|------|--------|----------|\n")


def update_report_summary(report_file, test_results):
    """Update the summary table in the report."""
    with open(report_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the end of the summary table
    table_start = 0
    for i, line in enumerate(lines):
        if line.startswith("| Test | Status | Duration |"):
            table_start = i
            break

    # Insert the test results into the table
    table_end = table_start + 2  # Skip the header and separator rows
    for test_script, (passed, duration) in test_results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        lines.insert(table_end, f"| {test_script} | {status} | {duration:.2f}s |\n")
        table_end += 1

    # Add overall result
    all_passed = all(passed for passed, _ in test_results.values())
    overall_status = "✅ PASS" if all_passed else "❌ FAIL"
    total_duration = sum(duration for _, duration in test_results.values())
    lines.insert(table_end, f"| **OVERALL** | **{overall_status}** | **{total_duration:.2f}s** |\n")

    # Write the updated report
    with open(report_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def add_feature_descriptions(report_file):
    """Add descriptions of the tested features to the report."""
    with open(report_file, 'a', encoding='utf-8') as f:
        f.write("\n## Tested Features\n\n")

        f.write("### 1. Markdown to YAML Conversion\n")
        f.write("Converts Markdown content to YAML format while preserving formatting. ")
        f.write("Extracts metadata such as headers, links, and structure.\n\n")

        f.write("### 2. Markdown Link Fixing\n")
        f.write("Finds Markdown links in the format [Text](URL) and replaces them with [Text](). ")
        f.write("This is useful for removing external URLs from Markdown files.\n\n")

        f.write("### 3. Main Scraper Functionality\n")
        f.write("Scrapes content from deepwiki sites using different strategies:\n")
        f.write("- DirectMarkdownScraper: Fetches raw Markdown content directly\n")
        f.write("- DirectDeepwikiScraper: Fetches HTML and converts it to Markdown\n\n")

        f.write("### 4. Chat Scraper\n")
        f.write("Uses Selenium to interact with chat interfaces, send messages, and save responses ")
        f.write("in various formats (HTML, Markdown, YAML).\n\n")

        f.write("### 5. Repository Creation Tool\n")
        f.write("Uses Selenium to automate the process of creating repository requests by setting ")
        f.write("an email address and submitting a form.\n\n")


def main():
    """Run all tests and generate a comprehensive report."""
    # Create a directory for test reports
    reports_dir = "test_reports"
    os.makedirs(reports_dir, exist_ok=True)

    # Create a report file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(reports_dir, f"test_report_{timestamp}.md")

    # Create the report header
    create_report_header(report_file)

    # List of test scripts to run
    test_scripts = [
        "test_md_to_yaml.py",
        "test_fix_markdown_links.py",
        "test_scraper.py",
        "test_chat_scraper.py",
        "test_repository_creator.py"
    ]

    # Run each test and collect results
    test_results = {}
    for test_script in test_scripts:
        passed, duration = run_test(test_script, report_file)
        test_results[test_script] = (passed, duration)

    # Update the summary table in the report
    update_report_summary(report_file, test_results)

    # Add feature descriptions
    add_feature_descriptions(report_file)

    # Print the final result
    all_passed = all(passed for passed, _ in test_results.values())
    print(f"\n{'=' * 80}")
    print(f"All tests {'PASSED' if all_passed else 'FAILED'}")
    print(f"Report saved to: {report_file}")
    print(f"{'=' * 80}")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
