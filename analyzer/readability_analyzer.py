import os
import logging
import textstat
from .prompts import READABILITY_PROMPT
import json
from utils.gemini import generate_with_fallback

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def analyze_readability(document_text: str) -> dict:
    analysis_result = {
        "score": None,  
        "assessment": "Could not be determined.",
        "suggestions": []
    }

    if not document_text or document_text.isspace():
        analysis_result["assessment"] = "Document text is empty or contains only whitespace."
        return analysis_result

    try:
        analysis_result["score"] = textstat.flesch_reading_ease(document_text)
    except Exception as e:
        logger.error(f"Error calculating Flesch-Kincaid score: {e}")
        analysis_result["assessment"] = (
            f"Flesch-Kincaid score calculation failed: {e}. "
            "LLM assessment will proceed if possible."
        )

    # LLM analysis part
    llm_failure_message = (
        "LLM content generation failed. This could be due to an invalid/missing API key, "
        "network issues, all model attempts (including fallback) failing, or the models being unavailable."
    )


    prompt = READABILITY_PROMPT.format(document_text=document_text)

    if len(prompt) > 750000: 
        logger.warning(
            f"READABILITY_ANALYZER: Prompt string length is very large ({len(prompt)} chars). "
            "This might impact performance or cost."
        )

    response = None
    try:
        response = generate_with_fallback(prompt, GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"READABILITY_ANALYZER: generate_with_fallback call failed: {e}")
        response = None

    if response: 
        try:
            if response.parts:  
                llm_text_output = response.text.strip()

                # Strip ```json fences if present
                if llm_text_output.startswith("```json"):
                    llm_text_output = llm_text_output[7:]
                if llm_text_output.endswith("```"):
                    llm_text_output = llm_text_output[:-3]

                try:
                    llm_data = json.loads(llm_text_output)

                    # NEW: If the LLM returned a list instead of a dict, handle accordingly
                    if isinstance(llm_data, list):
                        analysis_result["assessment"] = llm_data.get(
                            "assessment", "LLM returned suggestions without a top-level object."
                        )
                        analysis_result["suggestions"] = llm_data
                    elif isinstance(llm_data, dict):
                        # Normal path: extract "assessment" and "suggestions" keys
                        analysis_result["assessment"] = llm_data.get(
                            "assessment", "LLM output missing 'assessment' key."
                        )
                        suggestions = llm_data.get("suggestions", [])
                        if isinstance(suggestions, list):
                            analysis_result["suggestions"] = suggestions
                        else:
                            analysis_result["suggestions"] = [str(suggestions)]
                    else:
                        analysis_result["assessment"] = (
                            "LLM returned unexpected JSON type. Using raw output."
                        )
                        analysis_result["suggestions"] = [llm_text_output]

                except json.JSONDecodeError as je:
                    logger.error(f"READABILITY_ANALYZER: Failed to parse LLM response as JSON: {je}")
                    logger.error(f"READABILITY_ANALYZER: Raw LLM output was: {llm_text_output}")
                    analysis_result["assessment"] = "LLM response was not valid JSON. Using raw output."
                    parts = llm_text_output.split("Suggestions:", 1) 
                    analysis_result["assessment"] = parts[0].strip()
                    if len(parts) > 1:
                        analysis_result["suggestions"] = [
                            s.strip() for s in parts[1].strip().splitlines() if s.strip()
                        ]
                    else:
                        analysis_result["suggestions"] = [
                            "Could not parse suggestions from non-JSON LLM output."
                        ]

                except Exception as e: 
                    logger.error(f"READABILITY_ANALYZER: Error processing LLM JSON output: {e}")
                    analysis_result["assessment"] = f"Error processing LLM JSON: {e}"
                    analysis_result["suggestions"] = [f"Raw output: {llm_text_output}"]

            else:
                safety_feedback_message = (
                    "LLM response was empty or potentially blocked by safety filters."
                )
                if hasattr(response, "prompt_feedback") and response.prompt_feedback:
                    if response.prompt_feedback.block_reason:
                        safety_feedback_message = (
                            f"LLM response blocked due to: "
                            f"{response.prompt_feedback.block_reason.name} "
                            f"({response.prompt_feedback.block_reason_message or ''})"
                        )
                logger.warning(f"READABILITY_ANALYZER: {safety_feedback_message}")
                analysis_result["assessment"] = safety_feedback_message
                analysis_result["suggestions"] = [safety_feedback_message]

        except Exception as e:  
            logger.error(f"READABILITY_ANALYZER: Error processing LLM response object: {e}", exc_info=True)
            analysis_result["assessment"] = f"LLM assessment failed during response processing: {e}"
            analysis_result["suggestions"] = [f"LLM assessment failed: {e}"]

    else:
        # generate_with_fallback returned None (e.g., API key issue or all model attempts failed)
        logger.warning(f"READABILITY_ANALYZER: {llm_failure_message}")
        current_assessment_is_score_error = (
            "Flesch-Kincaid score calculation failed" in analysis_result.get("assessment", "")
        )
        if analysis_result.get("score") is not None and not current_assessment_is_score_error:
            analysis_result["assessment"] = (
                f"Readability score: {analysis_result['score']}. {llm_failure_message}"
            )
        else:
            analysis_result["assessment"] = llm_failure_message

        if not analysis_result["suggestions"]:  # Lets try to add a failure message if suggestions are empty
            analysis_result["suggestions"].append(llm_failure_message)

    return analysis_result
