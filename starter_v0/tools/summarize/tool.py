"""summarize — extract key bullet points from a block of text.

This tool runs locally (no external API) and uses simple extractive
summarization: splits text into sentences, scores each by keyword density
and position, then returns the top-N sentences as bullet points.
"""

from __future__ import annotations

import re
from typing import Any


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences using regex for common delimiters."""
    sentences = re.split(r'(?<=[.!?。])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def _score_sentence(sentence: str, position: int, total: int) -> float:
    """Score a sentence based on length, position, and keyword indicators."""
    score = 0.0

    # Prefer earlier sentences (intro/topic sentences)
    if position < total * 0.3:
        score += 2.0
    elif position < total * 0.6:
        score += 1.0

    # Prefer medium-length sentences (not too short, not too long)
    word_count = len(sentence.split())
    if 10 <= word_count <= 30:
        score += 1.5
    elif word_count > 5:
        score += 0.5

    # Boost sentences with indicator words
    indicators = [
        'however', 'important', 'key', 'significant', 'conclude',
        'result', 'finding', 'major', 'critical', 'essential',
        'tuy nhiên', 'quan trọng', 'chính', 'kết luận', 'chủ yếu',
        'đáng chú ý', 'nổi bật', 'cần', 'phải',
    ]
    lower = sentence.lower()
    for word in indicators:
        if word in lower:
            score += 0.5

    return score


def summarize_text(
    text: str,
    max_points: int = 5,
    language: str = "vi",
) -> dict[str, Any]:
    """Summarize a block of text into bullet points.

    Args:
        text: The text to summarize.
        max_points: Maximum number of bullet points to return.
        language: Output language hint (vi or en). Currently affects
                  only the metadata; sentences are extracted as-is.

    Returns:
        Dict with summary_points, original_length, summary_length, language, error.
    """
    if not text or not text.strip():
        return {
            "summary_points": [],
            "original_length": 0,
            "summary_length": 0,
            "language": language,
            "error": "empty_text",
            "message": "No text provided to summarize.",
        }

    sentences = _split_sentences(text)

    if not sentences:
        return {
            "summary_points": [text.strip()[:200]],
            "original_length": len(text),
            "summary_length": min(len(text), 200),
            "language": language,
            "error": None,
        }

    # Score and rank sentences
    scored = []
    for i, sent in enumerate(sentences):
        score = _score_sentence(sent, i, len(sentences))
        scored.append((score, i, sent))

    # Sort by score descending, take top N
    scored.sort(key=lambda x: (-x[0], x[1]))
    top = scored[:max_points]

    # Re-order by original position for coherence
    top.sort(key=lambda x: x[1])
    summary_points = [item[2] for item in top]

    summary_text = " ".join(summary_points)
    return {
        "summary_points": summary_points,
        "original_length": len(text),
        "summary_length": len(summary_text),
        "language": language,
        "error": None,
    }
