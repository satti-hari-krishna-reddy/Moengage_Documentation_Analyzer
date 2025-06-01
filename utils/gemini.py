import os
import logging
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError

logger = logging.getLogger(__name__)

PRIMARY_MODEL_NAME = "gemini-2.5-flash-preview-05-20"
FALLBACK_MODEL_NAME = "gemini-2.0-flash" # Fallback for rate limits

# To ensure genai.configure is called only once with a valid key
gemini_configured = False
gemini_config_success = False

def _configure_gemini_if_needed(api_key_to_use: str) -> bool:
    """Configures the Gemini API if not already done. Returns True if successful."""
    global gemini_configured, gemini_config_success
    if not gemini_configured:
        gemini_configured = True # Attempt configuration only once
        if not api_key_to_use or api_key_to_use == "YOUR_API_KEY_PLACEHOLDER":
            logger.warning("GEMINI_UTILS: API key is missing or a placeholder. Gemini calls will be skipped.")
            gemini_config_success = False
            return False
        try:
            genai.configure(api_key=api_key_to_use)
            logger.info(f"GEMINI_UTILS: Gemini API configured successfully with key ending: ...{api_key_to_use[-4:]}")
            gemini_config_success = True
            return True
        except Exception as e:
            logger.error(f"GEMINI_UTILS: Error configuring Gemini API: {e}", exc_info=True)
            gemini_config_success = False
            return False
    return gemini_config_success


def generate_with_fallback(prompt_text: str, api_key: str) -> genai.types.GenerateContentResponse | None:
    """
    Generates content using the primary Gemini model, with a fallback to a secondary
    model in case of specific rate limit errors (ResourceExhausted).
    Returns the response object or None if all attempts fail or API is not configured.
    """
    if not _configure_gemini_if_needed(api_key):
        logger.warning("GEMINI_UTILS: API not configured. Skipping content generation.")
        return None

    models_to_try = [PRIMARY_MODEL_NAME, FALLBACK_MODEL_NAME]
    last_exception = None

    for i, model_name in enumerate(models_to_try):
        try:
            logger.info(f"GEMINI_UTILS: Attempting content generation with model: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt_text)
            logger.info(f"GEMINI_UTILS: Successfully generated content with {model_name}.")
            return response

        except ResourceExhausted as re:
            logger.warning(f"GEMINI_UTILS: ResourceExhausted (rate limit) error with model {model_name}: {re}")
            last_exception = re
            if i < len(models_to_try) - 1: # If there's a fallback model left
                logger.info(f"GEMINI_UTILS: Attempting fallback to model {models_to_try[i+1]}.")
                continue # Try next model
            else: 
                logger.error(f"GEMINI_UTILS: All model attempts failed due to ResourceExhausted.")
                break 

        except GoogleAPIError as api_err: 
            logger.error(f"GEMINI_UTILS: GoogleAPIError with model {model_name}: {api_err}", exc_info=True)
            last_exception = api_err
            # Do not fallback for general API errors, only for ResourceExhausted
            break

        except Exception as e:
            logger.error(f"GEMINI_UTILS: Unexpected error with model {model_name}: {e}", exc_info=True)
            last_exception = e
            break

    logger.error(f"GEMINI_UTILS: Failed to generate content after all attempts. Last error: {last_exception}")
    return None 