import os
import sys
import json
import logging
import difflib
import re
from utils.gemini import generate_with_fallback


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def get_env_api_key() -> str:
    """
    Fetch GEMINI_API_KEY from environment. Exit if it's missing.
    """
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        logger.error("GEMINI_API_KEY environment variable is not set. Aborting.")
        sys.exit(1)
    return key

def load_json_file(filepath: str) -> dict:
    """
    Load and return JSON data from the given filepath. Exit if file not found or parsing fails.
    """
    if not os.path.isfile(filepath):
        logger.error(f"Required file '{filepath}' not found. Aborting.")
        sys.exit(1)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to read/parse JSON from '{filepath}': {e}")
        sys.exit(1)

    return data

def load_text_file(filepath: str) -> str:
    """
    Load and return text content from the given filepath. Exit if file not found.
    """
    if not os.path.isfile(filepath):
        logger.error(f"Required file '{filepath}' not found. Aborting.")
        sys.exit(1)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read text from '{filepath}': {e}")
        sys.exit(1)

def tokenize_sentences(text: str) -> list[str]:
    """
    Simple sentence splitter. Splits on ., !, or ? followed by whitespace.
    Keeps punctuation attached to the sentence.
    """
    parts = re.split(r'(?<=[\.\!\?])\s+', text)
    return parts

def rewrite_via_llm(original: str, instruction: str, api_key: str) -> str:
    """
    Use generate_with_fallback (Gemini) to rewrite a single sentence based on the given instruction.
    If Gemini fails or returns empty, return the original text to avoid data loss.
    """
    prompt = (
        "You are a documentation editor focused on readability.\n"
        "Please rewrite the following sentence based solely on this instruction, and return only the revised sentence:\n\n"
        "Sentence:\n"
        f"\"\"\"{original}\"\"\"\n\n"
        "Instruction:\n"
        f"\"\"\"{instruction}\"\"\"\n"
    )
    try:
        output = generate_with_fallback(prompt, api_key)
        if output and output.parts: 
            llm_text_output = output.text.strip()
            if llm_text_output.startswith("```json"):
                llm_text_output = llm_text_output[7:]
            if llm_text_output.endswith("```"):
                llm_text_output = llm_text_output[:-3]
            return llm_text_output
        else:
            logger.warning("Gemini returned empty for single-sentence rewrite. Keeping original sentence.")
            return original
    except Exception as e:
        logger.error(f"Gemini rewrite_via_llm failed: {e}")
        return original

def call_full_document_llm(text: str, remaining_suggestions: list[dict], api_key: str) -> str:
    """
    Batch all remaining suggestions into a single prompt. Ask Gemini to rewrite the entire document.
    Returns the full revised document if successful; otherwise returns the original text.
    """
    # Build the prompt
    prompt_lines = [
        "You are an expert documentation editor. Below is the current document, followed by edit instructions.\n"
        "Apply each instruction precisely where needed and return the entire revised document. "
        "Keep all existing headings and formatting markers (e.g., '[H1]', '[H2]').\n\n",
        "--- CURRENT DOCUMENT START ---",
        text,
        "--- CURRENT DOCUMENT END ---\n",
        "--- EDIT INSTRUCTIONS START ---"
    ]

    for idx, s in enumerate(remaining_suggestions, start=1):
        desc = s.get("description", "").strip()
        orig = s.get("original", "").strip()
        sugg = s.get("suggestion", "").strip()
        prompt_lines.append(f"{idx}. {desc}")
        prompt_lines.append(f"   Original: \"{orig}\"")
        prompt_lines.append(f"   Suggested rewrite: \"{sugg}\"\n")

    prompt_lines.append("--- EDIT INSTRUCTIONS END ---")
    full_prompt = "\n".join(prompt_lines)

    try:
        result = generate_with_fallback(full_prompt, api_key)
        if result and result.parts: 
            llm_text_output = result.text.strip()

            if llm_text_output.startswith("```json"):
                llm_text_output = llm_text_output[7:]
            if llm_text_output.endswith("```"):
                llm_text_output = llm_text_output[:-3]
            return llm_text_output

        else:
            logger.warning("Gemini returned empty on full-document rewrite. Keeping current text.")
            return text
    except Exception as e:
        logger.error(f"Gemini full-document rewrite failed: {e}")
        return text


