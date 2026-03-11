# Copyright (c) 2026 Hari Ramachandran
# SPDX-License-Identifier: Apache-2.0
# See the LICENSE file in the project root for details.

"""
Metric classifier for categorizing Redfish metrics into different types.
"""

from enum import Enum
from typing import Dict, List, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Enumeration of supported metric types."""
    PLATFORM_METRICS = "PlatformMetrics"
    ENVIRONMENT_METRICS = "EnvironmentMetrics"
    PROCESSOR_METRICS = "ProcessorMetrics"
    MEMORY_METRICS = "MemoryMetrics"
    ALARMS_METRICS = "AlarmsMetrics"
    STATUS_AND_COUNTER_METRICS = "StatusAndCounterMetrics"


class MetricClassifier:
    """Classifies metrics based on their properties and source."""
    
    def __init__(self, mappings_config: Optional[Dict] = None):
        """Initialize with optional custom mappings configuration."""
        if mappings_config:
            # Filter config to only include metric type classifications
            # Valid keys are the MetricType enum values
            valid_keys = {mt.value for mt in MetricType}
            filtered_mappings = {k: v for k, v in mappings_config.items() 
                               if k in valid_keys}
            # Merge with defaults, giving precedence to custom config
            default_mappings = self._get_default_mappings()
            default_mappings.update(filtered_mappings)
            self.mappings = default_mappings
        else:
            self.mappings = self._get_default_mappings()
        
    def _get_default_mappings(self) -> Dict:
        """Get default metric classification mappings."""
        return {
            MetricType.PLATFORM_METRICS.value: {
                "keywords": [
                    "platform", "system", "board", "motherboard", "chassis",
                    "uptime", "boot", "reset", "power_state", "health"
                ],
                "properties": [
                    "PowerState", "BootProgress", "SystemType", "ProcessorSummary",
                    "MemorySummary", "Status", "PowerRestorePolicy"
                ],
                "resource_types": ["system", "chassis", "manager"]
            },
            MetricType.ENVIRONMENT_METRICS.value: {
                "keywords": [
                    "temperature", "thermal", "fan", "cooling", "ambient",
                    "inlet", "outlet", "airflow", "humidity", "pressure"
                ],
                "properties": [
                    "ReadingCelsius", "UpperThresholdCritical", "LowerThresholdCritical",
                    "Reading", "SpeedRPM", "SpeedPercent"
                ],
                "resource_types": ["temperature", "fan", "sensor"],
                "sensor_types": ["Temperature", "Fan", "Humidity", "Pressure"]
            },
            MetricType.PROCESSOR_METRICS.value: {
                "keywords": [
                    "cpu", "processor", "core", "thread", "frequency", "utilization",
                    "cache", "instruction", "performance", "turbo", "throttle"
                ],
                "properties": [
                    "MaxSpeedMHz", "TotalCores", "TotalThreads", "ProcessorType",
                    "InstructionSet", "Manufacturer", "Model", "Utilization"
                ],
                "resource_types": ["processor"],
                "sensor_types": ["Frequency", "Utilization"]
            },
            MetricType.MEMORY_METRICS.value: {
                "keywords": [
                    "memory", "ram", "dimm", "dram", "capacity", "bandwidth",
                    "ecc", "error", "correctable", "uncorrectable"
                ],
                "properties": [
                    "CapacityMiB", "OperatingSpeedMhz", "MemoryType", "DataWidthBits",
                    "ErrorCorrection", "RankCount", "MemoryMedia"
                ],
                "resource_types": ["memory"],
                "sensor_types": ["Utilization", "BandwidthPercent"]
            },
            MetricType.ALARMS_METRICS.value: {
                "keywords": [
                    "alarm", "alert", "fault", "error", "critical", "warning",
                    "emergency", "notification", "event", "log"
                ],
                "properties": [
                    "Health", "State", "HealthRollup", "Severity", "MessageId",
                    "AlarmType", "AlarmStatus"
                ],
                "resource_types": ["log_entry", "event"],
                "sensor_types": ["Alarm"]
            },
            MetricType.STATUS_AND_COUNTER_METRICS.value: {
                "keywords": [
                    "counter", "count", "rate", "packets", "bytes", "errors",
                    "drops", "statistics", "performance", "throughput"
                ],
                "properties": [
                    "PacketsReceived", "PacketsSent", "BytesReceived", "BytesSent",
                    "ErrorsReceived", "ErrorsSent", "DroppedPackets", "Collisions"
                ],
                "resource_types": ["network_interface", "port"],
                "sensor_types": ["Counter", "Rate"]
            }
        }
    
    def classify_metric_source(self, source: Dict[str, Any]) -> List[MetricType]:
        """Classify a metric source and return applicable metric types."""
        classifications = []
        source_type = source.get('type', '').lower()
        source_data = source.get('data', {})
        source_name = source.get('name', '').lower()
        
        logger.debug(f"Classifying source: {source_type} - {source_name}")
        
        for metric_type_str, config in self.mappings.items():
            metric_type = MetricType(metric_type_str)
            
            if self._matches_classification(source_type, source_data, source_name, config):
                classifications.append(metric_type)
                logger.debug(f"Source matches {metric_type.value}")
        
        return classifications
    
    def _matches_classification(self, source_type: str, source_data: Dict, 
                              source_name: str, config: Dict) -> bool:
        """Check if a source matches a classification configuration."""
        
        # Check resource types
        if 'resource_types' in config:
            if source_type in config['resource_types']:
                return True
        
        # Check sensor types for sensor resources
        if source_type == 'sensor' and 'sensor_types' in config:
            sensor_type = source_data.get('ReadingType', '')
            if sensor_type in config['sensor_types']:
                return True
        
        # Check keywords in name
        if 'keywords' in config:
            for keyword in config['keywords']:
                if keyword.lower() in source_name:
                    return True
        
        # Check for specific properties in the data
        if 'properties' in config:
            for prop in config['properties']:
                if self._has_property(source_data, prop):
                    return True
        
        return False
    
    def _has_property(self, data: Dict, property_path: str) -> bool:
        """Check if data has a specific property (supports nested paths with dots)."""
        keys = property_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return False
        
        return True
    
    def extract_metrics_by_type(self, metric_sources: List[Dict], 
                               metric_type: MetricType) -> List[Dict]:
        """Extract metrics of a specific type from metric sources."""
        matching_metrics = []
        
        for source in metric_sources:
            classifications = self.classify_metric_source(source)
            
            if metric_type in classifications:
                metrics = self._extract_metrics_from_source(source, metric_type)
                matching_metrics.extend(metrics)
        
        return matching_metrics
    
    def _extract_metrics_from_source(self, source: Dict, 
                                   metric_type: MetricType) -> List[Dict]:
        """Extract specific metrics from a source based on metric type."""
        metrics = []
        source_data = source.get('data', {})
        source_type = source.get('type', '')
        
        base_metric = {
            'source_id': source.get('id', ''),
            'source_name': source.get('name', ''),
            'source_type': source_type,
            'metric_type': metric_type.value
        }
        
        if metric_type == MetricType.PLATFORM_METRICS:
            metrics.extend(self._extract_platform_metrics(source_data, base_metric))
        elif metric_type == MetricType.ENVIRONMENT_METRICS:
            metrics.extend(self._extract_environment_metrics(source_data, base_metric))
        elif metric_type == MetricType.PROCESSOR_METRICS:
            metrics.extend(self._extract_processor_metrics(source_data, base_metric))
        elif metric_type == MetricType.MEMORY_METRICS:
            metrics.extend(self._extract_memory_metrics(source_data, base_metric))
        elif metric_type == MetricType.ALARMS_METRICS:
            metrics.extend(self._extract_alarms_metrics(source_data, base_metric))
        elif metric_type == MetricType.STATUS_AND_COUNTER_METRICS:
            metrics.extend(self._extract_status_counter_metrics(source_data, base_metric))
        
        return metrics
    
    def _extract_platform_metrics(self, data: Dict, base: Dict) -> List[Dict]:
        """Extract platform-specific metrics."""
        metrics = []
        
        # System power state
        if 'PowerState' in data:
            metrics.append({
                **base,
                'metric_name': 'PowerState',
                'metric_property': 'PowerState',
                'data_type': 'String',
                'current_value': data['PowerState']
            })
        
        # System health
        if 'Status' in data and 'Health' in data['Status']:
            metrics.append({
                **base,
                'metric_name': 'SystemHealth',
                'metric_property': 'Status.Health',
                'data_type': 'String',
                'current_value': data['Status']['Health']
            })
        
        # Boot progress
        if 'BootProgress' in data and 'LastState' in data['BootProgress']:
            metrics.append({
                **base,
                'metric_name': 'BootProgress',
                'metric_property': 'BootProgress.LastState',
                'data_type': 'String',
                'current_value': data['BootProgress']['LastState']
            })
        
        return metrics
    
    def _extract_environment_metrics(self, data: Dict, base: Dict) -> List[Dict]:
        """Extract environment-specific metrics."""
        metrics = []
        
        # Temperature reading
        if 'ReadingCelsius' in data:
            metrics.append({
                **base,
                'metric_name': 'Temperature',
                'metric_property': 'ReadingCelsius',
                'data_type': 'Number',
                'units': 'Cel',
                'current_value': data['ReadingCelsius']
            })
        
        # Fan speed
        if 'Reading' in data and base['source_type'] == 'fan':
            metrics.append({
                **base,
                'metric_name': 'FanSpeed',
                'metric_property': 'Reading',
                'data_type': 'Number',
                'units': 'RPM',
                'current_value': data['Reading']
            })
        
        return metrics
    
    def _extract_processor_metrics(self, data: Dict, base: Dict) -> List[Dict]:
        """Extract processor-specific metrics."""
        metrics = []
        
        # Max speed
        if 'MaxSpeedMHz' in data:
            metrics.append({
                **base,
                'metric_name': 'ProcessorMaxSpeed',
                'metric_property': 'MaxSpeedMHz',
                'data_type': 'Number',
                'units': 'MHz',
                'current_value': data['MaxSpeedMHz']
            })
        
        # Total cores
        if 'TotalCores' in data:
            metrics.append({
                **base,
                'metric_name': 'ProcessorCores',
                'metric_property': 'TotalCores',
                'data_type': 'Number',
                'current_value': data['TotalCores']
            })
        
        # Total threads
        if 'TotalThreads' in data:
            metrics.append({
                **base,
                'metric_name': 'ProcessorThreads',
                'metric_property': 'TotalThreads',
                'data_type': 'Number',
                'current_value': data['TotalThreads']
            })
        
        return metrics
    
    def _extract_memory_metrics(self, data: Dict, base: Dict) -> List[Dict]:
        """Extract memory-specific metrics."""
        metrics = []
        
        # Memory capacity
        if 'CapacityMiB' in data:
            metrics.append({
                **base,
                'metric_name': 'MemoryCapacity',
                'metric_property': 'CapacityMiB',
                'data_type': 'Number',
                'units': 'MiBy',
                'current_value': data['CapacityMiB']
            })
        
        # Operating speed
        if 'OperatingSpeedMhz' in data:
            metrics.append({
                **base,
                'metric_name': 'MemorySpeed',
                'metric_property': 'OperatingSpeedMhz',
                'data_type': 'Number',
                'units': 'MHz',
                'current_value': data['OperatingSpeedMhz']
            })
        
        return metrics
    
    def _extract_alarms_metrics(self, data: Dict, base: Dict) -> List[Dict]:
        """Extract alarm-specific metrics."""
        metrics = []
        
        # Health status (can indicate alarms)
        if 'Status' in data:
            status = data['Status']
            if 'Health' in status and status['Health'] in ['Warning', 'Critical']:
                metrics.append({
                    **base,
                    'metric_name': 'HealthAlarm',
                    'metric_property': 'Status.Health',
                    'data_type': 'String',
                    'current_value': status['Health']
                })
        
        return metrics
    
    def _extract_status_counter_metrics(self, data: Dict, base: Dict) -> List[Dict]:
        """Extract status and counter-specific metrics."""
        metrics = []
        
        # Look for counter-like properties
        counter_properties = [
            'PacketsReceived', 'PacketsSent', 'BytesReceived', 'BytesSent',
            'ErrorsReceived', 'ErrorsSent', 'DroppedPackets'
        ]
        
        for prop in counter_properties:
            if prop in data:
                metrics.append({
                    **base,
                    'metric_name': prop,
                    'metric_property': prop,
                    'data_type': 'Number',
                    'current_value': data[prop]
                })
        
        return metrics