"""Utility functions for topic matching, scoring, and filtering."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from coursemap.core import Course, UserProfile


def normalize_topic(topic: str) -> str:
    """Normalize a topic string for consistent matching.

    Lowercases, strips whitespace, and replaces spaces with hyphens.
    """
    return topic.strip().lower().replace(" ", "-").replace("_", "-")


def normalize_topics(topics: list[str]) -> list[str]:
    """Normalize a list of topic strings."""
    return [normalize_topic(t) for t in topics]


def compute_topic_overlap(topics_a: list[str], topics_b: list[str]) -> float:
    """Compute Jaccard-style overlap between two topic lists.

    Returns a score between 0.0 and 1.0 representing the ratio of
    shared topics to the total unique topics across both lists.
    """
    set_a = set(normalize_topics(topics_a))
    set_b = set(normalize_topics(topics_b))

    if not set_a and not set_b:
        return 0.0

    intersection = set_a & set_b
    union = set_a | set_b

    return len(intersection) / len(union)


def compute_relevance_score(course: "Course", profile: "UserProfile") -> float:
    """Compute a relevance score for a course given a user profile.

    The score combines:
    - Topic overlap between course topics and user skills (weight: 0.4)
    - Topic overlap between course topics and user goals (weight: 0.4)
    - Level match bonus (weight: 0.2)
    - Average rating bonus (up to 0.1)

    Returns a float between 0.0 and 1.0.
    """
    skill_overlap = compute_topic_overlap(course.topics, profile.skills)
    goal_overlap = compute_topic_overlap(course.topics, profile.goals)

    level_bonus = 0.0
    if normalize_topic(course.level) == normalize_topic(profile.level):
        level_bonus = 1.0

    rating_bonus = 0.0
    if course.ratings:
        avg_rating = sum(course.ratings) / len(course.ratings)
        rating_bonus = avg_rating / 5.0  # Normalize to 0-1 range

    score = (
        0.4 * skill_overlap
        + 0.4 * goal_overlap
        + 0.15 * level_bonus
        + 0.05 * rating_bonus
    )

    return min(score, 1.0)


def filter_courses_by_topic(courses: list["Course"], topic: str) -> list["Course"]:
    """Filter courses that contain the given topic."""
    normalized = normalize_topic(topic)
    return [c for c in courses if normalized in normalize_topics(c.topics)]


def filter_courses_by_level(courses: list["Course"], level: str) -> list["Course"]:
    """Filter courses matching the given difficulty level."""
    normalized = normalize_topic(level)
    return [c for c in courses if normalize_topic(c.level) == normalized]


def sort_courses_by_level(courses: list["Course"]) -> list["Course"]:
    """Sort courses by difficulty level: beginner -> intermediate -> advanced."""
    level_order = {"beginner": 0, "intermediate": 1, "advanced": 2}

    def sort_key(course: "Course") -> int:
        return level_order.get(normalize_topic(course.level), 99)

    return sorted(courses, key=sort_key)


def format_duration(minutes: int) -> str:
    """Format a duration in minutes to a human-readable string."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    remaining = minutes % 60
    if remaining == 0:
        return f"{hours}h"
    return f"{hours}h {remaining}m"
