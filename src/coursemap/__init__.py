"""CourseMap -- Course recommendation engine using content-based filtering."""

from coursemap.core import Course, CourseMap, ScoredCourse, UserProfile
from coursemap.config import CourseMapConfig

__version__ = "0.1.0"
__all__ = [
    "Course",
    "CourseMap",
    "CourseMapConfig",
    "ScoredCourse",
    "UserProfile",
]
