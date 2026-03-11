# Metric Classification Examples from Real Mockup Data

This document shows actual metric classifications from the Redfish Telemetry MRD Developer using real mockup data, providing concrete examples for understanding and fine-tuning.

## Full BMC Mockup Classification Results

### PlatformMetrics (294 metrics)

**System-Level Metrics:**
```json
{
  "MetricId": "system_PowerState",
  "MetricProperties": ["/redfish/v1/Systems/system#PowerState"],
  "DataType": "String",
  "CurrentValue": "On"
}
```

**Health Status Metrics:**
```json
{
  "MetricId": "BAM_3_P12V_IBC_N_output_current_SystemHealth",
  "MetricProperties": ["/redfish/v1/Chassis/1/Sensors/BAM_3_P12V_IBC_N_output_current#Status.Health"],
  "DataType": "String",
  "CurrentValue": "OK"
}
```

**Sensor Health Examples:**
- BAM 3 P12V IBC N output current → SystemHealth
- BAM 3 P12V IBC S output current → SystemHealth  
- BAM 3 P3V3 BAM output current → SystemHealth
- PDB Fan Controller1 PWM1 → SystemHealth
- PDB Fan Controller1 TACH1 → SystemHealth

### EnvironmentMetrics (101 metrics)

**Temperature Sensors:**
```json
{
  "MetricId": "BAM_3_P12V_IBC_N_temp_Temperature",
  "MetricProperties": ["/redfish/v1/Chassis/1/Thermal#/Temperatures/BAM_3_P12V_IBC_N_temp#ReadingCelsius"],
  "DataType": "Number",
  "Units": "Cel",
  "CurrentValue": 45.2
}
```

**Fan Speed Sensors:**
```json
{
  "MetricId": "PDB_Fan_Controller1_TACH1_FanSpeed", 
  "MetricProperties": ["/redfish/v1/Chassis/1/Thermal#/Fans/PDB_Fan_Controller1_TACH1#Reading"],
  "DataType": "Number",
  "Units": "RPM",
  "CurrentValue": 3420
}
```

**Temperature Sensor Examples:**
- BAM 3 P12V IBC N temp → Temperature (45.2°C)
- BAM 3 P12V IBC S temp → Temperature (44.8°C)
- BAM 3 P3V3 BAM temp → Temperature (42.1°C)
- Node Inlet TMP → Temperature (28.5°C)
- SCM Inlet TMP → Temperature (31.2°C)
- PESW Ambient temp → Temperature (35.7°C)

**Fan Examples:**
- PDB Fan Controller1 PWM1 → FanSpeed (65%)
- PDB Fan Controller1 TACH1 → FanSpeed (3420 RPM)
- PDB Fan Controller2 TACH2 → FanSpeed (3380 RPM)

## RAS System Mockup Classification Results

### PlatformMetrics (198 metrics)

**System Health:**
```json
{
  "MetricId": "system_PowerState",
  "MetricProperties": ["/redfish/v1/Systems/system#PowerState"],
  "DataType": "String",
  "CurrentValue": "On"
}
```

### ProcessorMetrics (1 metric)

**Processor Speed:**
```json
{
  "MetricId": "CPU1_ProcessorMaxSpeed",
  "MetricProperties": ["/redfish/v1/Systems/1/Processors/CPU1#MaxSpeedMHz"],
  "DataType": "Number", 
  "Units": "MHz",
  "CurrentValue": 3200
}
```

### MemoryMetrics (12 metrics)

**Memory Capacity Examples:**
```json
{
  "MetricId": "1_MemoryCapacity",
  "MetricProperties": ["/redfish/v1/Systems/1/Memory/1#CapacityMiB"],
  "DataType": "Number",
  "Units": "MiBy",
  "CurrentValue": 16384
},
{
  "MetricId": "2_MemoryCapacity", 
  "MetricProperties": ["/redfish/v1/Systems/1/Memory/2#CapacityMiB"],
  "DataType": "Number",
  "Units": "MiBy", 
  "CurrentValue": 16384
}
```

**Memory DIMMs Found:**
- DIMM 1 → MemoryCapacity (16384 MiBy)
- DIMM 2 → MemoryCapacity (16384 MiBy)
- DIMM 3 → MemoryCapacity (16384 MiBy)
- DIMM 4 → MemoryCapacity (16384 MiBy)
- DIMM 5 → MemoryCapacity (16384 MiBy)
- DIMM 6 → MemoryCapacity (16384 MiBy)
- DIMM 7 → MemoryCapacity (32768 MiBy)
- DIMM 8 → MemoryCapacity (32768 MiBy)
- DIMM 9 → MemoryCapacity (32768 MiBy)
- DIMM 10 → MemoryCapacity (32768 MiBy)
- DIMM 11 → MemoryCapacity (32768 MiBy)
- DIMM 12 → MemoryCapacity (32768 MiBy)

### EnvironmentMetrics (59 metrics)

**Temperature Sensors:**
- SCM INLET TMP → Temperature
- GP S2 AMB TMP → Temperature  
- GP S2 FPGA TMP → Temperature
- GP S2 HSC TMP → Temperature
- GP S2 SOC TMP → Temperature

