# Contributing to Redfish Telemetry MRD Developer

Thank you for your interest in contributing to the Redfish Telemetry MRD Developer! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Submitting Changes](#submitting-changes)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct v2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
By participating, you are expected to uphold this code.

Please report unacceptable behavior by opening a [GitHub issue](https://github.com/harira-microsoft/redfish-telemetry-mrd-developer/issues) requesting a private channel.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git for version control
- Basic understanding of Redfish specification
- Familiarity with Flask for web interface contributions

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/harira-microsoft/redfish-telemetry-mrd-developer.git
   cd redfish-telemetry-mrd-developer
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov flake8 black  # Development tools
   ```

4. **Verify setup**
   ```bash
   python3 mrd_tool.py --help
   python3 -c "from app import app; print('Setup successful')"
   ```

## Contribution Guidelines

### Types of Contributions

We welcome several types of contributions:

1. **Bug Reports**: Help us identify and fix issues
2. **Feature Requests**: Suggest new functionality
3. **Code Contributions**: Implement fixes or new features
4. **Documentation**: Improve guides, examples, and API docs
5. **Testing**: Add test cases or improve test coverage

### Bug Reports

When reporting bugs, please include:

- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Environment details** (Python version, OS, etc.)
- **Log output** if applicable
- **Sample files** that trigger the issue (if possible)

Use the bug report template:

```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior  
What actually happens

## Environment
- Python version:
- Operating System:
- Tool version:

## Additional Context
Any other relevant information
```

### Feature Requests

For feature requests, please provide:

- **Use case description**: Why is this feature needed?
- **Proposed solution**: How should it work?
- **Alternatives considered**: What other approaches were considered?
- **Implementation ideas**: How might this be implemented?

## Submitting Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-metric-type` for new features
- `fix/handle-empty-mockups` for bug fixes  
- `docs/update-api-guide` for documentation
- `test/add-validation-tests` for testing

### Commit Messages

Follow conventional commit format:

```
type(scope): description

Detailed explanation of what changed and why.
```

Examples:
- `feat(parser): add support for compressed mockups`
- `fix(ui): resolve file upload validation error`
- `docs(readme): update installation instructions`
- `test(classifier): add edge case tests`

### Pull Request Process

1. **Create a branch** for your changes
2. **Make your changes** following code standards
3. **Add or update tests** for your changes
4. **Update documentation** if needed
5. **Run the test suite** to ensure nothing breaks
6. **Submit a pull request** with a clear description

#### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Documentation updated
- [ ] Changes are backward compatible (or breaking changes documented)
```

## Testing

### Running Tests

```bash
# Run basic functionality tests
python3 mrd_tool.py --help
python3 -c "from app import app; print('Import test passed')"

# Run linting
flake8 src/ app.py mrd_tool.py

# If you have pytest installed
pytest tests/ -v
```

### Adding Tests

When adding new functionality:

1. **Add unit tests** for new functions/classes
2. **Add integration tests** for new workflows
3. **Test edge cases** and error conditions
4. **Ensure good test coverage** for new code

### Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for workflows  
├── fixtures/       # Test data files
└── conftest.py     # Shared test configuration
```

## Documentation

### Types of Documentation

1. **Code Comments**: Explain complex logic and algorithms
2. **Docstrings**: Document functions, classes, and modules
3. **User Documentation**: Guides, examples, and tutorials
4. **Technical Documentation**: Architecture and implementation details

### Documentation Standards

- Use clear, concise language
- Include practical examples
- Keep documentation up-to-date with code changes
- Follow Markdown formatting standards for .md files

### API Documentation

Use Python docstring conventions:

```python
def generate_mrd(mockup_path: str, config: dict = None) -> dict:
    """
    Generate MetricReportDefinition from mockup data.
    
    Args:
        mockup_path: Path to Redfish mockup file or directory
        config: Optional configuration dictionary
        
    Returns:
        Dictionary containing generated MRD data
        
    Raises:
        ValueError: If mockup_path is invalid
        FileNotFoundError: If mockup file doesn't exist
    """
```

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- **Add type hints to all functions and methods**
- **Use dataclasses for structured data objects**
- **Add docstrings to all public classes and methods**
- **Use custom exceptions for domain-specific errors**
- **Write unit tests for new functionality**
- Keep functions focused and single-purpose
- Add comments for complex logic
- Limit line length to 88 characters (black default)

#### Type Hints Example
```python
def generate_mrd(
    self, 
    metrics: List[Dict], 
    metric_type: MetricType,
    report_name: Optional[str] = None
) -> Dict[str, Any]:
```

#### Dataclass Example
```python
@dataclass
class MetricDefinition:
    MetricId: str
    MetricProperties: List[str]
    DataType: Optional[str] = None
```

#### Custom Exception Example
```python
class MRDGenerationError(Exception):
    """Exception raised for errors during MRD generation."""
    pass
```

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors appropriately
- Handle edge cases gracefully

### Performance Considerations

- Optimize for readability first, performance second
- Profile before optimizing
- Consider memory usage with large mockup files
- Use generators for processing large datasets

## Getting Help

If you need help or have questions:

1. **Check the documentation** in the `docs/` directory
2. **Search existing issues** on GitHub
3. **Ask questions** by opening a discussion
4. **Join community channels** (if available)

## Recognition

Contributors will be recognized in:

- `CONTRIBUTORS.md` file (if created)
- Release notes for significant contributions
- Repository insights and contribution graphs

Thank you for contributing to the Redfish Telemetry MRD Developer!