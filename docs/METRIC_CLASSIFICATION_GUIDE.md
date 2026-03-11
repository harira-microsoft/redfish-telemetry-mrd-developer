# BMC Metric Report Definition Classification Guide

This document provides a comprehensive overview of how metrics are classified into different categories in the Redfish Telemetry MRD Developer, along with examples and fine-tuning guidance.

## Overview

The Redfish Telemetry MRD Developer classifies Redfish metrics into six main categories based on a multi-layered classification system that considers resource types, sensor types, keywords, and data properties.

## Classification Categories

### 1. PlatformMetrics

**Purpose**: System-level health, status, and operational metrics

**Resource Types**:
- `system` - ComputerSystem resources
- `chassis` - Chassis resources  
- `manager` - Manager/BMC resources

**Keywords Matched**:
- platform, system, board, motherboard, chassis
- uptime, boot, reset, power_state, health

**Key Properties**:
- `PowerState` - System power status
- `BootProgress` - Boot progression state
- `SystemType` - Type of computer system
- `ProcessorSummary` - Overall processor information
- `MemorySummary` - Overall memory information
- `Status` - Health and state information
- `PowerRestorePolicy` - Power restoration behavior
- `HostName` - System hostname
- `UUID` - System unique identifier

**Example Metrics**:
```json
{
  "MetricId": "System_PowerState",
  "MetricProperties": ["/redfish/v1/Systems/1#PowerState"],
  "DataType": "String"
},
{
  "MetricId": "System_SystemHealth", 
  "MetricProperties": ["/redfish/v1/Systems/1#Status.Health"],
  "DataType": "String"
},
{
  "MetricId": "System_BootProgress",
  "MetricProperties": ["/redfish/v1/Systems/1#BootProgress.LastState"],
  "DataType": "String"
}
```

**Use Cases**:
- System boot monitoring
- Platform health tracking
- Power state management
- Overall system status reporting

---

### 2. EnvironmentMetrics

**Purpose**: Environmental conditions and thermal management

**Resource Types**:
- `temperature` - Temperature sensors
- `fan` - Fan controllers and sensors
- `sensor` - Generic environmental sensors
- `power_supply` - Power supply units

**Sensor Types**:
- `Temperature` - Temperature readings
- `Fan` - Fan speed measurements
- `Humidity` - Humidity sensors
- `Pressure` - Pressure sensors
- `Voltage` - Voltage measurements
- `Current` - Current measurements

**Keywords Matched**:
- temperature, thermal, fan, cooling, ambient
- inlet, outlet, airflow, humidity, pressure
- voltage, current

**Key Properties**:
- `ReadingCelsius` - Temperature in Celsius
- `UpperThresholdCritical` - Critical high threshold
- `LowerThresholdCritical` - Critical low threshold
- `UpperThresholdNonCritical` - Warning high threshold
- `LowerThresholdNonCritical` - Warning low threshold
- `Reading` - Generic sensor reading
- `SpeedRPM` - Fan speed in RPM
- `SpeedPercent` - Fan speed percentage
- `ReadingVolts` - Voltage reading
- `ReadingAmperes` - Current reading

**Example Metrics**:
```json
{
  "MetricId": "CPU_Inlet_Temperature",
  "MetricProperties": ["/redfish/v1/Chassis/1/Thermal#/Temperatures/CPU_Inlet#ReadingCelsius"],
  "DataType": "Number",
  "Units": "Cel",
  "Thresholds": {
    "UpperCritical": {"Reading": 85.0, "Activation": "Increasing"}
  }
},
{
  "MetricId": "Fan1_Speed",
  "MetricProperties": ["/redfish/v1/Chassis/1/Thermal#/Fans/Fan1#Reading"],
  "DataType": "Number", 
  "Units": "RPM"
}
```

**Use Cases**:
- Thermal monitoring and alerting
- Fan speed control
- Environmental condition tracking
- Power consumption monitoring
- Data center environmental management

---

### 3. ProcessorMetrics

**Purpose**: CPU and processor performance metrics

**Resource Types**:
- `processor` - Processor resources

**Sensor Types**:
- `Frequency` - Clock frequency measurements
- `Utilization` - CPU utilization percentages
- `Power` - Processor power consumption

**Keywords Matched**:
- cpu, processor, core, thread, frequency
- utilization, cache, instruction, performance
- turbo, throttle

**Key Properties**:
- `MaxSpeedMHz` - Maximum processor speed
- `TotalCores` - Number of processor cores
- `TotalThreads` - Number of execution threads
- `ProcessorType` - Type of processor
- `InstructionSet` - Supported instruction set
- `Manufacturer` - Processor manufacturer
- `Model` - Processor model
- `Utilization` - Current utilization
- `CurrentSpeedMHz` - Current operating speed
- `ProcessorArchitecture` - Processor architecture

