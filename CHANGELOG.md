# Changelog

All notable changes to the Redfish Telemetry MRD Developer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-11-15

### Added
- **Core MRD Generation Engine**
  - Redfish MetricReportDefinition generation compliant with v1.3.0 schema
  - Support for 6 metric categories: PlatformMetrics, EnvironmentMetrics, ProcessorMetrics, MemoryMetrics, AlarmsMetrics, StatusAndCounterMetrics
  - Automatic metric classification from Redfish mockup data
  - Built-in schema validation

- **CLI Interface**
  - Comprehensive command-line tool with `analyze`, `generate`, and `validate` commands
  - Rich help system with detailed examples and workflow guidance
  - Support for custom configuration files and selective metric generation
  - Verbose logging and error reporting

- **Web Interface**
  - Modern Flask-based web UI with Bootstrap 5 styling
  - File upload for mockup processing
  - Interactive analysis and configuration forms
  - Real-time MRD generation with progress tracking
  - Integrated documentation viewer with markdown rendering

- **Configuration System**
  - YAML-based configuration for MRD properties customization
  - Custom metric ID mappings support
  - Per-metric-type configuration overrides
  - Multiple configuration examples included

- **Documentation**
  - Comprehensive README with usage examples
  - Technical documentation covering all features
  - Web-based documentation viewer
  - CLI examples and workflow guides

### Technical Features
- **Mockup Parser**: Robust parsing of Redfish mockup files (directories and .tgz archives)
- **Metric Classifier**: Intelligent classification using keyword-based algorithms
- **MRD Generator**: Schema-compliant JSON generation with proper @odata formatting
- **Validation Engine**: Built-in validation against Redfish schema requirements
- **Directory Organization**: Clean, professional project structure
- **Error Handling**: Comprehensive error handling and user-friendly messages

### Infrastructure
- **GitHub Workflows**: CI/CD pipeline with automated testing and releases
- **Code Quality**: Linting, security checks, and documentation validation
- **Cross-Platform**: Tested on Python 3.9+ across multiple environments
- **Apache 2.0 License**: Open source with permissive licensing

## [0.9.0] - Development Phase

### Development Milestones
- Initial mockup parsing implementation
- Basic metric classification algorithms
- Early CLI prototype
- Schema compliance research and implementation
- Web interface prototype development
- Configuration system design and implementation
- Documentation creation and organization
- Testing and validation framework

---

## Release Notes Template

### Version X.Y.Z - YYYY-MM-DD

#### Added
- New features and capabilities

#### Changed  
- Modifications to existing functionality

#### Fixed
- Bug fixes and corrections

#### Removed
- Deprecated or removed features

#### Security
- Security-related improvements