def apply_readability_patches(text: str, suggestions: list[dict], api_key: str) -> str:
    """
    Applies readability suggestions in three passes:
     1. Exact string replacement.
     2. Fuzzy matching + single-sentence LLM rewrite.
     3. Full-document LLM fallback for any remaining unapplied suggestions.
    Returns the fully revised text.
    """
    # 1) Mark all suggestions as not yet applied
    for s in suggestions:
        s["applied"] = False

    # 1. Exact Replacement 
    for s in suggestions:
        orig = s.get("original", "")
        new = s.get("suggestion", "")
        if orig and new and orig in text:
            text = text.replace(orig, new)
            s["applied"] = True
            logger.info(f"Exact replacement applied for: '{orig[:30]}...'")

    # 2. Fuzzy Matching Pass
    sentences = tokenize_sentences(text)
    for s in suggestions:
        if s["applied"]:
            continue

        orig = s.get("original", "")
        new = s.get("suggestion", "")
        if not orig or not new:
            continue

        # Find the closest sentence in 'sentences'
        matches = difflib.get_close_matches(orig, sentences, n=1, cutoff=0.75)
        if matches:
            matched_sentence = matches[0]
            instruction = f"Please rewrite for better readability: {new}"
            rewritten_sentence = rewrite_via_llm(matched_sentence, instruction, api_key)
            if rewritten_sentence and rewritten_sentence != matched_sentence:
                text = text.replace(matched_sentence, rewritten_sentence)
                s["applied"] = True
                logger.info(f"Fuzzy match rewrite applied. Matched: '{matched_sentence[:30]}...'")
            else:
                logger.warning(f"Fuzzy matched but no change made for: '{matched_sentence[:30]}...'")

    # 3. Full-Document LLM Fallback 
    remaining = [s for s in suggestions if not s["applied"]]
    if remaining:
        logger.info(f"{len(remaining)} suggestions still unapplied. Invoking full-document LLM fallback.")
        text = call_full_document_llm(text, remaining, api_key)
        # Mark all as applied regardless of LLM result
        for s in remaining:
            s["applied"] = True

    return text


def main():
    api_key = get_env_api_key()

    scraped_path = "scraped_text.txt"
    json_path = "analysis_report.json"

    scraped_text = load_text_file(scraped_path)

    analysis_data = load_json_file(json_path)
    # We expect analysis_data to be a dict, containing a "readability" key with "suggestions"
    suggestions = []
    if "readability" in analysis_data and isinstance(analysis_data["readability"].get("suggestions"), list):
        raw_suggestions = analysis_data["readability"]["suggestions"]
        # Agent 1 would have provided objects with original/suggestion fields.
        # Here, we assume each item is already a dict with the keys: "description", "original", "suggestion".
        for item in raw_suggestions:
            if isinstance(item, dict) and "original" in item and "suggestion" in item:
                suggestions.append({
                    "type": "readability",
                    "description": item.get("description", ""),
                    "original": item["original"],
                    "suggestion": item["suggestion"]
                })
            else:
                logger.warning("Skipping malformed suggestion entry in analysis_report.json")

    if not suggestions:
        logger.error("No valid readability suggestions found in analysis_report.json. Aborting.")
        sys.exit(1)

    try:
        revised_text = apply_readability_patches(scraped_text, suggestions, api_key)
    except Exception as e:
        logger.error(f"Unexpected error during patching: {e}")
        # If something truly unexpected happens, fall back to original scraped text
        revised_text = scraped_text

    output_path = os.path.join(os.getcwd(), "revised_document.txt")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(revised_text)
        print(f"Patching complete. See '{output_path}'.")
    except Exception as e:
        logger.error(f"Failed to write revised_document.txt: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

