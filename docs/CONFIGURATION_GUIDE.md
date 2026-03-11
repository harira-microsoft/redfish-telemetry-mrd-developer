# MRD Configuration Guide

This guide demonstrates how to use the new configurable MRD properties and custom metric mappings.

## Configuration File Structure

Create a YAML configuration file with the following structure:

```yaml
# Global MRD Properties
report_actions: ["RedfishEvent", "LogToMetricReportsCollection"]
report_updates: "Overwrite"
append_limit: 100
heartbeat_interval: "PT0S"
recurrence_interval: "PT60S"

# Per-Type Configuration
metric_type_configs:
  EnvironmentMetrics:
    recurrence_interval: "PT30S"
  ProcessorMetrics:
    recurrence_interval: "PT10S"

# Custom Metric Mappings
metric_mappings:
  "Temp CPU0_Temperature": "CPU0_CoreTemp"
  
# Custom Property Mappings
metric_properties_mappings:
  "CPU0_CoreTemp":
    - "/redfish/v1/Systems/1/Processors/CPU0/Metrics#TemperatureCelsius"
```

## Usage Examples

### Basic Usage with Configuration

```bash
# Generate MRDs with custom configuration
python mrd_tool.py generate -m /path/to/mockup.tgz -c config/my_config.yaml -o ./output

# Analyze with configuration
python mrd_tool.py analyze -m /path/to/mockup.tgz -c config/my_config.yaml
```

### Configuration Options

#### 1. Report Actions
Controls what happens when metrics are collected:
- `"RedfishEvent"` - Send Redfish events
- `"LogToMetricReportsCollection"` - Store in collection
- `"CollectionTimeSpecified"` - Collect at specified times

#### 2. Report Updates
Controls how new metric reports are handled:
- `"Overwrite"` - Replace previous report
- `"AppendWrapsWhenFull"` - Append, wrap when full
- `"AppendStopsWhenFull"` - Append, stop when full
- `"NewReport"` - Create new report each time

#### 3. Intervals (ISO 8601 Duration)
- `"PT0S"` - No interval/heartbeat
- `"PT30S"` - 30 seconds
- `"PT5M"` - 5 minutes
- `"PT1H"` - 1 hour

### Example: Environmental Monitoring Configuration

```yaml
# Optimized for environmental monitoring
report_actions: ["RedfishEvent"]
report_updates: "Overwrite"
recurrence_interval: "PT30S"  # 30 second updates
heartbeat_interval: "PT5M"    # 5 minute heartbeat

metric_type_configs:
  EnvironmentMetrics:
    recurrence_interval: "PT15S"  # Faster for temperature/fans
  AlarmsMetrics:
    report_actions: ["RedfishEvent", "LogToMetricReportsCollection"]
    report_updates: "AppendStopsWhenFull"
    append_limit: 1000

# Clean metric naming
metric_mappings:
  "Temp CPU0_Temperature": "CPU_CoreTemperature"
  "Temp Inlet_Temperature": "ChassisInletTemperature"
  "Fan 1A_FanSpeed": "SystemFan_1A_RPM"
  "Fan PSU 1_FanSpeed": "PSU_Fan_RPM"

# Map to modern Redfish URIs
metric_properties_mappings:
  "CPU_CoreTemperature":
    - "/redfish/v1/Systems/1/Processors/CPU0/Metrics#TemperatureCelsius"
  "ChassisInletTemperature":
    - "/redfish/v1/Chassis/1/ThermalSubsystem/Sensors/InletTemp#ReadingCelsius"
  "SystemFan_1A_RPM":
    - "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/1A#SpeedRPM"
```

### Example: Performance Monitoring Configuration

```yaml
# Optimized for performance monitoring
report_actions: ["RedfishEvent"]
report_updates: "Overwrite"
recurrence_interval: "PT10S"  # High frequency

metric_type_configs:
  ProcessorMetrics:
    recurrence_interval: "PT5S"   # Very fast for CPU
  MemoryMetrics:
    recurrence_interval: "PT10S"
  EnvironmentMetrics:
    recurrence_interval: "PT60S"  # Slower for environment

# Performance-focused naming
metric_mappings:
  "CPU*_Utilization": "Processor_{source_id}_Usage"
  "Memory*_Bandwidth": "Memory_{source_id}_BandwidthPercent"

metric_properties_mappings:
  "Processor_CPU0_Usage":
    - "/redfish/v1/Systems/1/Processors/CPU0/Metrics#AverageFrequency"
    - "/redfish/v1/Systems/1/Processors/CPU0/Metrics#ConsumedPowerWatt"
    - "/redfish/v1/Systems/1/Processors/CPU0/Metrics#CorrectableCoreErrorCount"
```

## Testing Configuration

Test your configuration before deployment:

```bash
# Test analysis with new config
python mrd_tool.py analyze -m /path/to/mockup.tgz -c my_config.yaml

# Generate test MRDs
python mrd_tool.py generate -m /path/to/mockup.tgz -c my_config.yaml -o test_output

# Validate generated MRDs
python mrd_tool.py validate -f test_output/environmentmetrics_mrd.json
```

## Advanced Features

### Pattern-Based Metric Mapping

Use wildcards for systematic renaming:

```yaml
metric_mappings:
  # Pattern matching
  "Temp DIMM *_Temperature": "Memory_{source_id}_Temperature"
  "Fan *_FanSpeed": "CoolingFan_{source_id}_RPM"
  "PWM *_FanSpeed": "PWMFan_{source_id}_Duty"
  
  # Variables: {source_id}, {metric_name}
  "*_Utilization": "{source_id}_UsagePercent"
```

### Multiple Property Mappings

Map one MetricId to multiple Redfish properties:

```yaml
metric_properties_mappings:
  "Processor_Performance":
    - "/redfish/v1/Systems/1/Processors/CPU0/Metrics#AverageFrequency"
    - "/redfish/v1/Systems/1/Processors/CPU0/Metrics#ConsumedPowerWatt"
    - "/redfish/v1/Systems/1/Processors/CPU0/Metrics#ThrottlingCause"
    
  "Memory_Health":
    - "/redfish/v1/Systems/1/Memory/DIMM0/Metrics#CorrectableErrorCount"
    - "/redfish/v1/Systems/1/Memory/DIMM0/Metrics#UncorrectableErrorCount"
    - "/redfish/v1/Systems/1/Memory/DIMM0#Status/Health"
```

### Per-Metric-Type Customization

Override global settings per metric type:

```yaml
# Global defaults
report_actions: ["LogToMetricReportsCollection"]
recurrence_interval: "PT60S"

# Per-type overrides
metric_type_configs:
  EnvironmentMetrics:
    report_actions: ["RedfishEvent"]  # Events for temp alerts
    recurrence_interval: "PT30S"
    
  AlarmsMetrics:
    report_actions: ["RedfishEvent", "LogToMetricReportsCollection"]
    report_updates: "AppendStopsWhenFull"
    append_limit: 500
    
  ProcessorMetrics:
    recurrence_interval: "PT5S"  # High frequency
```