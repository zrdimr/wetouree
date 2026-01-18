# Contributing to Pulau Harapan Tourism Management Application

Thank you for your interest in contributing! We welcome all contributions that help improve this platform.

## 🛠️ Development Setup

1. Fork the repository and clone it locally.
2. Follow the setup instructions in the [README.md](README.md).
3. Create a new branch for your feature or fix: `git checkout -b feature/your-feature-name`.

## 📐 Coding Standards

### Pylint
We maintain a strict **10.00/10** score. Before submitting a PR, ensure your code passes:
```bash
pylint --rcfile=.pylintrc backend/ frontend/
```

### Testing
Write tests for any new features in the `tests/` directory. All tests must pass:
```bash
pytest tests/
```

## 📝 Pull Request Process

1. Ensure your code follows the established architecture (FastAPI backend / Flask frontend).
2. Update the `README.md` or other documentation if your change introduces new behavior.
3. Your PR must pass all CI checks (Pylint, Pytest, Smoke Test) before it can be merged.
4. Describe your changes clearly in the PR template.

## 🐛 Reporting Bugs

Use the **Bug Report** issue template to provide detailed information about the issue, including steps to reproduce and environment details.

## 💡 Feature Requests

We encourage you to open a **Feature Request** if you have ideas for new capabilities!

---
By contributing, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).
