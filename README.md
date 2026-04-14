# CourseMap — Course recommendation engine — content-based filtering, learning paths, topic matching

Course recommendation engine — content-based filtering, learning paths, topic matching.

## Why CourseMap

CourseMap exists to make this workflow practical. Course recommendation engine — content-based filtering, learning paths, topic matching. It favours a small, inspectable surface over sprawling configuration.

## Features

- `Course` — exported from `src/coursemap/core.py`
- `UserProfile` — exported from `src/coursemap/core.py`
- `ScoredCourse` — exported from `src/coursemap/core.py`
- Included test suite
- Dedicated documentation folder

## Tech Stack

- **Runtime:** Python
- **Tooling:** Pydantic

## How It Works

The codebase is organised into `docs/`, `src/`, `tests/`. The primary entry points are `src/coursemap/core.py`, `src/coursemap/__init__.py`. `src/coursemap/core.py` exposes `Course`, `UserProfile`, `ScoredCourse` — the core types that drive the behaviour.

## Getting Started

```bash
pip install -e .
```

## Usage

```python
from coursemap.core import Course

instance = Course()
# See the source for the full API
```

## Project Structure

```
CourseMap/
├── .env.example
├── CONTRIBUTING.md
├── Makefile
├── README.md
├── docs/
├── pyproject.toml
├── src/
├── tests/
```