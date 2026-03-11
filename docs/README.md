# Redfish Telemetry MRD Developer - Documentation Index

This directory contains comprehensive documentation for understanding and customizing the BMC Metric Report Definition Developer Tool.

## 📚 Documentation Overview

### Core Documentation

1. **[README.md](../README.md)** - Main project overview and usage instructions
2. **[Metric Classification Guide](METRIC_CLASSIFICATION_GUIDE.md)** - Complete classification system reference
3. **[Classification Examples](CLASSIFICATION_EXAMPLES.md)** - Real-world examples from mockup data

### Quick Links

| Document | Purpose | Audience |
|----------|---------|----------|
| [Classification Guide](METRIC_CLASSIFICATION_GUIDE.md) | Understand how metrics are categorized | Developers, System Administrators |
| [Classification Examples](CLASSIFICATION_EXAMPLES.md) | See real examples from BMC mockups | BMC Engineers, DevOps Teams |
| [Configuration Guide](../config/metric_mappings.yaml) | Customize classification rules | System Integrators |

## 🎯 Use Cases by Role

### **BMC Developers**
- Review [Classification Examples](CLASSIFICATION_EXAMPLES.md) to understand how your BMC metrics will be categorized
- Customize [metric_mappings.yaml](../config/metric_mappings.yaml) for vendor-specific naming conventions
- Use the tool to validate metric coverage across all categories

### **System Administrators**  
- Use [Classification Guide](METRIC_CLASSIFICATION_GUIDE.md) to understand metric organization
- Generate MRDs for specific metric types needed for monitoring
- Validate MRD outputs against organizational standards

### **DevOps Engineers**
- Integrate the tool into CI/CD pipelines for automatic MRD generation
- Use examples to understand metric structure for monitoring platform integration
- Customize classifications for specific deployment environments

### **Standards Compliance Teams**
- Verify generated MRDs comply with Redfish specifications
- Use validation features to ensure schema compliance
- Review classification logic for standards alignment

## 📖 Getting Started Guide

### 1. **First Time Users**
```bash
# Install dependencies
./setup.sh

# Analyze a mockup to understand available metrics
python mrd_tool.py analyze --mockup-path ./mockups/your_mockup.tgz

# Generate MRDs for all metric types  
python mrd_tool.py generate --mockup-path ./mockups/your_mockup.tgz --output-dir ./output
```

### 2. **Understanding Classifications**
- Read [Metric Classification Guide](METRIC_CLASSIFICATION_GUIDE.md) sections 1-3
- Review [Classification Examples](CLASSIFICATION_EXAMPLES.md) for your BMC type
- Run analysis on your mockup data to see actual classifications

### 3. **Customizing for Your Environment**
- Edit [config/metric_mappings.yaml](../config/metric_mappings.yaml) 
- Add custom keywords, properties, or sensor types
- Test changes with your mockup data

### 4. **Advanced Usage**
- Generate MRDs for specific metric types only
- Validate generated MRDs against Redfish schema
- Integrate into automated workflows

## 🔧 Configuration and Customization

### Classification Rules Location
- **Primary Config**: `config/metric_mappings.yaml`
- **Code Implementation**: `src/metric_classifier.py` 
- **Examples**: `docs/CLASSIFICATION_EXAMPLES.md`

### Common Customizations

#### Adding Vendor-Specific Keywords
```yaml
EnvironmentMetrics:
  keywords:
    - your_vendor_term
    - custom_component_name
```

#### Custom Sensor Types
```yaml
ProcessorMetrics:
  sensor_types:
    - CustomCPUSensor
    - VendorSpecificType
```

#### New Metric Categories
```python
# In src/metric_classifier.py
class MetricType(Enum):
    CUSTOM_METRICS = "CustomMetrics"
```

## 📊 Real-World Examples

### BMC Types Tested
- **Full BMC mockup** - Power distribution, sensors, and chassis data
- **RAS-focused mockup** - Complete system with processors, memory, and error reporting

### Metric Coverage
- **PlatformMetrics**: System health, power states, boot progress
- **EnvironmentMetrics**: Temperature, fan speed, voltage, current
- **ProcessorMetrics**: CPU specifications, utilization
- **MemoryMetrics**: DIMM capacity, speed, type
- **AlarmsMetrics**: Health status, fault conditions  
- **StatusAndCounterMetrics**: Network statistics, counters

## 🛠️ Troubleshooting

### Common Issues

1. **Missing Metrics**: Check if resources exist in mockup
2. **Incorrect Classifications**: Review keyword/property matching
3. **Empty Categories**: Verify mockup contains relevant resources
4. **Validation Errors**: Check MRD structure against Redfish schema

### Debug Commands
```bash
# Verbose analysis
python mrd_tool.py -v analyze --mockup-path ./mockups/your_mockup.tgz

# Specific metric types only
python mrd_tool.py generate --metric-types PlatformMetrics --mockup-path ./mockups/your_mockup.tgz

# Validate generated MRDs
python mrd_tool.py validate --mrd-file ./output/platformmetrics_mrd.json
```

## 🤝 Contributing

### Documentation Improvements
- Add examples from new BMC types
- Enhance classification explanations
- Update configuration examples

### Tool Enhancements  
- New metric types
- Enhanced classification logic
- Additional validation rules

## 📞 Support

### Questions About Classifications?
- Review [Classification Guide](METRIC_CLASSIFICATION_GUIDE.md)
- Check [real examples](CLASSIFICATION_EXAMPLES.md) 
- Run analysis on your specific mockup

### Need Custom Classifications?
- Edit [metric_mappings.yaml](../config/metric_mappings.yaml)
- Test with your mockup data
- Validate generated MRDs

### Found Issues?
- Check troubleshooting section above
- Review tool logs with verbose mode
- Verify mockup data structure

This documentation provides comprehensive guidance for understanding, using, and customizing the Redfish Telemetry MRD Developer for your specific BMC implementation and organizational needs.