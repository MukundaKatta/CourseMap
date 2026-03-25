# Contributing to CourseMap

Thank you for considering contributing to CourseMap! This document provides guidelines for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Install development dependencies:

```bash
make dev
```

## Development Workflow

1. Create a feature branch from `main`:

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and write tests.

3. Run the full test suite:

```bash
make all
```

4. Commit your changes with a descriptive message:

```bash
git commit -m "feat: add new filtering strategy"
```

## Code Style

- Follow PEP 8 conventions.
- Use type hints for all function signatures.
- Format code with `make fmt`.
- Lint with `make lint`.

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for adding or updating tests
- `refactor:` for code refactoring

## Pull Requests

- Keep PRs focused on a single change.
- Include tests for new functionality.
- Update documentation if needed.
- Ensure CI passes before requesting review.

## Reporting Issues

- Use GitHub Issues to report bugs or request features.
- Include steps to reproduce, expected behavior, and actual behavior.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