**Example Metrics**:
```json
{
  "MetricId": "CPU1_MaxSpeed",
  "MetricProperties": ["/redfish/v1/Systems/1/Processors/CPU1#MaxSpeedMHz"],
  "DataType": "Number",
  "Units": "MHz"
},
{
  "MetricId": "CPU1_Cores",
  "MetricProperties": ["/redfish/v1/Systems/1/Processors/CPU1#TotalCores"],
  "DataType": "Number"
},
{
  "MetricId": "CPU1_Utilization",
  "MetricProperties": ["/redfish/v1/Systems/1/Processors/CPU1#Utilization"],
  "DataType": "Number",
  "Units": "Percent"
}
```

**Use Cases**:
- Performance monitoring
- Capacity planning
- Workload optimization
- Thermal management correlation

---

### 4. MemoryMetrics

**Purpose**: Memory subsystem performance and health metrics

**Resource Types**:
- `memory` - Memory modules (DIMMs)

**Sensor Types**:
- `Utilization` - Memory utilization
- `BandwidthPercent` - Memory bandwidth usage
- `Power` - Memory power consumption

**Keywords Matched**:
- memory, ram, dimm, dram, capacity
- bandwidth, ecc, error, correctable, uncorrectable

**Key Properties**:
- `CapacityMiB` - Memory capacity in MiB
- `OperatingSpeedMhz` - Operating frequency
- `MemoryType` - Type of memory (DDR4, DDR5, etc.)
- `DataWidthBits` - Data bus width
- `ErrorCorrection` - ECC capabilities
- `RankCount` - Number of ranks
- `MemoryMedia` - Memory media type
- `MemoryDeviceType` - Device type
- `AllowedSpeedsMHz` - Supported speeds

**Example Metrics**:
```json
{
  "MetricId": "DIMM1_Capacity",
  "MetricProperties": ["/redfish/v1/Systems/1/Memory/DIMM1#CapacityMiB"],
  "DataType": "Number",
  "Units": "MiBy"
},
{
  "MetricId": "DIMM1_Speed",
  "MetricProperties": ["/redfish/v1/Systems/1/Memory/DIMM1#OperatingSpeedMhz"],
  "DataType": "Number",
  "Units": "MHz"
},
{
  "MetricId": "DIMM1_Utilization",
  "MetricProperties": ["/redfish/v1/Systems/1/Memory/DIMM1#Utilization"],
  "DataType": "Number",
  "Units": "Percent"
}
```

**Use Cases**:
- Memory capacity planning
- Performance optimization
- Error tracking and reliability
- Power management

---

### 5. AlarmsMetrics

**Purpose**: Fault detection, alerting, and health status metrics

**Resource Types**:
- `log_entry` - Event log entries
- `event` - Event notifications
- `alarm` - Alarm resources

**Sensor Types**:
- `Alarm` - Alarm sensors
- `Fault` - Fault indicators

**Keywords Matched**:
- alarm, alert, fault, error, critical
- warning, emergency, notification, event
- log, failure

**Key Properties**:
- `Health` - Component health status
- `State` - Operational state
- `HealthRollup` - Aggregated health status
- `Severity` - Event severity level
- `MessageId` - Standard message identifier
- `AlarmType` - Type of alarm
- `AlarmStatus` - Current alarm status
- `EventType` - Type of event
- `EventId` - Event identifier

**Example Metrics**:
```json
{
  "MetricId": "System_HealthAlarm",
  "MetricProperties": ["/redfish/v1/Systems/1#Status.Health"],
  "DataType": "String"
},
{
  "MetricId": "ThermalAlarm_Status",
  "MetricProperties": ["/redfish/v1/Chassis/1/Thermal#Status.Health"],
  "DataType": "String"
}
```

**Use Cases**:
- Proactive fault detection
- Health monitoring dashboards
- Alert generation and escalation
- Predictive maintenance

---

### 6. StatusAndCounterMetrics

**Purpose**: Network performance, packet statistics, and operational counters

**Resource Types**:
- `network_interface` - Network interfaces
- `port` - Physical/logical ports
- `ethernet_interface` - Ethernet interfaces

**Sensor Types**:
- `Counter` - Cumulative counters
- `Rate` - Rate measurements
- `Percent` - Percentage values

**Keywords Matched**:
- counter, count, rate, packets, bytes
- errors, drops, statistics, performance
- throughput, bandwidth, latency

**Key Properties**:
- `PacketsReceived` - Received packet count
- `PacketsSent` - Transmitted packet count
- `BytesReceived` - Received byte count
- `BytesSent` - Transmitted byte count
- `ErrorsReceived` - Receive error count
- `ErrorsSent` - Transmit error count
- `DroppedPackets` - Dropped packet count
- `Collisions` - Collision count
- `LinkStatus` - Link operational status
- `SpeedMbps` - Interface speed
- `FullDuplex` - Duplex mode

