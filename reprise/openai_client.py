import json
import logging
import re
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


def find_word_indices(text: str, words_to_mask: List[str]) -> List[List[int]]:
    """
    Find the start and end indices of words to mask in the given text.

    Args:
        text: The text content to search in
        words_to_mask: List of words or phrases to find and mask

    Returns:
        List of [start, end] positions representing where to mask
    """
    indices = []
    for word in words_to_mask:
        # For expressions with special characters like 'O(n log n)',
        # we can't rely on word boundaries, so we check for them separately
        if re.search(r"[^\w\s]", word):
            # For expressions with special characters, use direct pattern search
            pattern = re.escape(word)
            for match in re.finditer(pattern, text):
                start, end = match.span()
                # End index is exclusive in match.span(), but we want inclusive
                indices.append([start, end - 1])
        else:
            # For regular words, use word boundaries to ensure we match complete words
            pattern = r"\b" + re.escape(word) + r"\b"
            for match in re.finditer(pattern, text):
                start, end = match.span()
                # End index is exclusive in match.span(), but we want inclusive
                indices.append([start, end - 1])

    # Sort by start index
    indices.sort(key=lambda x: x[0])

    if not indices:
        logger.warning(f"No matches found for words: {words_to_mask}")

    return indices


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
                Given a text, identify the single most important word or phrase to mask out, as if you
                were to learn the text with flashcards and wanted to single out the important meaning.
                
                Return your response as a JSON object with a 'words_to_mask' key containing an array of strings.
                Each string is a word or short phrase that should be masked in the text.
                
                For example, if the input is 'The sky is blue' and you want to mask 'blue', return:
                { "words_to_mask": ["blue"] }
                
                You can mask multiple words or phrases, but only do so if it doesn't over-mask the text.
                For example, if the input it 'The sky is blue' you should not mask 'sky' and 'blue' because
                that would make reconstruction of the text unrealistic (all context is gone).
                
                If you want to mask multiple words, include multiple words like:
                { "words_to_mask": ["word_1", "word_2"] }

                If you mask a phrase, include the phrase as a single string:
                { "words_to_mask": ["Eiffel Tower"] }
                
                Be precise with your words to ensure they can be found exactly in the text.
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
        mask_data = json.loads(result)
        if "words_to_mask" not in mask_data:
            logger.error(f"Missing words_to_mask in response: {result}")
            raise ValueError("OpenAI response missing required 'words_to_mask' field")

        words_to_mask = mask_data["words_to_mask"]

        # Validate the words_to_mask
        if not isinstance(words_to_mask, list) or not all(
            isinstance(w, str) for w in words_to_mask
        ):
            logger.error(f"Invalid words_to_mask format from OpenAI: {words_to_mask}")
            raise ValueError(f"Invalid words_to_mask format: {words_to_mask}")

        # Find indices of words to mask
        valid_tuples = find_word_indices(content, words_to_mask)

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
