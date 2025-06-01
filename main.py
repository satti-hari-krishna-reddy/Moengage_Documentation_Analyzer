import os
import sys
import logging
import json
from utils.content_fetcher import ContentFetcher
from analyzer.analysis_runner import run_full_analysis
from rich import print as rprint
from rich.console import Console
from rich.syntax import Syntax

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("---------------------------------------------------------------------------")
    logger.warning("GEMINI_API_KEY environment variable is not set.")
    logger.warning("Please set your GEMINI_API_KEY to enable full analysis.")
    logger.warning("---------------------------------------------------------------------------")
    sys.exit(1)

def main():
    url = input("Enter the MoEngage documentation URL: ").strip()
    if not url:
        logger.error("No URL provided. Exiting.")
        return

    logger.info(f"Starting analysis for URL: {url}")

    try:
        logger.info("Fetching content...")
        content = ContentFetcher.get_content(url)
        logger.info("Content fetched successfully.")

        if not content.strip():
            logger.warning("Fetched content is empty. Analysis might not be meaningful.")

        logger.info("Running analysis modules...")
        analysis_report = run_full_analysis(url, content)
        logger.info("Analysis complete.")

        # Pretty-print JSON with rich
        console = Console()
        console.rule("[bold green]JSON Report[/]")
        json_str = json.dumps(analysis_report, indent=2, ensure_ascii=False)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        console.print(syntax)
        console.rule()

        try:
            with open("analysis_report.json", "w", encoding="utf-8") as f_json:
                json.dump(analysis_report, f_json, indent=2, ensure_ascii=False)
            logger.info("JSON report saved to analysis_report.json")

            with open("scraped_text.txt", "w", encoding="utf-8") as f_md:
                f_md.write(content.strip() + "\n")

        except IOError as e:
            logger.error(f"Error saving report files: {e}")

    except Exception as e:
        logger.error(f"An error occurred in the main process: {e}", exc_info=True)

if __name__ == "__main__":
    main()