**Example Metrics**:
```json
{
  "MetricId": "Eth0_PacketsReceived",
  "MetricProperties": ["/redfish/v1/Systems/1/EthernetInterfaces/Eth0#PacketsReceived"],
  "DataType": "Number"
},
{
  "MetricId": "Eth0_BytesSent", 
  "MetricProperties": ["/redfish/v1/Systems/1/EthernetInterfaces/Eth0#BytesSent"],
  "DataType": "Number"
},
{
  "MetricId": "Eth0_LinkSpeed",
  "MetricProperties": ["/redfish/v1/Systems/1/EthernetInterfaces/Eth0#SpeedMbps"],
  "DataType": "Number",
  "Units": "Mbps"
}
```

**Use Cases**:
- Network performance monitoring
- Traffic analysis
- Error rate tracking
- Bandwidth utilization

---

## Classification Decision Matrix

| Input | Resource Type | Sensor Type | Keywords | Properties | Result |
|-------|---------------|-------------|----------|------------|---------|
| ComputerSystem | system | - | - | PowerState | PlatformMetrics |
| Temperature Sensor | sensor | Temperature | temperature | ReadingCelsius | EnvironmentMetrics |
| CPU Temp Sensor | sensor | Temperature | cpu, temperature | ReadingCelsius | EnvironmentMetrics + ProcessorMetrics |
| Processor | processor | - | cpu | MaxSpeedMHz | ProcessorMetrics + PlatformMetrics |
| Memory DIMM | memory | - | memory | CapacityMiB | MemoryMetrics + PlatformMetrics |
| Health Status | - | - | health | Status.Health | PlatformMetrics + AlarmsMetrics |
| Network Interface | network_interface | - | - | PacketsReceived | StatusAndCounterMetrics |

## Multi-Classification Examples

Some metrics can belong to multiple categories based on their purpose:

### CPU Temperature Sensor
- **EnvironmentMetrics**: Temperature monitoring for thermal management
- **ProcessorMetrics**: CPU-specific thermal monitoring
- **PlatformMetrics**: Overall system health indicator

### Memory Module with Health Status  
- **MemoryMetrics**: Memory-specific capacity and performance
- **PlatformMetrics**: System health component

### Power Supply Current Sensor
- **EnvironmentMetrics**: Environmental power monitoring  
- **PlatformMetrics**: Platform health indicator

## Customization and Fine-Tuning

### Modifying Classification Rules

Edit `/config/metric_mappings.yaml` to customize:

```yaml
# Add new keywords
EnvironmentMetrics:
  keywords:
    - temperature
    - thermal
    - custom_env_keyword  # Add custom keyword

# Add new properties  
ProcessorMetrics:
  properties:
    - MaxSpeedMHz
    - CustomProcessorProperty  # Add custom property

# Add new sensor types
MemoryMetrics:
  sensor_types:
    - Utilization
    - CustomMemorySensorType  # Add custom sensor type
```

### Priority Override

The classification follows this priority:
1. **Resource Type** (highest priority)
2. **Sensor Type** 
3. **Keyword Match**
4. **Property Match** (lowest priority)

### Adding New Metric Types

1. Define new enum in `src/metric_classifier.py`:
```python
class MetricType(Enum):
    CUSTOM_METRICS = "CustomMetrics"
```

2. Add mapping configuration:
```yaml
CustomMetrics:
  keywords:
    - custom
    - special
  properties:
    - CustomProperty
  resource_types:
    - custom_resource
```

3. Add extraction logic in `_extract_custom_metrics()` method.

## Validation and Testing

Use the analysis command to validate classifications:

```bash
# Analyze mockup classifications
python mrd_tool.py analyze --mockup-path ./mockups/your_mockup.tgz

# Generate with specific types to test
python mrd_tool.py generate --mockup-path ./mockups/your_mockup.tgz \
  --metric-types PlatformMetrics,EnvironmentMetrics

# Validate generated MRDs
python mrd_tool.py validate --mrd-file ./output/platformmetrics_mrd.json
```

## Best Practices

1. **Start with Resource Types**: Most reliable classification method
2. **Use Semantic Keywords**: Add domain-specific terms for your environment
3. **Leverage Properties**: Most flexible for custom implementations
4. **Test Classifications**: Always validate with real mockup data
5. **Document Changes**: Keep track of custom modifications
6. **Multi-Classification**: Embrace metrics serving multiple purposes

This classification system provides a robust foundation for organizing Redfish metrics while allowing extensive customization for specific BMC implementations and use cases.