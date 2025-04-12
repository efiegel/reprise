import logging
import re
from typing import List

from pydantic import BaseModel, Field
from pydantic_ai import Agent

logger = logging.getLogger(__name__)


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


class ClozeDeletionResult(BaseModel):
    cloze_deletion_sets: List[List[str]] = Field(
        description="List of cloze deletion sets, each containing a list of words or phrases to mask"
    )


def generate_cloze_deletions(content: str, n_max: int = 1) -> List[List[List[int]]]:
    """
    Use AI to generate multiple cloze deletion sets.
    Returns a list of cloze deletion sets, each containing a list of [start, end]
    position pairs that define what should be masked.

    Args:
        content: The text content to generate cloze deletions for
        n_max: The maximum number of different cloze deletion sets to generate (default: 3)

    Returns:
        List of lists of [start, end] positions, where each inner list represents a cloze deletion set
    """

    system_prompt = f"""
    You are a helpful assistant that creates cloze deletions for learning purposes.
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
    """

    agent = Agent(
        model="gpt-4o-mini",
        system_prompt=system_prompt,
        result_type=ClozeDeletionResult,
    )

    response = agent.run_sync(
        f"Create appropriate cloze deletion sets (maximum {n_max}) for: '{content}'"
    )
    cloze_deletion_sets = response.cloze_deletion_sets

    # Find indices for each set of words to mask
    all_mask_tuples = []
    for words_set in cloze_deletion_sets:
        mask_tuples = find_word_indices(content, words_set)
        if mask_tuples:
            all_mask_tuples.append(mask_tuples)

    if len(cloze_deletion_sets) != len(all_mask_tuples):
        raise ValueError("Invalid cloze deletion generation")

    return all_mask_tuples
