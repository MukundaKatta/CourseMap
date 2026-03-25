"""Tests for CourseMap core recommendation engine."""

import json

import pytest

from coursemap import CourseMap, UserProfile


@pytest.fixture
def engine() -> CourseMap:
    """Create a CourseMap engine pre-loaded with sample courses."""
    cm = CourseMap()
    cm.add_course("Intro to Python", topics=["python", "programming"], level="beginner", duration=10)
    cm.add_course(
        "Machine Learning Basics",
        topics=["ml", "python", "data-science"],
        level="intermediate",
        duration=20,
    )
    cm.add_course(
        "Deep Learning with PyTorch",
        topics=["deep-learning", "pytorch", "ml"],
        level="advanced",
        duration=30,
    )
    cm.add_course(
        "Data Analysis with Pandas",
        topics=["pandas", "python", "data-science"],
        level="beginner",
        duration=12,
    )
    cm.add_course(
        "Web Development with Django",
        topics=["django", "python", "web"],
        level="intermediate",
        duration=25,
    )
    return cm


class TestAddCourse:
    def test_add_course_creates_course(self, engine: CourseMap) -> None:
        initial_size = engine.catalog_size
        course = engine.add_course("New Course", topics=["testing"], level="beginner", duration=5)
        assert engine.catalog_size == initial_size + 1
        assert course.title == "New Course"
        assert course.topics == ["testing"]
        assert course.id is not None

    def test_add_course_default_values(self, engine: CourseMap) -> None:
        course = engine.add_course("Minimal Course", topics=["topic"])
        assert course.level == "beginner"
        assert course.duration == 0


class TestRecommend:
    def test_recommend_returns_relevant_courses(self, engine: CourseMap) -> None:
        profile = UserProfile(skills=["python"], goals=["data-science"], level="intermediate")
        recs = engine.recommend(profile, n=3)
        assert len(recs) > 0
        assert len(recs) <= 3
        # Scores should be in descending order
        scores = [r.score for r in recs]
        assert scores == sorted(scores, reverse=True)

    def test_recommend_respects_max_n(self, engine: CourseMap) -> None:
        profile = UserProfile(skills=["python"], goals=["ml"], level="beginner")
        recs = engine.recommend(profile, n=2)
        assert len(recs) <= 2

    def test_recommend_empty_profile_returns_few_results(self, engine: CourseMap) -> None:
        profile = UserProfile(skills=[], goals=[], level="beginner")
        recs = engine.recommend(profile, n=10)
        # With no skills/goals overlap, only level-matching courses pass the threshold
        for rec in recs:
            assert rec.score >= engine.config.min_score


class TestFiltering:
    def test_filter_by_topic(self, engine: CourseMap) -> None:
        results = engine.filter_by_topic("python")
        assert len(results) >= 3
        for course in results:
            assert "python" in [t.lower() for t in course.topics]

    def test_filter_by_level(self, engine: CourseMap) -> None:
        results = engine.filter_by_level("beginner")
        assert len(results) >= 2
        for course in results:
            assert course.level.lower() == "beginner"

    def test_filter_by_topic_no_match(self, engine: CourseMap) -> None:
        results = engine.filter_by_topic("quantum-computing")
        assert len(results) == 0


class TestRating:
    def test_rate_course(self, engine: CourseMap) -> None:
        course = engine.add_course("Rated Course", topics=["test"], level="beginner")
        engine.rate_course(course.id, 4.5)
        engine.rate_course(course.id, 3.5)
        updated = engine.get_course(course.id)
        assert updated is not None
        assert updated.average_rating == 4.0
        assert updated.rating_count == 2

    def test_rate_course_invalid_rating(self, engine: CourseMap) -> None:
        course = engine.add_course("Bad Rating", topics=["test"])
        with pytest.raises(ValueError, match="between 1.0 and 5.0"):
            engine.rate_course(course.id, 6.0)

    def test_rate_course_not_found(self, engine: CourseMap) -> None:
        with pytest.raises(ValueError, match="not found"):
            engine.rate_course("nonexistent", 3.0)


class TestPopularAndPath:
    def test_get_popular(self, engine: CourseMap) -> None:
        courses = list(engine._courses.values())
        engine.rate_course(courses[0].id, 5.0)
        engine.rate_course(courses[1].id, 3.0)
        popular = engine.get_popular(n=2)
        assert len(popular) == 2
        assert popular[0].average_rating >= popular[1].average_rating

    def test_get_learning_path(self, engine: CourseMap) -> None:
        path = engine.get_learning_path("python")
        assert len(path) >= 2
        # Path should be ordered by level
        level_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        levels = [level_order.get(c.level, 99) for c in path]
        assert levels == sorted(levels)


class TestExport:
    def test_export_json(self, engine: CourseMap) -> None:
        profile = UserProfile(skills=["python"], goals=["ml"], level="intermediate")
        recs = engine.recommend(profile, n=2)
        output = engine.export(recs, format="json")
        data = json.loads(output)
        assert isinstance(data, list)
        assert len(data) == len(recs)
        assert "title" in data[0]
        assert "score" in data[0]

    def test_export_csv(self, engine: CourseMap) -> None:
        profile = UserProfile(skills=["python"], goals=["ml"], level="beginner")
        recs = engine.recommend(profile, n=2)
        output = engine.export(recs, format="csv")
        lines = output.strip().split("\n")
        assert len(lines) >= 2  # header + at least 1 row
        assert "title" in lines[0].lower()

    def test_export_markdown(self, engine: CourseMap) -> None:
        profile = UserProfile(skills=["python"], goals=["data-science"], level="beginner")
        recs = engine.recommend(profile, n=2)
        output = engine.export(recs, format="markdown")
        assert "| #" in output
        assert "Title" in output

    def test_export_invalid_format(self, engine: CourseMap) -> None:
        with pytest.raises(ValueError, match="Unsupported"):
            engine.export([], format="xml")  # type: ignore[arg-type]
