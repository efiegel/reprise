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

    Raises:
        ValueError: If the OpenAI API key is not set
        ValueError: If the response format is invalid
        Exception: For any OpenAI API errors
    """
    if not OPENAI_API_KEY or not client:
        logger.warning("OpenAI API key not set")
        raise ValueError("OpenAI API key is required but not provided")

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": """You are a helpful assistant that creates cloze deletions for learning purposes.
                Given a text, identify the most important word(s) to mask out, as if you were trying learn the text with flashcards.
                
                Return your response as a JSON object with a 'mask_tuples' key containing an array of [start, end] position pairs.
                Each pair identifies a span of text to mask, where 'start' is the starting character index (0-based) 
                and 'end' is the ending character index (0-based, inclusive).
                
                For example, if the input is 'The sky is blue' and you want to mask 'blue', return:
                { "mask_tuples": [[11, 14]] }
                
                If you want to mask multiple parts, include multiple pairs like:
                { "mask_tuples": [[4, 6], [11, 14]] }

                Note that spaces are also characters, so don't omit them when determining character indices.
                """,
            },
            {"role": "user", "content": f"Create a cloze deletion for: '{content}'"},
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
        if "mask_tuples" not in mask_tuples_data:
            logger.error(f"Missing mask_tuples in response: {result}")
            raise ValueError("OpenAI response missing required 'mask_tuples' field")

        mask_tuples = mask_tuples_data["mask_tuples"]

        # Validate the mask_tuples
        if not isinstance(mask_tuples, list) or not all(
            isinstance(t, list) and len(t) == 2 and all(isinstance(i, int) for i in t)
            for t in mask_tuples
        ):
            logger.error(f"Invalid mask_tuples format from OpenAI: {mask_tuples}")
            raise ValueError(f"Invalid mask_tuples format: {mask_tuples}")

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

        # If no valid tuples, raise an exception
        if not valid_tuples:
            logger.error("No valid mask tuples found")
            raise ValueError("No valid mask tuples found in the content range")

        return valid_tuples

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing OpenAI response: {e}. Response: {result}")
        raise ValueError(f"Invalid JSON in OpenAI response: {e}") from e
    except (KeyError, TypeError) as e:
        logger.error(
            f"Error extracting data from OpenAI response: {e}. Response: {result}"
        )
        raise ValueError(f"Error extracting data from OpenAI response: {e}") from e
