"""Core recommendation engine for CourseMap."""

from __future__ import annotations

import csv
import io
import json
import uuid
from typing import Literal

from pydantic import BaseModel, Field

from coursemap.config import CourseMapConfig, config as default_config
from coursemap.utils import (
    compute_relevance_score,
    filter_courses_by_level,
    filter_courses_by_topic,
    sort_courses_by_level,
)


class Course(BaseModel):
    """A course in the catalog."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str
    topics: list[str]
    level: str = "beginner"
    duration: int = Field(default=0, description="Duration in minutes")
    ratings: list[float] = Field(default_factory=list)
    score: float = Field(default=0.0, description="Computed relevance score")

    @property
    def average_rating(self) -> float:
        """Return the average rating, or 0.0 if unrated."""
        if not self.ratings:
            return 0.0
        return sum(self.ratings) / len(self.ratings)

    @property
    def rating_count(self) -> int:
        """Return the number of ratings."""
        return len(self.ratings)


class UserProfile(BaseModel):
    """A learner profile used for generating recommendations."""

    skills: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    level: str = "beginner"


class ScoredCourse(Course):
    """A course with an attached relevance score for recommendation output."""

    score: float = 0.0


class CourseMap:
    """Course recommendation engine using content-based filtering.

    Manages a catalog of courses, user profiles, and provides recommendations
    based on topic overlap scoring between course content and user interests.
    """

    def __init__(self, config: CourseMapConfig | None = None) -> None:
        self.config = config or default_config
        self._courses: dict[str, Course] = {}
        self._profiles: dict[str, UserProfile] = {}

    @property
    def catalog_size(self) -> int:
        """Return the number of courses in the catalog."""
        return len(self._courses)

    def add_course(
        self,
        title: str,
        topics: list[str],
        level: str = "beginner",
        duration: int = 0,
    ) -> Course:
        """Add a course to the catalog and return it.

        Args:
            title: The course title.
            topics: List of topic tags for the course.
            level: Difficulty level (beginner, intermediate, advanced).
            duration: Duration in minutes.

        Returns:
            The newly created Course object.
        """
        course = Course(title=title, topics=topics, level=level, duration=duration)
        self._courses[course.id] = course
        return course

    def get_course(self, course_id: str) -> Course | None:
        """Retrieve a course by its ID."""
        return self._courses.get(course_id)

    def set_profile(
        self,
        skills: list[str] | None = None,
        goals: list[str] | None = None,
        level: str = "beginner",
        profile_id: str | None = None,
    ) -> UserProfile:
        """Create or update a user profile.

        Args:
            skills: List of existing skills the user has.
            goals: List of learning goals the user wants to achieve.
            level: Current skill level.
            profile_id: Optional ID for the profile (auto-generated if omitted).

        Returns:
            The created or updated UserProfile.
        """
        profile = UserProfile(
            skills=skills or [],
            goals=goals or [],
            level=level,
        )
        pid = profile_id or uuid.uuid4().hex[:12]
        self._profiles[pid] = profile
        return profile

    def recommend(self, profile: UserProfile, n: int | None = None) -> list[Course]:
        """Generate course recommendations for a user profile.

        Uses content-based filtering: computes relevance scores based on
        topic overlap between the course and the user's skills and goals,
        combined with level matching and course ratings.

        Args:
            profile: The user profile to generate recommendations for.
            n: Maximum number of recommendations (defaults to config).

        Returns:
            A list of Course objects sorted by descending relevance score.
        """
        max_n = n or self.config.max_recommendations
        scored: list[Course] = []

        for course in self._courses.values():
            score = compute_relevance_score(course, profile)
            if score >= self.config.min_score:
                course_copy = course.model_copy(update={"score": score})
                scored.append(course_copy)

        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[:max_n]

    def filter_by_topic(self, topic: str) -> list[Course]:
        """Return all courses matching a given topic.

        Args:
            topic: The topic string to filter by.

        Returns:
            List of courses containing the topic.
        """
        return filter_courses_by_topic(list(self._courses.values()), topic)

    def filter_by_level(self, level: str) -> list[Course]:
        """Return all courses matching a given difficulty level.

        Args:
            level: The difficulty level to filter by.

        Returns:
            List of courses at the specified level.
        """
        return filter_courses_by_level(list(self._courses.values()), level)

    def rate_course(self, course_id: str, rating: float) -> Course:
        """Add a rating to a course.

        Args:
            course_id: The ID of the course to rate.
            rating: A rating value between 1.0 and 5.0.

        Returns:
            The updated Course object.

        Raises:
            ValueError: If the course is not found or rating is out of range.
        """
        if rating < 1.0 or rating > 5.0:
            raise ValueError(f"Rating must be between 1.0 and 5.0, got {rating}")

        course = self._courses.get(course_id)
        if course is None:
            raise ValueError(f"Course not found: {course_id}")

        course.ratings.append(rating)
        return course

    def get_popular(self, n: int = 10) -> list[Course]:
        """Get the most popular courses by average rating.

        Courses must have at least one rating to be included.

        Args:
            n: Maximum number of courses to return.

        Returns:
            List of courses sorted by average rating (descending).
        """
        rated = [c for c in self._courses.values() if c.ratings]
        rated.sort(key=lambda c: c.average_rating, reverse=True)
        return rated[:n]

    def get_learning_path(self, goal: str) -> list[Course]:
        """Generate a learning path for a specific goal.

        Finds courses related to the goal topic and orders them by
        difficulty level (beginner -> intermediate -> advanced).

        Args:
            goal: The learning goal / topic to build a path for.

        Returns:
            An ordered list of courses forming a learning path.
        """
        related = filter_courses_by_topic(list(self._courses.values()), goal)
        return sort_courses_by_level(related)

    def export(
        self,
        recommendations: list[Course],
        format: Literal["json", "csv", "markdown"] = "json",
    ) -> str:
        """Export recommendations in the specified format.

        Args:
            recommendations: List of courses to export.
            format: Output format -- 'json', 'csv', or 'markdown'.

        Returns:
            A string containing the exported data.

        Raises:
            ValueError: If an unsupported format is specified.
        """
        if format == "json":
            return self._export_json(recommendations)
        elif format == "csv":
            return self._export_csv(recommendations)
        elif format == "markdown":
            return self._export_markdown(recommendations)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_json(self, courses: list[Course]) -> str:
        """Export courses as a JSON string."""
        data = [
            {
                "id": c.id,
                "title": c.title,
                "topics": c.topics,
                "level": c.level,
                "duration": c.duration,
                "score": round(c.score, 4),
                "average_rating": round(c.average_rating, 2),
            }
            for c in courses
        ]
        return json.dumps(data, indent=2)

    def _export_csv(self, courses: list[Course]) -> str:
        """Export courses as a CSV string."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "title", "topics", "level", "duration", "score", "avg_rating"])
        for c in courses:
            writer.writerow([
                c.id,
                c.title,
                "|".join(c.topics),
                c.level,
                c.duration,
                round(c.score, 4),
                round(c.average_rating, 2),
            ])
        return output.getvalue()

    def _export_markdown(self, courses: list[Course]) -> str:
        """Export courses as a Markdown table."""
        lines = [
            "| # | Title | Topics | Level | Duration | Score |",
            "|---|-------|--------|-------|----------|-------|",
        ]
        for i, c in enumerate(courses, 1):
            topics_str = ", ".join(c.topics)
            lines.append(
                f"| {i} | {c.title} | {topics_str} | {c.level} | {c.duration}m | {c.score:.2f} |"
            )
        return "\n".join(lines)
