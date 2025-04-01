import json
import logging
import re
from typing import List

from openai import OpenAI

from reprise.settings import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)


class OpenAIError(Exception):
    """Exception raised for OpenAI API related errors."""

    pass


def get_client():
    """Get or create the OpenAI client."""
    if not OPENAI_API_KEY:
        logger.warning("OpenAI API key not set")
        raise ValueError("OpenAI API key is required but not provided")
    return OpenAI(api_key=OPENAI_API_KEY)


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
        # Unless there are special characters, use word boundaries to not match substrings
        if not re.search(r"[^\w\s]", word):
            pattern = r"\b" + re.escape(word) + r"\b"
            for match in re.finditer(pattern, text):
                start, end = match.span()
                indices.append([start, end - 1])
        else:
            pattern = re.escape(word)
            for match in re.finditer(pattern, text):
                start, end = match.span()
                indices.append([start, end - 1])

    # Sort by start index
    indices.sort(key=lambda x: x[0])

    if not indices:
        logger.warning(f"No matches found for words: {words_to_mask}")

    return indices


def generate_cloze_deletions(content: str, n_max: int = 1) -> List[List[List[int]]]:
    """
    Use OpenAI model to generate multiple cloze deletion sets.
    Returns a list of cloze deletion sets, each containing a list of [start, end]
    position pairs that define what should be masked.

    Args:
        content: The text content to generate cloze deletions for
        n_max: The maximum number of different cloze deletion sets to generate (default: 3)

    Returns:
        List of lists of [start, end] positions, where each inner list represents a cloze deletion set

    Raises:
        ValueError: If the OpenAI API key is not set
        Exception: For any OpenAI API errors or response parsing errors
    """
    try:
        client = get_client()
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a helpful assistant that creates cloze deletions for learning purposes.
                    Given a text, create an appropriate number of different cloze deletion sets (up to {n_max} sets) 
                    where each set masks different important words or phrases that are important to learn. For example,
                    think of this as making flashcards for the text. Make as many as appropriate to learn the important
                    information, but do not exceed {n_max} sets.
                    
                    Return your response as a JSON object with a 'cloze_deletion_sets' key containing an array of arrays.
                    Each inner array contains strings representing the words or phrases to mask for that cloze deletion set.

                    For example, for the text "George Washington was the first president":
                    {{
                      "cloze_deletion_sets": [
                        ["George Washington"],
                        ["first"],
                        ["president"]
                      ]
                    }}
                    Note how the cloze deletions here represent important qualifiers on relevant information as well, i.e.
                    we did not choose "first president" but instead chose "first" and "president" separately.
                    
                    Be precise with your words to ensure they can be found exactly in the text.
                    """,
                },
                {
                    "role": "user",
                    "content": f"Create appropriate cloze deletion sets (maximum {n_max}) for: '{content}'",
                },
            ],
            temperature=0.7,
            max_tokens=250,
            response_format={"type": "json_object"},
        )

        result = response.choices[0].message.content
        mask_data = json.loads(result)
        cloze_deletion_sets = mask_data["cloze_deletion_sets"]

    except Exception as e:
        logger.error(f"Error calling OpenAI: {e}")
        raise OpenAIError(f"Failed to generate cloze deletions: {str(e)}") from e

    # Find indices for each set of words to mask
    all_mask_tuples = []
    for words_set in cloze_deletion_sets:
        mask_tuples = find_word_indices(content, words_set)
        if mask_tuples:
            all_mask_tuples.append(mask_tuples)

    if len(cloze_deletion_sets) != len(all_mask_tuples):
        raise OpenAIError("Invalid cloze deletion generation")

    return all_mask_tuples
