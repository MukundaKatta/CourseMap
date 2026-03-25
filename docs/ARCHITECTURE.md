# Architecture

## Overview

CourseMap is a content-based filtering recommendation engine for courses and learning resources. It matches learner profiles (skills, goals, level) against a course catalog to produce ranked recommendations.

## Components

### Core Engine (`src/coursemap/core.py`)

The `CourseMap` class is the main entry point. It manages:

- **Course Catalog**: An in-memory dictionary of `Course` objects keyed by unique ID.
- **User Profiles**: `UserProfile` objects representing learner skills, goals, and current level.
- **Recommendations**: Generated via content-based filtering using topic overlap scoring.
- **Export**: Results can be serialized to JSON, CSV, or Markdown.

### Data Models

All models use **Pydantic v2** for validation and serialization:

- `Course` -- title, topics, level, duration, ratings
- `UserProfile` -- skills, goals, level
- `ScoredCourse` -- extends Course with a relevance score

### Scoring Algorithm (`src/coursemap/utils.py`)

The relevance score is a weighted combination of:

| Factor | Weight | Description |
|--------|--------|-------------|
| Skill overlap | 0.40 | Jaccard similarity between course topics and user skills |
| Goal overlap | 0.40 | Jaccard similarity between course topics and user goals |
| Level match | 0.15 | Bonus when course level matches user level |
| Rating bonus | 0.05 | Normalized average course rating (0-5 mapped to 0-1) |

### Configuration (`src/coursemap/config.py`)

Runtime settings loaded from environment variables with sensible defaults. Uses Pydantic for validation.

## Data Flow

```
User Profile (skills, goals, level)
        |
        v
  +------------------+
  |  CourseMap Engine  |
  |                    |
  |  For each course:  |
  |  1. Compute topic  |
  |     overlap score  |
  |  2. Add level      |
  |     match bonus    |
  |  3. Add rating     |
  |     bonus          |
  |  4. Filter by      |
  |     min_score      |
  +------------------+
        |
        v
  Sorted recommendations
        |
        v
  Export (JSON / CSV / Markdown)
```

## Design Decisions

1. **In-memory storage**: Simplicity first. No database dependency for the core library.
2. **Pydantic models**: Type safety and validation at the data boundary.
3. **Jaccard similarity**: Simple, interpretable, and effective for tag-based matching.
4. **Pluggable config**: Environment-based configuration makes it easy to adjust without code changes.