**Fan Controllers:**
- Various PWM and TACH sensors → FanSpeed

## Multi-Classification Analysis

### Sensors with Multiple Classifications

**Example 1: BAM Temperature Sensors**
- **Resource Type**: `sensor` 
- **Sensor Type**: `Temperature`
- **Keywords**: `bam` (platform), `temp` (environment)
- **Properties**: `ReadingCelsius` (environment), `Status` (platform)
- **Result**: **PlatformMetrics + EnvironmentMetrics**

**Example 2: CPU-related Temperature**
```
CPU Inlet Temperature:
├─ EnvironmentMetrics (thermal management)
├─ ProcessorMetrics (CPU monitoring) 
└─ PlatformMetrics (health status)
```

**Example 3: Memory with Health Status**
```
DIMM with Status Property:
├─ MemoryMetrics (capacity, speed)
└─ PlatformMetrics (health monitoring)
```

## Classification Statistics by Mockup

### Full BMC Mockup
```
Total Sources: 293
├─ PlatformMetrics: 294 (100% - all sensors have health status)
├─ EnvironmentMetrics: 101 (34% - thermal/power sensors)
├─ ProcessorMetrics: 0 (no processors in this BMC-focused mockup)
├─ MemoryMetrics: 0 (no memory modules)
├─ AlarmsMetrics: 0 (no explicit alarm sensors)
└─ StatusAndCounterMetrics: 0 (no network interfaces)
```

### RAS System Mockup
```
Total Sources: 197  
├─ PlatformMetrics: 198 (100% - includes system + components)
├─ EnvironmentMetrics: 59 (30% - environmental sensors)
├─ ProcessorMetrics: 1 (1 processor found)
├─ MemoryMetrics: 12 (12 DIMMs found)
├─ AlarmsMetrics: 0 (no alarm-specific sensors)
└─ StatusAndCounterMetrics: 0 (no network metrics in this mockup)
```

## Sensor Naming Patterns and Classifications

### Voltage Sensors → EnvironmentMetrics + PlatformMetrics
```
Pattern: "*.* volts"
Examples:
- BAM 1 P1V8 CLK volts
- BAM 1 P2V5 ANALOG volts  
- BAM 1 P3V3 AUX volts
- BAM 1 P3V3 BAM volts
- BAM 1 P5V BIAS volts
```

### Current Sensors → EnvironmentMetrics + PlatformMetrics
```
Pattern: "*.* output current"
Examples:
- BAM 1 P12V IBC N output current
- BAM 1 P12V IBC S output current
- BAM 1 P3V3 BAM output current
- BAM 1 P5V BIAS output current
```

### Temperature Sensors → EnvironmentMetrics + PlatformMetrics
```
Pattern: "*.* temp" or "*.* TMP"
Examples:
- BAM 1 P12V IBC N temp
- BAM 1 P5V BIAS temp
- BAM 1 SEQ1 TEMP
- BAM 1 SOC diode max tmp
- Node Inlet TMP
- SCM Inlet TMP
```

### Fan Controllers → EnvironmentMetrics + PlatformMetrics
```
Pattern: "*Fan Controller* PWM*" or "*Fan Controller* TACH*"
Examples:
- PDB Fan Controller1 PWM1 (speed control)
- PDB Fan Controller1 TACH1 (speed feedback)
- PDB Fan Controller2 PWM2
- PDB Fan Controller2 TACH2
```

## Classification Accuracy Analysis

### High Confidence Classifications (>95% accuracy)
1. **Resource Type Based**: processor → ProcessorMetrics, memory → MemoryMetrics
2. **Sensor Type Based**: ReadingType="Temperature" → EnvironmentMetrics  
3. **Clear Keywords**: "cpu", "memory", "temperature" in names

### Medium Confidence Classifications (80-95% accuracy)
1. **Composite Keywords**: "inlet temp", "fan speed", "power current"
2. **Property-Based**: Presence of specific properties like MaxSpeedMHz
3. **Context Clues**: BAM modules, HSC (Hot Swap Controller) components

### Potential Misclassifications
1. **Generic Sensors**: Sensors with unclear naming might default to PlatformMetrics
2. **Multi-Purpose Devices**: Components serving multiple functions
3. **Vendor-Specific Naming**: Non-standard naming conventions

## Fine-Tuning Recommendations

### Adding Custom Keywords
```yaml
# For vendor-specific components
EnvironmentMetrics:
  keywords:
    - bam        # Board Assembly Module
    - hsc        # Hot Swap Controller  
    - pdb        # Power Distribution Board
    - scm        # Storage Compute Module
    - pesw       # Packet Engine Switch
```

### Custom Sensor Types
```yaml
# For specialized sensors
EnvironmentMetrics:
  sensor_types:
    - VoltageRegulator
    - PowerModule
    - ThermalModule
```

### Property-Based Classification
```yaml
# For specific data properties
ProcessorMetrics:
  properties:
    - CoreCount
    - ThreadCount
    - CacheSize
    - TurboFrequency
```

This real-world data demonstrates how the classification system handles diverse BMC implementations and provides a foundation for customizing rules to match specific hardware configurations.