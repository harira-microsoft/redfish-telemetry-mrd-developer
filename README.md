# Redfish Telemetry MRD Developer

![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3%2B-green.svg)
![Redfish](https://img.shields.io/badge/redfish-v1.3.0-orange.svg)

A comprehensive tool for generating Redfish MetricReportDefinition (MRD) files from Redfish mockup data, compliant with Redfish v1.3.0 schema.

## Features

- **Metric Classification**: Automatically classifies metrics into 6 categories:
  - Performance: CPU utilization, memory bandwidth, I/O throughput
  - Environmental: Temperature, power consumption, fan speeds
  - Health: Component status, alert conditions, diagnostic results
  - Error: ECC errors, link errors, timeout events
  - Security: Authentication attempts, encryption status, access violations
  - Lifecycle: Boot count, power cycles, firmware versions

- **Flexible Configuration**: YAML-based configuration system for customizing:
  - MRD properties (schedule, report actions, etc.)
  - Custom metric ID mappings
  - Per-metric-type overrides

- **Multiple Interfaces**:
  - Command-line interface with comprehensive help
  - Web UI for easier interaction
  - Python API for integration

- **Modern Codebase**:
  - Full type hints for better IDE support and maintainability
  - Python dataclasses for structured metric representation
  - Custom exception classes for domain-specific errors
  - Comprehensive unit tests with pytest

- **Validation**: Built-in validation against Redfish schema

## Screenshots

### Web Interface Dashboard
The intuitive web interface provides easy access to all tool features:

### CLI Interface  
Powerful command-line interface with comprehensive help:

```bash
$ python3 mrd_tool.py --help
$ python3 mrd_tool.py examples
```

## Installation

### Prerequisites

- Python 3.9+
- Required Python packages:
  ```bash
  pip install -r requirements.txt
  ```

### Quick Start

1. Clone or download this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables (optional): `export REDFISH_MRD_SECRET_KEY="your-secret-key"`
4. Run analysis: `python3 mrd_tool.py analyze -m your_mockup.tgz`
5. Generate MRDs: `python3 mrd_tool.py generate -m your_mockup.tgz`

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_mrd_generator.py

# Run with verbose output and coverage
pytest -v --cov=src
```

## Usage

### Command Line Interface

```bash
# Show all available commands and options
python3 mrd_tool.py --help

# Show comprehensive examples and workflow guide
python3 mrd_tool.py examples

# Analyze mockup data
python3 mrd_tool.py analyze -m redfish_mockup.tgz

# Generate all MRD types
python3 mrd_tool.py generate -m redfish_mockup.tgz

# Generate specific metric types only
python3 mrd_tool.py generate -m mockup/ -t PlatformMetrics,EnvironmentMetrics

# Use custom configuration
python3 mrd_tool.py generate -m mockup.tgz -c config/custom_config.yaml

# Validate generated MRD
python3 mrd_tool.py validate -f output/performancemetrics_mrd.json
```

### Web Interface

Launch the web UI for a more user-friendly experience:

```bash
python3 app.py
```

Then open http://localhost:5000 in your browser.

The web interface provides:
- File upload for mockup files
- Interactive analysis results
- Configuration form builder
- Real-time MRD generation
- Download management

## Configuration

Create a YAML configuration file to customize MRD generation:

```yaml
# Global MRD properties applied to all metric types
report_actions:
  - "RedfishEvent"
  - "LogToMetricReportsCollection"
report_updates: "Overwrite"
recurrence_interval: "PT60S"

# Custom metric ID mappings for specific sensors
metric_mappings:
  "Temp_CPU0_Temperature": "CPU0_CoreTemperature"
  "Fan_1A_FanSpeed": "SystemFan_1A_Speed"

# Per-metric-type overrides
metric_type_configs:
  EnvironmentMetrics:
    recurrence_interval: "PT30S"  # Slower updates for environmental data
  ProcessorMetrics:
    recurrence_interval: "PT10S"  # Faster updates for CPU metrics
    report_actions: ["RedfishEvent"]
```

## Output Files

Generated MRDs are named by metric type:
- `platformmetrics_mrd.json`
- `environmentmetrics_mrd.json`
- `processormetrics_mrd.json`
- `memorymetrics_mrd.json`
- `alarmsmetrics_mrd.json`
- `statusandcountermetrics_mrd.json`
- `collection.json` (links all MRDs)

Each file contains a complete MetricReportDefinition with proper @odata.type and @odata.id, classified metrics for that type, configured properties and schedule, and valid Redfish v1.3.0 schema compliance.

## Examples

### Basic Workflow

1. **Analyze**: `python3 mrd_tool.py analyze -m redfish_mockup.tgz`
2. **Configure**: Create a configuration file (optional)
3. **Generate**: `python3 mrd_tool.py generate -m redfish_mockup.tgz -c config.yaml`
4. **Validate**: `python3 mrd_tool.py validate -f output/platformmetrics_mrd.json`

### Advanced Usage

Generate only specific metric types with custom output directory:
```bash
python3 mrd_tool.py generate \
  -m large_mockup.tgz \
  -t PlatformMetrics,EnvironmentMetrics \
  -c high_frequency_config.yaml \
  -o /custom/output/path/
```

For comprehensive examples and detailed documentation, run:
```bash
python3 mrd_tool.py examples
```

## Architecture

### Core Components

- **MockupParser**: Extracts telemetry data from Redfish mockups
- **MetricClassifier**: Classifies metrics into the six categories using configurable mappings
- **MRDGenerator**: Generates schema-compliant MetricReportDefinitions with dataclass-based metric definitions
- **Configuration System**: YAML-based customization framework with environment variable support
- **Error Handling**: Custom exception classes (MRDGenerationError, MRDValidationError) for better debugging
- **Testing Framework**: Comprehensive unit tests using pytest for reliability

### File Structure

```
redfish-telemetry-mrd-developer/
├── README.md                 # Main documentation
├── requirements.txt          # Python dependencies
├── mrd_tool.py              # CLI interface
├── app.py                   # Web interface
├── src/                     # Core source code
│   ├── __init__.py          # Package init
│   ├── mockup_parser.py     # Mockup data extraction
│   ├── metric_classifier.py # Metric classification logic
│   └── mrd_generator.py     # MRD generation engine
├── templates/               # Web UI templates
├── config/                  # Configuration examples
├── examples/                # Usage examples and sample outputs
├── docs/                    # Comprehensive documentation
├── tests/                   # Unit tests
├── mockups/                 # Place mockup files here (gitignored)
└── outputs/                 # Generated MRD output files
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Mockup parsing errors**: Verify mockup file format and accessibility

3. **Configuration errors**: Check YAML syntax and valid property values

4. **Validation failures**: Review generated MRD against error messages

### Getting Help

- Use `--help` with any command for detailed usage information
- Run `python3 mrd_tool.py examples` for comprehensive usage examples
- Check the web UI at http://localhost:5000 for interactive guidance

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository** and create your feature branch
2. **Follow coding standards** and add tests for new features  
3. **Update documentation** for any API changes
4. **Submit a pull request** with a clear description of changes

### Development Setup

```bash
# Clone the repository
git clone https://github.com/harira-microsoft/redfish-telemetry-mrd-developer.git
cd redfish-telemetry-mrd-developer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python3 -m pytest tests/
```

### Reporting Issues

Please use the [GitHub Issues](https://github.com/harira-microsoft/redfish-telemetry-mrd-developer/issues) page to:
- Report bugs with detailed reproduction steps
- Request new features with use case descriptions  
- Ask questions about usage or configuration

## Acknowledgments

- DMTF Redfish specification and schema contributors
- Open source community for excellent Python libraries
- BMC vendors providing mockup data for testing