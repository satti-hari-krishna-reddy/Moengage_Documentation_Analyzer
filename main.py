# server.py
import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.content_fetcher import ContentFetcher
from analyzer.analysis_runner import run_full_analysis
from agent2 import revise_text  

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY environment variable is not set. Exiting.")
    exit(1)

app = Flask(__name__)
CORS(app)

@app.route("/api/v1/analyse", methods=["POST"])
def analyse():
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    logger.info(f"Starting analysis for URL: {url}")
    try:
        content = ContentFetcher.get_content(url)
        if not content.strip():
            logger.warning("Fetched content is empty. Might be a bad URL.")

        analysis_report = run_full_analysis(url, content)

        response = {
            "url": url,
            "analysis": analysis_report,
            "raw_text": content.strip()
        }
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/revise", methods=["POST"])
def revise():
    data = request.get_json()
    raw_text = data.get("text", "").strip()
    analysis_data = data.get("analysis")

    if not raw_text or not analysis_data:
        return jsonify({"error": "Both text and analysis data are required"}), 400

    try:
        revised = revise_text(raw_text, analysis_data)
        return jsonify({"revised_text": revised}), 200
    except Exception as e:
        logger.error(f"Revision error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
