# API Reference

## Overview

This document provides detailed API reference for the Redfish Telemetry MRD Developer, including classes, methods, dataclasses, and exception handling. All modules include comprehensive type hints and follow modern Python best practices.

## Core Classes

### MRDGenerator

The main class for generating Metric Report Definitions.

```python
from src.mrd_generator import MRDGenerator, MRDGenerationError, MRDValidationError

# Initialize with optional configuration
generator = MRDGenerator(config=config_dict)

# Generate MRDs with error handling
try:
    mrds = generator.generate_all_mrds(classified_metrics)
except MRDGenerationError as e:
    print(f"MRD generation failed: {e}")
except MRDValidationError as e:
    print(f"MRD validation failed: {e}")
```

#### Methods

- `generate_mrd(metrics, metric_type, report_name=None)` - Generate MRD for specific type
- `generate_all_mrds(classified_metrics)` - Generate all MRDs from classified metrics
- `save_mrds_to_files(mrds, output_dir)` - Save MRDs to JSON files
- `create_collection_mrd(mrds)` - Create collection MRD referencing all individual MRDs
- `validate_mrd(mrd)` - Validate MRD against Redfish requirements

### MetricDefinition

Dataclass representing a metric definition within an MRD.

```python
from src.mrd_generator import MetricDefinition

# Create metric definition
metric_def = MetricDefinition(
    MetricId="cpu_temp_celsius",
    MetricProperties=["/redfish/v1/Chassis/1/Thermal#/Temperatures/0/ReadingCelsius"],
    DataType="Number",
    Units="Cel",
    Thresholds={"UpperCritical": {"Reading": 85, "Activation": "Increasing"}}
)
```

#### Fields

- `MetricId: str` - Unique identifier for the metric
- `MetricProperties: List[str]` - List of Redfish property URIs
- `DataType: Optional[str]` - Data type (Number, String, Boolean, etc.)
- `Units: Optional[str]` - Units of measurement
- `Thresholds: Optional[Dict]` - Threshold definitions for alerts

### MetricClassifier

Classifies metrics based on properties and source types.

```python
from src.metric_classifier import MetricClassifier, MetricType

# Initialize with optional custom mappings
classifier = MetricClassifier(custom_mappings)

# Extract metrics by type
performance_metrics = classifier.extract_metrics_by_type(
    metric_sources, 
    MetricType.PLATFORM_METRICS
)
```

### MockupParser

Parses Redfish mockup data to extract metric sources with full type hint support.

```python
from src.mockup_parser import MockupParser
from typing import Dict, List, Any

# Use as context manager for automatic resource cleanup
with MockupParser(mockup_path) as parser:
    mockup_data: Dict[str, Any] = parser.parse()
    metric_sources: List[Dict] = parser.get_metric_sources()
```

#### Methods

- `__init__(mockup_path: Union[str, Path])` - Initialize parser with mockup path
- `__enter__() -> MockupParser` - Context manager entry with automatic extraction
- `__exit__(exc_type, exc_val, exc_tb) -> None` - Context manager exit with cleanup
- `parse() -> Dict[str, Any]` - Parse mockup and return structured data
- `get_metric_sources() -> List[Dict]` - Extract all potential metric sources

## Dataclasses

### MetricDefinition

```python
@dataclass
class MetricDefinition:
    MetricId: str
    MetricProperties: List[str]
    DataType: Optional[str] = None
    Units: Optional[str] = None
    Thresholds: Optional[Dict] = None
```

## Custom Exceptions

The tool uses custom exceptions for better error handling and debugging:

### MRDGenerationError

Raised when MRD generation fails due to invalid input or configuration.

```python
try:
    mrd = generator.generate_mrd([], MetricType.PLATFORM_METRICS)
except MRDGenerationError as e:
    print(f"Cannot generate MRD: {e}")
```

### MRDValidationError

Raised when MRD validation fails against Redfish schema requirements.

```python
try:
    errors = generator.validate_mrd(invalid_mrd)
except MRDValidationError as e:
    print(f"MRD validation failed: {e}")
```

## Enums

### MetricType

Enumeration of supported metric categories:

```python
from src.metric_classifier import MetricType

# Available metric types
MetricType.PLATFORM_METRICS       # System-level metrics
MetricType.ENVIRONMENT_METRICS    # Temperature, power, fans
MetricType.PROCESSOR_METRICS      # CPU performance and status
MetricType.MEMORY_METRICS         # Memory capacity and performance
MetricType.ALARMS_METRICS         # Alerts and fault conditions
MetricType.STATUS_AND_COUNTER_METRICS  # Network and statistical counters
```

## Type Hints

All functions and methods include comprehensive type hints for better IDE support:

```python
def generate_mrd(
    self, 
    metrics: List[Dict], 
    metric_type: MetricType,
    report_name: Optional[str] = None
) -> Dict[str, Any]:
```

## Configuration API

### Environment Variables

- `REDFISH_MRD_SECRET_KEY` - Flask secret key for web interface security

### Configuration Dictionary Structure

```python
config = {
    "mrd_properties": {
        "ReportActions": ["RedfishEvent", "LogToMetricReportsCollection"],
        "Schedule": {"RecurrenceInterval": "PT60S"}
    },
    "metric_mappings": {
        "CPU Temperature": "cpu_temp_celsius"
    },
    "metric_type_configs": {
        "EnvironmentMetrics": {
            "recurrence_interval": "PT30S"
        }
    }
}
```

## Error Handling Best Practices

1. **Use specific exception types** for different error conditions
2. **Log errors** with appropriate context for debugging
3. **Provide meaningful error messages** to users
4. **Use try-catch blocks** around file operations and API calls
5. **Handle both custom and built-in exceptions** appropriately

```python
from src.mrd_generator import MRDGenerator, MRDGenerationError, MRDValidationError
from src.mockup_parser import MockupParser
import logging

logger = logging.getLogger(__name__)

try:
    with MockupParser(mockup_path) as parser:
        mockup_data = parser.parse()
        generator = MRDGenerator(config)
        mrds = generator.generate_all_mrds(classified_metrics)
except FileNotFoundError:
    logger.error(f"Mockup file not found: {mockup_path}")
except MRDGenerationError as e:
    logger.error(f"MRD generation failed: {e}")
except MRDValidationError as e:
    logger.error(f"MRD validation failed: {e}")
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
```

## Module Structure

The codebase is organized into focused modules with clear responsibilities:

```
src/
├── __init__.py                # Package initialization
├── mrd_generator.py          # MRD generation with dataclasses and exceptions
├── metric_classifier.py      # Metric classification with type hints
└── mockup_parser.py         # Mockup parsing with context managers
```

### Import Best Practices

```python
# Import specific classes and functions
from src.mrd_generator import MRDGenerator, MRDGenerationError, MetricDefinition
from src.metric_classifier import MetricClassifier, MetricType
from src.mockup_parser import MockupParser

# Type hints for better IDE support
from typing import Dict, List, Optional, Any
```

## Testing

The API includes comprehensive unit tests using pytest:

```python
# Run all tests
pytest

# Run specific test file
pytest tests/test_mrd_generator.py

# Run with coverage
pytest --cov=src

# Run with type checking
mypy src/
```

Test files are located in the `tests/` directory and follow the naming convention `test_*.py`.