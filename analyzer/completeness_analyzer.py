import os
import logging
from .prompts import COMPLETENESS_PROMPT
import json
from utils.gemini import generate_with_fallback

logger = logging.getLogger(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def analyze_completeness(document_text: str) -> dict:
    analysis_result = { "assessment": "Could not be determined.", "suggestions": [] }
    if not document_text or document_text.isspace():
        analysis_result["assessment"] = "Document text is empty or contains only whitespace."
        return analysis_result

    llm_failure_message = "LLM content generation failed. This could be due to an invalid/missing API key, network issues, all model attempts (including fallback) failing, or the models being unavailable."
    prompt = COMPLETENESS_PROMPT.format(document_text=document_text)
    if len(prompt) > 750000:
        logger.warning(f"COMPLETENESS_ANALYZER: Prompt string length is very large ({len(prompt)} chars). This might impact performance or cost.")

    response = generate_with_fallback(prompt, GEMINI_API_KEY)

    if response:
        try:
            if response.parts:
                llm_text_output = response.text.strip()
                try:
                    if llm_text_output.startswith("```json"): llm_text_output = llm_text_output[7:]
                    if llm_text_output.endswith("```"): llm_text_output = llm_text_output[:-3]
                    llm_data = json.loads(llm_text_output)
                    analysis_result["assessment"] = llm_data.get("assessment", "LLM output missing 'assessment' key.")
                    analysis_result["suggestions"] = llm_data.get("suggestions", ["LLM output missing 'suggestions' key."])
                    if not isinstance(analysis_result["suggestions"], list):
                        analysis_result["suggestions"] = [str(analysis_result["suggestions"])]
                except json.JSONDecodeError as je:
                    logger.error(f"COMPLETENESS_ANALYZER: Failed to parse LLM response as JSON: {je}\nRaw output: {llm_text_output}")
                    analysis_result["assessment"] = "LLM response was not valid JSON. Using raw output."
                    parts = llm_text_output.split("Suggestions:", 1)
                    analysis_result["assessment"] = parts[0].strip()
                    analysis_result["suggestions"] = [s.strip() for s in parts[1].strip().splitlines() if s.strip()] if len(parts) > 1 else ["Could not parse suggestions."]
                except Exception as e:
                    logger.error(f"COMPLETENESS_ANALYZER: Error processing LLM JSON output: {e}")
                    analysis_result["assessment"] = f"Error processing LLM JSON: {e}"
                    analysis_result["suggestions"] = [f"Raw output: {llm_text_output}"]
            else:
                safety_feedback_message = "LLM response was empty or potentially blocked by safety filters."
                if response.prompt_feedback and response.prompt_feedback.block_reason:
                    safety_feedback_message = f"LLM response blocked due to: {response.prompt_feedback.block_reason.name} ({response.prompt_feedback.block_reason_message or ''})"
                logger.warning(f"COMPLETENESS_ANALYZER: {safety_feedback_message}")
                analysis_result["assessment"] = safety_feedback_message
                analysis_result["suggestions"] = [safety_feedback_message]
        except Exception as e:
            logger.error(f"COMPLETENESS_ANALYZER: Error processing LLM response object: {e}", exc_info=True)
            analysis_result["assessment"] = f"LLM assessment failed during response processing: {e}"
            analysis_result["suggestions"] = [f"LLM assessment failed: {e}"]
    else:
        logger.warning(f"COMPLETENESS_ANALYZER: {llm_failure_message}")
        analysis_result["assessment"] = llm_failure_message
        if not analysis_result["suggestions"]: analysis_result["suggestions"].append(llm_failure_message)
    return analysis_result

