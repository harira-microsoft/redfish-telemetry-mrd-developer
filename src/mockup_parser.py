# Copyright (c) 2026 Hari Ramachandran
# SPDX-License-Identifier: Apache-2.0
# See the LICENSE file in the project root for details.

"""
Redfish mockup parser for extracting metric data from mockup directories and tgz files.
"""

import os
import json
import tarfile
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class MockupParser:
    """Parser for Redfish mockup data."""
    
    def __init__(self, mockup_path: Union[str, Path]):
        """Initialize the parser with a mockup path."""
        self.mockup_path = Path(mockup_path)
        self.temp_dir = None
        self.data = {}
        
    def __enter__(self) -> 'MockupParser':
        """Context manager entry."""
        if self.mockup_path.suffix == '.tgz':
            self._extract_tgz()
        return self
        
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        if self.temp_dir:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _extract_tgz(self) -> None:
        """Extract tgz file to temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        with tarfile.open(self.mockup_path, 'r:gz') as tar:
            tar.extractall(self.temp_dir)
        
        # Find the actual mockup directory containing redfish data
        # First, check if there's only one extracted item
        extracted_items = os.listdir(self.temp_dir)
        if len(extracted_items) == 1:
            self.mockup_path = Path(self.temp_dir) / extracted_items[0]
        else:
            # Multiple items - search for directory containing redfish/v1
            redfish_dir_found = False
            for item in extracted_items:
                item_path = Path(self.temp_dir) / item
                if item_path.is_dir():
                    redfish_path = item_path / "redfish" / "v1"
                    if redfish_path.exists():
                        self.mockup_path = item_path
                        redfish_dir_found = True
                        logger.info(f"Found Redfish mockup in subdirectory: {item}")
                        break
            
            # If no redfish directory found in subdirectories, use temp_dir
            if not redfish_dir_found:
                self.mockup_path = Path(self.temp_dir)
    
    def parse(self) -> Dict[str, Any]:
        """Parse the mockup directory and return structured data."""
        if not self.mockup_path.exists():
            raise FileNotFoundError(f"Mockup path not found: {self.mockup_path}")
        
        logger.info(f"Parsing mockup from: {self.mockup_path}")
        self.data = {
            "systems": self._parse_systems(),
            "chassis": self._parse_chassis(),
            "managers": self._parse_managers(),
            "telemetry": self._parse_telemetry(),
            "sensors": self._parse_sensors(),
            "memory": self._parse_memory(),
            "processors": self._parse_processors(),
            "power": self._parse_power(),
            "thermal": self._parse_thermal()
        }
        
        return self.data
    
    def _parse_systems(self) -> List[Dict]:
        """Parse ComputerSystem resources."""
        systems = []
        systems_path = self.mockup_path / "redfish" / "v1" / "Systems"
        
        if systems_path.exists():
            for system_dir in systems_path.iterdir():
                if system_dir.is_dir():
                    index_file = system_dir / "index.json"
                    if index_file.exists():
                        try:
                            with open(index_file, 'r') as f:
                                system_data = json.load(f)
                                system_data['_mockup_path'] = str(system_dir)
                                systems.append(system_data)
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse system data: {index_file} - {e}")
        
        return systems
    
    def _parse_chassis(self) -> List[Dict]:
        """Parse Chassis resources."""
        chassis_list = []
        chassis_path = self.mockup_path / "redfish" / "v1" / "Chassis"
        
        if chassis_path.exists():
            for chassis_dir in chassis_path.iterdir():
                if chassis_dir.is_dir():
                    index_file = chassis_dir / "index.json"
                    if index_file.exists():
                        try:
                            with open(index_file, 'r') as f:
                                chassis_data = json.load(f)
                                chassis_data['_mockup_path'] = str(chassis_dir)
                                chassis_list.append(chassis_data)
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse chassis data: {index_file} - {e}")
        
        return chassis_list
    
    def _parse_managers(self) -> List[Dict]:
        """Parse Manager resources."""
        managers = []
        managers_path = self.mockup_path / "redfish" / "v1" / "Managers"
        
        if managers_path.exists():
            for manager_dir in managers_path.iterdir():
                if manager_dir.is_dir():
                    index_file = manager_dir / "index.json"
                    if index_file.exists():
                        try:
                            with open(index_file, 'r') as f:
                                manager_data = json.load(f)
                                manager_data['_mockup_path'] = str(manager_dir)
                                managers.append(manager_data)
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse manager data: {index_file} - {e}")
        
        return managers
    
    def _parse_telemetry(self) -> Dict[str, Any]:
        """Parse Telemetry service and metric reports."""
        telemetry_data = {}
        telemetry_path = self.mockup_path / "redfish" / "v1" / "TelemetryService"
        
        if telemetry_path.exists():
            # Parse TelemetryService
            index_file = telemetry_path / "index.json"
            if index_file.exists():
                try:
                    with open(index_file, 'r') as f:
                        telemetry_data['service'] = json.load(f)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse telemetry service: {index_file} - {e}")
            
            # Parse MetricReports
            reports_path = telemetry_path / "MetricReports"
            if reports_path.exists():
                telemetry_data['metric_reports'] = self._parse_json_collection(reports_path)
            
            # Parse MetricReportDefinitions
            definitions_path = telemetry_path / "MetricReportDefinitions"
            if definitions_path.exists():
                telemetry_data['metric_report_definitions'] = self._parse_json_collection(definitions_path)
        
        return telemetry_data
    
    def _parse_sensors(self) -> List[Dict]:
        """Parse sensor data from various locations."""
        sensors = []
        
        # Look for sensors in Chassis
        for chassis_dir in (self.mockup_path / "redfish" / "v1" / "Chassis").glob("*/"):
            sensors_path = chassis_dir / "Sensors"
            if sensors_path.exists():
                sensors.extend(self._parse_json_collection(sensors_path))
        
        return sensors
    
    def _parse_memory(self) -> List[Dict]:
        """Parse memory resources."""
        memory = []
        
        # Look for memory in Systems
        for system_dir in (self.mockup_path / "redfish" / "v1" / "Systems").glob("*/"):
            memory_path = system_dir / "Memory"
            if memory_path.exists():
                memory.extend(self._parse_json_collection(memory_path))
        
        return memory
    
    def _parse_processors(self) -> List[Dict]:
        """Parse processor resources."""
        processors = []
        
        # Look for processors in Systems
        for system_dir in (self.mockup_path / "redfish" / "v1" / "Systems").glob("*/"):
            processors_path = system_dir / "Processors"
            if processors_path.exists():
                processors.extend(self._parse_json_collection(processors_path))
        
        return processors
    
    def _parse_power(self) -> List[Dict]:
        """Parse power resources."""
        power = []
        
        # Look for power in Chassis
        for chassis_dir in (self.mockup_path / "redfish" / "v1" / "Chassis").glob("*/"):
            power_path = chassis_dir / "Power"
            if power_path.exists():
                index_file = power_path / "index.json"
                if index_file.exists():
                    try:
                        with open(index_file, 'r') as f:
                            power_data = json.load(f)
                            power_data['_mockup_path'] = str(power_path)
                            power.append(power_data)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse power data: {index_file} - {e}")
        
        return power
    
    def _parse_thermal(self) -> List[Dict]:
        """Parse thermal resources."""
        thermal = []
        
        # Look for thermal in Chassis
        for chassis_dir in (self.mockup_path / "redfish" / "v1" / "Chassis").glob("*/"):
            thermal_path = chassis_dir / "Thermal"
            if thermal_path.exists():
                index_file = thermal_path / "index.json"
                if index_file.exists():
                    try:
                        with open(index_file, 'r') as f:
                            thermal_data = json.load(f)
                            thermal_data['_mockup_path'] = str(thermal_path)
                            thermal.append(thermal_data)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse thermal data: {index_file} - {e}")
        
        return thermal
    
    def _parse_json_collection(self, collection_path: Path) -> List[Dict]:
        """Parse a collection of JSON resources."""
        items = []
        
        if not collection_path.exists():
            return items
        
        # First try to parse the collection index
        index_file = collection_path / "index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    collection_data = json.load(f)
                    if 'Members' in collection_data:
                        # This is a collection, parse individual members
                        for member_ref in collection_data.get('Members', []):
                            if '@odata.id' in member_ref:
                                member_path = self._odata_id_to_path(member_ref['@odata.id'])
                                if member_path and member_path.exists():
                                    try:
                                        with open(member_path, 'r') as mf:
                                            member_data = json.load(mf)
                                            member_data['_mockup_path'] = str(member_path.parent)
                                            items.append(member_data)
                                    except json.JSONDecodeError as e:
                                        logger.warning(f"Failed to parse member: {member_path} - {e}")
                    else:
                        # This might be a single resource
                        collection_data['_mockup_path'] = str(collection_path)
                        items.append(collection_data)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse collection: {index_file} - {e}")
        
        # Also look for individual item directories
        for item_dir in collection_path.iterdir():
            if item_dir.is_dir():
                item_index = item_dir / "index.json"
                if item_index.exists():
                    try:
                        with open(item_index, 'r') as f:
                            item_data = json.load(f)
                            item_data['_mockup_path'] = str(item_dir)
                            # Avoid duplicates
                            if not any(item.get('@odata.id') == item_data.get('@odata.id') for item in items):
                                items.append(item_data)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse item: {item_index} - {e}")
        
        return items
    
    def _odata_id_to_path(self, odata_id: str) -> Optional[Path]:
        """Convert an @odata.id to a filesystem path."""
        # Remove leading '/redfish/v1' and convert to path
        if odata_id.startswith('/redfish/v1'):
            relative_path = odata_id[len('/redfish/v1'):].lstrip('/')
            if relative_path:
                return self.mockup_path / "redfish" / "v1" / relative_path / "index.json"
        return None
    
    def get_metric_sources(self) -> List[Dict]:
        """Get all potential metric sources from the parsed data."""
        metric_sources = []
        
        # Add systems as metric sources
        for system in self.data.get('systems', []):
            metric_sources.append({
                'type': 'system',
                'id': system.get('Id', ''),
                'name': system.get('Name', ''),
                'data': system
            })
        
        # Add processors as metric sources
        for processor in self.data.get('processors', []):
            metric_sources.append({
                'type': 'processor',
                'id': processor.get('Id', ''),
                'name': processor.get('Name', ''),
                'data': processor
            })
        
        # Add memory as metric sources
        for memory in self.data.get('memory', []):
            metric_sources.append({
                'type': 'memory',
                'id': memory.get('Id', ''),
                'name': memory.get('Name', ''),
                'data': memory
            })
        
        # Add sensors as metric sources
        for sensor in self.data.get('sensors', []):
            metric_sources.append({
                'type': 'sensor',
                'id': sensor.get('Id', ''),
                'name': sensor.get('Name', ''),
                'data': sensor
            })
        
        # Add power supplies as metric sources
        for power in self.data.get('power', []):
            for supply in power.get('PowerSupplies', []):
                metric_sources.append({
                    'type': 'power_supply',
                    'id': supply.get('Name', ''),
                    'name': supply.get('Name', ''),
                    'data': supply
                })
        
        # Add thermal sensors as metric sources
        for thermal in self.data.get('thermal', []):
            for temp in thermal.get('Temperatures', []):
                metric_sources.append({
                    'type': 'temperature',
                    'id': temp.get('Name', ''),
                    'name': temp.get('Name', ''),
                    'data': temp
                })
            for fan in thermal.get('Fans', []):
                metric_sources.append({
                    'type': 'fan',
                    'id': fan.get('Name', ''),
                    'name': fan.get('Name', ''),
                    'data': fan
                })
        
        return metric_sources