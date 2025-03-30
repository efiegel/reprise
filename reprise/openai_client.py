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


def generate_cloze_deletion(content: str, n: int = 1) -> List[List[List[int]]]:
    """
    Use OpenAI model to generate multiple cloze deletion sets.
    Returns a list of cloze deletion sets, each containing a list of [start, end]
    position pairs that define what should be masked.

    Args:
        content: The text content to generate cloze deletions for
        n: The number of different cloze deletion sets to generate (default: 1)

    Returns:
        List of lists of [start, end] positions, where each inner list represents a cloze deletion set

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
                "content": f"""You are a helpful assistant that creates cloze deletions for learning purposes.
                Given a text, create {n} different cloze deletion sets where each set masks different important
                words or phrases to test different aspects of the text.
                
                Return your response as a JSON object with a 'cloze_deletion_sets' key containing an array of arrays.
                Each inner array contains strings representing the words or phrases to mask for that cloze deletion set.
                
                For example, if asked to create 2 cloze deletion sets for "The sky is blue and the grass is green":
                {{
                  "cloze_deletion_sets": [
                    ["blue", "green"],  // First deletion set masks colors
                    ["sky", "grass"]    // Second deletion set masks objects
                  ]
                }}
                
                Each set should focus on masking different aspects of the content.
                Be precise with your words to ensure they can be found exactly in the text.
                Provide exactly {n} different cloze deletion sets, unless the text is too short.
                """,
            },
            {
                "role": "user",
                "content": f"Create {n} different cloze deletion sets for: '{content}'",
            },
        ],
        temperature=0.7,
        max_tokens=250,
        response_format={"type": "json_object"},
    )

    # Extract the response and parse as JSON
    result = response.choices[0].message.content
    try:
        # Parse the JSON response
        mask_data = json.loads(result)
        if "cloze_deletion_sets" not in mask_data:
            logger.error(f"Missing cloze_deletion_sets in response: {result}")
            raise ValueError(
                "OpenAI response missing required 'cloze_deletion_sets' field"
            )

        cloze_deletion_sets = mask_data["cloze_deletion_sets"]

        # Validate the cloze_deletion_sets
        if not isinstance(cloze_deletion_sets, list) or not all(
            isinstance(set_items, list) and all(isinstance(w, str) for w in set_items)
            for set_items in cloze_deletion_sets
        ):
            logger.error(
                f"Invalid cloze_deletion_sets format from OpenAI: {cloze_deletion_sets}"
            )
            raise ValueError(
                f"Invalid cloze_deletion_sets format: {cloze_deletion_sets}"
            )

        # Find indices for each set of words to mask
        all_mask_tuples = []
        for words_set in cloze_deletion_sets:
            # Find indices of words to mask for this set
            mask_tuples = find_word_indices(content, words_set)

            # If no valid tuples for this set, log a warning but continue
            if not mask_tuples:
                logger.warning(f"No valid mask tuples found for words: {words_set}")
                continue

            all_mask_tuples.append(mask_tuples)

        # If no valid tuples found in any sets, raise an exception
        if not all_mask_tuples:
            logger.error("No valid mask tuples found in any cloze deletion set")
            raise ValueError("No valid mask tuples found in the content range")

        return all_mask_tuples

    except json.JSONDecodeError as e:
        logger.error(f"Error parsing OpenAI response: {e}. Response: {result}")
        raise ValueError(f"Invalid JSON in OpenAI response: {e}") from e
    except (KeyError, TypeError) as e:
        logger.error(
            f"Error extracting data from OpenAI response: {e}. Response: {result}"
        )
        raise ValueError(f"Error extracting data from OpenAI response: {e}") from e
