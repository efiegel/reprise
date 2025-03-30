import json
import logging
from typing import List

from openai import OpenAI

from reprise.config import OPENAI_API_KEY, OPENAI_MODEL

# Configure logging
logger = logging.getLogger(__name__)

# Only initialize the client if an API key is available
# This prevents errors during testing
client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)


def generate_cloze_deletion(content: str) -> List[List[int]]:
    """
    Use OpenAI model to generate mask tuples for a cloze deletion.
    Returns a list of [start, end] position pairs that define what should be masked.

    Args:
        content: The text content to generate a cloze deletion for

    Returns:
        List of [start, end] positions representing where to mask
    """
    if not OPENAI_API_KEY or not client:
        logger.warning("OpenAI API key not set, using default cloze deletion")
        return [[0, 1]]  # Default fallback if no API key

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful assistant that creates cloze deletions for learning purposes.
                    A cloze deletion is a learning exercise where certain parts of a text are masked out.
                    Given a text, identify 1-3 important words or phrases to mask out.
                    
                    Return your response as a JSON object with a 'mask_tuples' key containing an array of [start, end] position pairs.
                    Each pair identifies a span of text to mask, where 'start' is the starting character index (0-based) 
                    and 'end' is the ending character index (0-based, inclusive).
                    
                    For example, if the input is 'The sky is blue' and you want to mask 'blue', return:
                    { "mask_tuples": [[11, 14]] }
                    
                    If you want to mask multiple parts, include multiple pairs like:
                    { "mask_tuples": [[0, 3], [11, 14]] }
                    """,
                },
                {"role": "user", "content": f"Create a cloze deletion for: {content}"},
            ],
            temperature=0.7,
            max_tokens=150,
            response_format={"type": "json_object"},
        )

        # Extract the response and parse as JSON
        result = response.choices[0].message.content
        try:
            # Parse the JSON response
            mask_tuples_data = json.loads(result)
            mask_tuples = mask_tuples_data.get("mask_tuples", [[0, 1]])

            # Validate the mask_tuples
            if not isinstance(mask_tuples, list) or not all(
                isinstance(t, list)
                and len(t) == 2
                and all(isinstance(i, int) for i in t)
                for t in mask_tuples
            ):
                logger.warning(f"Invalid mask_tuples format from OpenAI: {mask_tuples}")
                return [[0, 1]]

            # Validate that the indices are within the content length
            content_length = len(content)
            valid_tuples = []
            for start, end in mask_tuples:
                if 0 <= start < content_length and start <= end < content_length:
                    valid_tuples.append([start, end])
                else:
                    logger.warning(
                        f"Invalid mask tuple range: [{start}, {end}] for content length {content_length}"
                    )

            # If no valid tuples, return default
            if not valid_tuples:
                logger.warning("No valid mask tuples found, using default")
                return [[0, 1]]

            return valid_tuples

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Error parsing OpenAI response: {e}. Response: {result}")
            return [[0, 1]]

    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return [[0, 1]]  # Default fallback on error
