import os
import logging
import json
from .prompts import STYLE_GUIDELINES_PROMPT
from utils.gemini import generate_with_fallback

logger = logging.getLogger(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def extract_text_from_response(response):
    if hasattr(response, "text"):
        return response.text.strip()
    elif hasattr(response, "parts"):
        return "".join(part.text for part in response.parts if hasattr(part, "text")).strip()
    return str(response).strip()

def parse_llm_output(llm_text_output):
    try:
        if llm_text_output.startswith("```json"):
            llm_text_output = llm_text_output[7:]
        if llm_text_output.endswith("```"):
            llm_text_output = llm_text_output[:-3]
        llm_data = json.loads(llm_text_output)
        assessment = llm_data.get("assessment", "LLM output missing 'assessment' key.")
        suggestions = llm_data.get("suggestions", ["LLM output missing 'suggestions' key."])
        if not isinstance(suggestions, list):
            suggestions = [str(suggestions)]
        return assessment, suggestions
    except json.JSONDecodeError as e:
        logger.error(f"STYLE_ANALYZER: Failed to parse JSON: {e} | Raw output: {llm_text_output}")
        parts = llm_text_output.split("Specific changes suggested:", 1)
        assessment = parts[0].strip()
        suggestions = [s.strip() for s in parts[1].splitlines() if s.strip()] if len(parts) > 1 else ["Could not parse specific changes."]
        return assessment, suggestions
    except Exception as e:
        logger.error(f"STYLE_ANALYZER: Unexpected error while parsing output: {e}")
        return f"Error during LLM parsing: {e}", [f"Raw output: {llm_text_output}"]

def analyze_style(document_text: str) -> dict:
    result = {
        "assessment": "Could not be determined.",
        "suggestions": []
    }

    if not document_text or document_text.isspace():
        result["assessment"] = "Document text is empty or contains only whitespace."
        return result

    prompt = STYLE_GUIDELINES_PROMPT.format(document_text=document_text)
    if len(prompt) > 750000:
        logger.warning(f"STYLE_ANALYZER: Large prompt ({len(prompt)} chars).")

    try:
        response = generate_with_fallback(prompt, GEMINI_API_KEY)
        if not response:
            raise ValueError("LLM generation failed or returned None")

        if hasattr(response, "parts") and response.parts:
            llm_output = extract_text_from_response(response)
            assessment, suggestions = parse_llm_output(llm_output)
            result["assessment"] = assessment
            result["suggestions"] = suggestions
        else:
            msg = "LLM response was empty or blocked."
            if getattr(response, "prompt_feedback", None) and response.prompt_feedback.block_reason:
                block = response.prompt_feedback.block_reason
                msg = f"LLM response blocked: {block.name} ({getattr(response.prompt_feedback, 'block_reason_message', '')})"
            result["assessment"] = msg
            result["suggestions"] = [msg]
    except Exception as e:
        logger.error(f"STYLE_ANALYZER: Top-level failure: {e}", exc_info=True)
        result["assessment"] = f"LLM assessment failed: {e}"
        result["suggestions"] = [f"LLM assessment failed: {e}"]

    return result
