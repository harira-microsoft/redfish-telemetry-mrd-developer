# Development Guide

## Development Setup

Follow these steps to set up the development environment:

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/harira-microsoft/redfish-telemetry-mrd-developer.git
   cd redfish-telemetry-mrd-developer
   ```

3. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov mypy  # Development tools
   ```

5. **Set up environment variables**:
   ```bash
   export REDFISH_MRD_SECRET_KEY="development-secret-key"
   ```

6. **Run tests** to verify setup:
   ```bash
   pytest
   ```

## Code Quality Standards

### Type Hints

All functions and methods must have type annotations:

```python
def generate_mrd(
    self, 
    metrics: List[Dict], 
    metric_type: MetricType,
    report_name: Optional[str] = None
) -> Dict[str, Any]:
    """Generate MRD with proper type hints."""
    pass
```

### Dataclasses

Use dataclasses for structured data objects:

```python
from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class MetricDefinition:
    MetricId: str
    MetricProperties: List[str]
    DataType: Optional[str] = None
    Units: Optional[str] = None
    Thresholds: Optional[Dict] = None
```

### Docstrings

All public classes and methods must have comprehensive docstrings:

```python
def generate_mrd(self, metrics: List[Dict], metric_type: MetricType) -> Dict[str, Any]:
    """
    Generate a Metric Report Definition for a specific metric type.

    Args:
        metrics: List of metric dicts to include in the MRD.
        metric_type: The MetricType enum value for this MRD.

    Returns:
        MRD dictionary ready for JSON serialization.

    Raises:
        MRDGenerationError: If no metrics provided or generation fails.
    """
```

### Error Handling

Use custom exceptions for domain-specific errors:

```python
class MRDGenerationError(Exception):
    """Exception raised for errors during MRD generation."""
    pass

class MRDValidationError(Exception):
    """Exception raised for errors during MRD validation."""
    pass
```

### Testing

Write unit tests for all new functionality using proper import paths:

```python
# tests/test_mrd_generator.py
import sys
import os
import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mrd_generator import MRDGenerator, MRDGenerationError, MRDValidationError
from src.metric_classifier import MetricType

def test_generate_mrd_with_valid_metrics():
    generator = MRDGenerator()
    metrics = [{'source_id': 'sys1', 'metric_name': 'PowerState'}]
    mrd = generator.generate_mrd(metrics, MetricType.PLATFORM_METRICS)
    assert mrd['Id'] == 'PlatformMetricsReport'
    assert len(mrd['Metrics']) == 1
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_mrd_generator.py

# Run specific test function
pytest tests/test_mrd_generator.py::test_generate_mrd_no_metrics
```

### Coverage Analysis

```bash
# Run tests with coverage
pytest --cov=src

# Generate HTML coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Type Checking

```bash
# Run type checking
mypy src/

# Type check specific file
mypy src/mrd_generator.py
```

## Code Organization

### Directory Structure

```
src/
├── __init__.py
├── mrd_generator.py      # MRD generation logic
├── metric_classifier.py # Metric classification
└── mockup_parser.py     # Mockup parsing

tests/
├── __init__.py
├── test_mrd_generator.py     # MRD generator tests
├── test_metric_classifier.py # Classifier tests
└── test_mockup_parser.py     # Parser tests
```

### Module Dependencies

- Keep modules loosely coupled
- Use dependency injection where appropriate
- Avoid circular imports
- Import from specific modules, not packages

```python
# Good
from metric_classifier import MetricType

# Avoid
from src import *
```

## Pull Request Process

### Before Submitting

1. **Run all tests**: `pytest`
2. **Check type hints**: `mypy src/`
3. **Verify code style**: `flake8 src/`
4. **Update documentation** if needed
5. **Add tests** for new functionality

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Added unit tests
- [ ] All tests pass
- [ ] Type checking passes

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### Code Review Guidelines

#### For Authors

- Keep PRs focused and small
- Write clear commit messages
- Respond to feedback constructively
- Update based on review comments

#### For Reviewers

- Review for correctness, not style preferences
- Suggest improvements, don't just point out problems
- Check test coverage for new code
- Verify documentation is updated

## Common Development Tasks

### Adding a New Metric Type

1. **Update MetricType enum**:
   ```python
   class MetricType(Enum):
       NEW_METRIC_TYPE = "NewMetricType"
   ```

2. **Add classification logic**:
   ```python
   def _extract_new_metrics(self, data: Dict, base: Dict) -> List[Dict]:
       # Implementation here
   ```

3. **Update mappings**:
   ```python
   MetricType.NEW_METRIC_TYPE: {
       "keywords": ["new", "metric"],
       "properties": ["NewProperty"]
   }
   ```

4. **Add tests**:
   ```python
   def test_new_metric_classification():
       # Test implementation
   ```

### Adding Configuration Options

1. **Update config schema** in documentation
2. **Add validation** in MRDGenerator.__init__()
3. **Update example configs** in config/ directory
4. **Add tests** for new configuration behavior

### Debugging Tips

#### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Use pytest fixtures for test data

```python
@pytest.fixture
def sample_metrics():
    return [
        {'source_id': 'sys1', 'metric_name': 'PowerState'},
        {'source_id': 'cpu1', 'metric_name': 'Temperature'}
    ]
```

#### Interactive debugging with pdb

```python
import pdb; pdb.set_trace()  # Add breakpoint
```

## Performance Considerations

- Use context managers for file operations
- Avoid loading large files into memory unnecessarily
- Use generators for large datasets
- Profile code with `cProfile` if performance issues arise

## Security Guidelines

- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all user inputs
- Sanitize file paths to prevent directory traversal
- Use secure file handling practices