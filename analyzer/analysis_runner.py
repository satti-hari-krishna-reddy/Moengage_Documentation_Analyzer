import logging 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

from .readability_analyzer import analyze_readability 
from .structure_analyzer import analyze_structure 
from .completeness_analyzer import analyze_completeness 
from .style_analyzer import analyze_style 

def run_full_analysis(url: str, document_text: str) -> dict:
    """
    Runs all analyses on the document text and returns a structured report.
    """
    report = {
        "url_analyzed": url,
        "readability": None,
        "structure_and_flow": None,
        "completeness_of_information": None,
        "style_guidelines": None,
        "errors": [] # To capture any errors during analysis sub-steps
    }

    try:
        logger.info(f"Starting readability analysis for {url}")
        report["readability"] = analyze_readability(document_text) 
        logger.info(f"Completed readability analysis for {url}")
    except Exception as e:
        logger.error(f"Readability analysis failed in runner: {e}", exc_info=True)
        report["errors"].append(f"Readability analysis failed: {str(e)}")

    try:
        logger.info(f"Starting structure and flow analysis for {url}")
        report["structure_and_flow"] = analyze_structure(document_text)
        logger.info(f"Completed structure and flow analysis for {url}")
    except Exception as e:
        logger.error(f"Structure and flow analysis failed in runner: {e}", exc_info=True)
        report["errors"].append(f"Structure and flow analysis failed: {str(e)}")

    try:
        logger.info(f"Starting completeness analysis for {url}")
        report["completeness_of_information"] = analyze_completeness(document_text)
        logger.info(f"Completed completeness analysis for {url}")
    except Exception as e:
        logger.error(f"Completeness analysis failed in runner: {e}", exc_info=True)
        report["errors"].append(f"Completeness of information analysis failed: {str(e)}")

    try:
        logger.info(f"Starting style guidelines analysis for {url}")
        report["style_guidelines"] = analyze_style(document_text) 
        logger.info(f"Completed style guidelines analysis for {url}")
    except Exception as e:
        logger.error(f"Style guidelines analysis failed in runner: {e}", exc_info=True)
        report["errors"].append(f"Style guidelines analysis failed: {str(e)}")

    return report
