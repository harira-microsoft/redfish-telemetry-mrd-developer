# Copyright (c) 2026 Hari Ramachandran
# SPDX-License-Identifier: Apache-2.0
# See the LICENSE file in the project root for details.

"""
Redfish Metric Report Definition (MRD) generator.

This module provides the MRDGenerator class for generating Redfish Metric Report Definitions
from classified metric data. It supports configuration overrides, custom metric mappings,
and validation against Redfish schema requirements. Metric objects are represented using
Python dataclasses for clarity and maintainability.
"""


import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from dataclasses import dataclass, asdict, field

from .metric_classifier import MetricType


logger = logging.getLogger(__name__)


class MRDGenerationError(Exception):
    """Exception raised for errors during MRD generation."""
    pass


class MRDValidationError(Exception):
    """Exception raised for errors during MRD validation."""
    pass


@dataclass
class MetricDefinition:
    MetricId: str
    MetricProperties: List[str]
    DataType: Optional[str] = None
    Units: Optional[str] = None
    Thresholds: Optional[Dict] = None


class MRDGenerator:
    """
    Generator for Redfish Metric Report Definitions.

    This class generates MRDs from classified metrics, supports configuration overrides,
    custom metric ID/property mappings, and provides validation and file output utilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MRD generator.

        Args:
            config: Configuration dictionary containing MRD settings and custom mappings.
        """
        self.base_uri = "/redfish/v1/TelemetryService/MetricReportDefinitions"
        self.config = config or {}
        
        # Default MRD properties (can be overridden by config)
        self.default_report_actions = ["RedfishEvent", "LogToMetricReportsCollection"]
        self.default_report_updates = "Overwrite"
        self.default_append_limit = 100
        self.default_heartbeat_interval = "PT0S"
        self.default_recurrence_interval = "PT60S"
        
        # Load custom mappings if provided
        self.custom_metric_mappings = self.config.get('metric_mappings', {})
        
    def generate_mrd(self, metrics: List[Dict], metric_type: MetricType,
                     report_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a Metric Report Definition for a specific metric type.

        Args:
            metrics: List of metric dicts to include in the MRD.
            metric_type: The MetricType enum value for this MRD.
            report_name: Optional custom report name/ID.
        Returns:
            MRD dictionary ready for JSON serialization.
        """
        
        if not metrics:
            logger.warning(f"No metrics provided for {metric_type.value}")
            raise MRDGenerationError(f"No metrics provided for {metric_type.value}")
        
        # Generate unique ID and name if not provided
        mrd_id = report_name or f"{metric_type.value}Report"
        
        # Get configurable properties (check metric-type specific config first)
        metric_type_config = self.config.get('metric_type_configs', {}).get(metric_type.value, {})
        
        report_actions = metric_type_config.get('report_actions', 
                        self.config.get('report_actions', self.default_report_actions))
        report_updates = metric_type_config.get('report_updates',
                        self.config.get('report_updates', self.default_report_updates))
        append_limit = metric_type_config.get('append_limit',
                      self.config.get('append_limit', self.default_append_limit))
        heartbeat_interval = metric_type_config.get('heartbeat_interval',
                            self.config.get('heartbeat_interval', self.default_heartbeat_interval))
        recurrence_interval = metric_type_config.get('recurrence_interval',
                             self.config.get('recurrence_interval', self.default_recurrence_interval))
        
        # Create the base MRD structure
        mrd = {
            "@odata.type": "#MetricReportDefinition.v1_3_0.MetricReportDefinition",
            "@odata.id": f"{self.base_uri}/{mrd_id}",
            "Id": mrd_id,
            "Name": f"{metric_type.value} Report Definition",
            "Description": f"Metric report definition for {metric_type.value.lower().replace('_', ' ')}",
            "MetricReport": {
                "@odata.id": f"/redfish/v1/TelemetryService/MetricReports/{mrd_id}"
            },
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            },
            "ReportActions": report_actions,
            "ReportUpdates": report_updates,
            "AppendLimit": append_limit,
            "MetricReportHeartbeatInterval": heartbeat_interval,
            "Wildcards": [],
            "Metrics": [],
            "ReportTimespan": "PT0S",  # Instantaneous
            "Schedule": {
                "RecurrenceInterval": recurrence_interval
            }
        }
        
        # Process metrics and add to definition
        processed_metrics = self._process_metrics_for_mrd(metrics, metric_type)
        mrd["Metrics"] = processed_metrics
        
        # Set appropriate collection function
        mrd["CollectionFunction"] = self._get_collection_function(metric_type)
        
        return mrd
    
    def _process_metrics_for_mrd(self, metrics: List[Dict], metric_type: MetricType) -> List[Dict]:
        """
        Process metrics for inclusion in MRD using MetricDefinition dataclass.

        Args:
            metrics: List of metric dicts.
            metric_type: The MetricType enum value.
        Returns:
            List of metric definition dicts for MRD inclusion.
        """
        processed: List[MetricDefinition] = []
        for metric in metrics:
            source_id = metric.get('source_id', '').replace(' ', '_')
            metric_name = metric.get('metric_name', '').replace(' ', '_')
            default_metric_id = f"{source_id}_{metric_name}"
            metric_id = self._get_custom_metric_id(metric, default_metric_id)
            metric_properties = self._get_custom_metric_properties(metric, metric_id)
            data_type = metric.get('data_type')
            units = metric.get('units')
            thresholds = None
            if metric_type == MetricType.ENVIRONMENT_METRICS:
                thresholds = self._get_environmental_thresholds(metric)
            processed.append(MetricDefinition(
                MetricId=metric_id,
                MetricProperties=metric_properties,
                DataType=data_type,
                Units=units,
                Thresholds=thresholds
            ))
        # Convert dataclass objects to dicts for JSON serialization
        return [asdict(m) for m in processed]
    
    def _build_metric_property_uri(self, metric: Dict) -> str:
        """
        Build the metric property URI based on source type.

        Args:
            metric: Metric dict containing source info.
        Returns:
            URI string for the metric property.
        """
        source_type = metric.get('source_type', '')
        source_id = metric.get('source_id', '').replace(' ', '_')
        metric_property = metric.get('metric_property', '')
        
        # Map source types to Redfish resource paths
        resource_mappings = {
            'system': f"/redfish/v1/Systems/{source_id}",
            'processor': f"/redfish/v1/Systems/1/Processors/{source_id}",
            'memory': f"/redfish/v1/Systems/1/Memory/{source_id}",
            'chassis': f"/redfish/v1/Chassis/{source_id}",
            'manager': f"/redfish/v1/Managers/{source_id}",
            'sensor': f"/redfish/v1/Chassis/1/Sensors/{source_id}",
            'temperature': f"/redfish/v1/Chassis/1/Thermal#/Temperatures/{source_id}",
            'fan': f"/redfish/v1/Chassis/1/Thermal#/Fans/{source_id}",
            'power_supply': f"/redfish/v1/Chassis/1/Power#/PowerSupplies/{source_id}"
        }
        
        base_uri = resource_mappings.get(source_type, f"/redfish/v1/{source_type}/{source_id}")
        
        # Append the metric property
        if metric_property:
            return f"{base_uri}#{metric_property}"
        else:
            return base_uri
    
    def _get_collection_function(self, metric_type: MetricType) -> str:
        """
        Get appropriate collection function for metric type.

        Args:
            metric_type: The MetricType enum value.
        Returns:
            String representing the collection function (e.g., 'Average').
        """
        function_mappings = {
            MetricType.PLATFORM_METRICS: "Average",
            MetricType.ENVIRONMENT_METRICS: "Average",
            MetricType.PROCESSOR_METRICS: "Average",
            MetricType.MEMORY_METRICS: "Average",
            MetricType.ALARMS_METRICS: "Summation",
            MetricType.STATUS_AND_COUNTER_METRICS: "Summation"
        }
        
        return function_mappings.get(metric_type, "Average")
    
    def _get_environmental_thresholds(self, metric: Dict) -> Optional[Dict]:
        """
        Get thresholds for environmental metrics.

        Args:
            metric: Metric dict containing source data.
        Returns:
            Dict of threshold values if present, else None.
        """
        source_data = metric.get('source_data', {})
        thresholds = {}
        
        # Temperature thresholds
        if 'UpperThresholdCritical' in source_data:
            thresholds["UpperCritical"] = {
                "Reading": source_data['UpperThresholdCritical'],
                "Activation": "Increasing"
            }
        
        if 'LowerThresholdCritical' in source_data:
            thresholds["LowerCritical"] = {
                "Reading": source_data['LowerThresholdCritical'],
                "Activation": "Decreasing"
            }
        
        if 'UpperThresholdNonCritical' in source_data:
            thresholds["UpperCaution"] = {
                "Reading": source_data['UpperThresholdNonCritical'],
                "Activation": "Increasing"
            }
        
        if 'LowerThresholdNonCritical' in source_data:
            thresholds["LowerCaution"] = {
                "Reading": source_data['LowerThresholdNonCritical'],
                "Activation": "Decreasing"
            }
        
        return thresholds if thresholds else None
    
    def _get_custom_metric_id(self, metric: Dict, default_id: str) -> str:
        """
        Get custom MetricId from mapping or use default.

        Args:
            metric: Metric dict.
            default_id: Default metric ID string.
        Returns:
            Custom metric ID if mapping exists, else default.
        """
        source_id = metric.get('source_id', '').replace(' ', '_')
        metric_name = metric.get('metric_name', '').replace(' ', '_')
        
        # Check if there's a custom mapping for this metric
        for mapping_key, custom_id in self.custom_metric_mappings.items():
            if mapping_key in [source_id, metric_name, f"{source_id}_{metric_name}"]:
                return custom_id
        
        # Check for pattern-based mappings
        for pattern, custom_id_template in self.custom_metric_mappings.items():
            if '*' in pattern:
                pattern_regex = pattern.replace('*', '.*')
                import re
                if re.match(pattern_regex, default_id):
                    # Replace placeholders in template
                    custom_id = custom_id_template.replace('{source_id}', source_id)
                    custom_id = custom_id.replace('{metric_name}', metric_name)
                    return custom_id
        
        return default_id
    
    def _get_custom_metric_properties(self, metric: Dict, metric_id: str) -> List[str]:
        """
        Get custom MetricProperties from mapping or use default.

        Args:
            metric: Metric dict.
            metric_id: Metric ID string.
        Returns:
            List of metric property URIs.
        """
        # Check if there's a custom property mapping for this MetricId
        properties_mappings = self.config.get('metric_properties_mappings', {})
        
        if metric_id in properties_mappings:
            custom_properties = properties_mappings[metric_id]
            if isinstance(custom_properties, str):
                return [custom_properties]
            elif isinstance(custom_properties, list):
                return custom_properties
        
        # Use default property URI
        return [self._build_metric_property_uri(metric)]
    
    def generate_all_mrds(self, classified_metrics: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """
        Generate MRDs for all metric types.

        Args:
            classified_metrics: Dict mapping metric type strings to lists of metric dicts.
        Returns:
            Dict mapping metric type strings to MRD dicts.
        """
        mrds = {}
        
        for metric_type_str, metrics in classified_metrics.items():
            if metrics:  # Only generate MRD if there are metrics
                try:
                    metric_type = MetricType(metric_type_str)
                    mrd = self.generate_mrd(metrics, metric_type)
                    if mrd:
                        mrds[metric_type_str] = mrd
                        logger.info(f"Generated MRD for {metric_type_str} with {len(metrics)} metrics")
                except ValueError as e:
                    logger.error(f"Invalid metric type: {metric_type_str} - {e}")
        
        return mrds
    
    def save_mrds_to_files(self, mrds: Dict[str, Dict], output_dir: Path) -> None:
        """
        Save MRDs to JSON files.

        Args:
            mrds: Dict mapping metric type strings to MRD dicts.
            output_dir: Path to output directory.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for metric_type, mrd in mrds.items():
            filename = f"{metric_type.lower()}_mrd.json"
            file_path = output_dir / filename
            
            try:
                with open(file_path, 'w') as f:
                    json.dump(mrd, f, indent=2)
                logger.info(f"Saved {metric_type} MRD to {file_path}")
            except Exception as e:
                logger.error(f"Failed to save {metric_type} MRD: {e}")
    
    def create_collection_mrd(self, mrds: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Create a collection MRD that references all individual MRDs.

        Args:
            mrds: Dict mapping metric type strings to MRD dicts.
        Returns:
            Collection MRD dict.
        """
        collection = {
            "@odata.type": "#MetricReportDefinitionCollection.MetricReportDefinitionCollection",
            "@odata.id": self.base_uri,
            "Name": "Metric Report Definition Collection",
            "Description": "Collection of metric report definitions generated from mockup data",
            "Members@odata.count": len(mrds),
            "Members": []
        }
        
        for metric_type, mrd in mrds.items():
            collection["Members"].append({
                "@odata.id": mrd.get("@odata.id", f"{self.base_uri}/{metric_type}")
            })
        
        return collection
    
    def validate_mrd(self, mrd: Dict[str, Any]) -> List[str]:
        """
        Validate an MRD against basic requirements.

        Args:
            mrd: MRD dict to validate.
        Returns:
            List of error strings, empty if valid.
        """
        errors = []
        # Required fields
        required_fields = ["@odata.type", "@odata.id", "Id", "Name", "Metrics"]
        for field in required_fields:
            if field not in mrd:
                errors.append(f"Missing required field: {field}")
        # Validate metrics structure
        if "Metrics" in mrd:
            for i, metric in enumerate(mrd["Metrics"]):
                if "MetricId" not in metric:
                    errors.append(f"Metric {i}: Missing MetricId")
                if "MetricProperties" not in metric:
                    errors.append(f"Metric {i}: Missing MetricProperties")
                elif not isinstance(metric["MetricProperties"], list):
                    errors.append(f"Metric {i}: MetricProperties must be a list")
        # Validate @odata.type
        if "@odata.type" in mrd:
            expected_type = "#MetricReportDefinition"
            if not mrd["@odata.type"].startswith(expected_type):
                errors.append(f"Invalid @odata.type: {mrd['@odata.type']}")
        return errors