# Copyright (c) 2026 Hari Ramachandran
# SPDX-License-Identifier: Apache-2.0
# See the LICENSE file in the project root for details.

import sys
import os
import json
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mrd_generator import MRDGenerator, MRDGenerationError
from src.metric_classifier import MetricClassifier, MetricType


# ── MRDGenerator tests ──────────────────────────────────────────────────────

def test_generate_mrd_no_metrics_raises():
    generator = MRDGenerator()
    with pytest.raises(MRDGenerationError):
        generator.generate_mrd([], MetricType.PLATFORM_METRICS)


def test_validate_mrd_missing_fields_returns_errors():
    """validate_mrd should return a non-empty error list, not raise."""
    generator = MRDGenerator()
    invalid_mrd = {"Id": "Test"}
    errors = generator.validate_mrd(invalid_mrd)
    assert isinstance(errors, list)
    assert len(errors) > 0
    assert any("Missing required field" in e for e in errors)


def test_validate_mrd_valid_returns_empty_list():
    generator = MRDGenerator()
    metrics = [{
        'source_id': 'sys1',
        'metric_name': 'PowerState',
        'metric_property': 'PowerState',
        'data_type': 'String',
        'current_value': 'On'
    }]
    mrd = generator.generate_mrd(metrics, MetricType.PLATFORM_METRICS)
    errors = generator.validate_mrd(mrd)
    assert errors == []


def test_generate_mrd_structure():
    """Generated MRD must have all required Redfish fields."""
    generator = MRDGenerator()
    metrics = [{
        'source_id': 'sys1',
        'metric_name': 'PowerState',
        'metric_property': 'PowerState',
        'data_type': 'String',
        'current_value': 'On'
    }]
    mrd = generator.generate_mrd(metrics, MetricType.PLATFORM_METRICS)
    assert mrd["@odata.type"].startswith("#MetricReportDefinition")
    assert "@odata.id" in mrd
    assert "Id" in mrd
    assert "Metrics" in mrd
    assert len(mrd["Metrics"]) == 1
    assert "MetricId" in mrd["Metrics"][0]
    assert "MetricProperties" in mrd["Metrics"][0]


def test_generate_mrd_custom_config():
    """Config overrides for report_actions and recurrence_interval are applied."""
    config = {
        'report_actions': ['RedfishEvent'],
        'recurrence_interval': 'PT10S'
    }
    generator = MRDGenerator(config=config)
    metrics = [{
        'source_id': 'sys1',
        'metric_name': 'PowerState',
        'metric_property': 'PowerState',
        'data_type': 'String',
    }]
    mrd = generator.generate_mrd(metrics, MetricType.PLATFORM_METRICS)
    assert mrd["ReportActions"] == ['RedfishEvent']
    assert mrd["Schedule"]["RecurrenceInterval"] == 'PT10S'


def test_generate_all_mrds():
    classified = {
        MetricType.PLATFORM_METRICS.value: [{
            'source_id': 'sys1', 'metric_name': 'PowerState',
            'metric_property': 'PowerState', 'data_type': 'String'
        }],
        MetricType.ENVIRONMENT_METRICS.value: [],  # empty — no MRD expected
    }
    generator = MRDGenerator()
    mrds = generator.generate_all_mrds(classified)
    assert MetricType.PLATFORM_METRICS.value in mrds
    assert MetricType.ENVIRONMENT_METRICS.value not in mrds


def test_save_mrds_to_files(tmp_path):
    generator = MRDGenerator()
    metrics = [{'source_id': 'sys1', 'metric_name': 'PowerState',
                'metric_property': 'PowerState', 'data_type': 'String'}]
    mrds = {MetricType.PLATFORM_METRICS.value: generator.generate_mrd(metrics, MetricType.PLATFORM_METRICS)}
    generator.save_mrds_to_files(mrds, tmp_path)
    saved = list(tmp_path.glob("*.json"))
    assert len(saved) == 1
    with open(saved[0]) as f:
        data = json.load(f)
    assert "@odata.type" in data


def test_create_collection_mrd():
    generator = MRDGenerator()
    metrics = [{'source_id': 'sys1', 'metric_name': 'PowerState',
                'metric_property': 'PowerState', 'data_type': 'String'}]
    mrds = {MetricType.PLATFORM_METRICS.value: generator.generate_mrd(metrics, MetricType.PLATFORM_METRICS)}
    collection = generator.create_collection_mrd(mrds)
    assert collection["Members@odata.count"] == 1
    assert len(collection["Members"]) == 1


# ── MetricClassifier tests ──────────────────────────────────────────────────

def test_classifier_default_mappings():
    classifier = MetricClassifier()
    assert MetricType.PLATFORM_METRICS.value in classifier.mappings
    assert MetricType.ENVIRONMENT_METRICS.value in classifier.mappings


def test_classify_system_source():
    classifier = MetricClassifier()
    source = {'type': 'system', 'id': '1', 'name': 'System1', 'data': {}}
    types = classifier.classify_metric_source(source)
    assert MetricType.PLATFORM_METRICS in types


def test_classify_temperature_source():
    classifier = MetricClassifier()
    source = {'type': 'temperature', 'id': 'CPU_Temp', 'name': 'CPU Temp',
              'data': {'ReadingCelsius': 45.0}}
    types = classifier.classify_metric_source(source)
    assert MetricType.ENVIRONMENT_METRICS in types


def test_classify_fan_source():
    classifier = MetricClassifier()
    source = {'type': 'fan', 'id': 'Fan1A', 'name': 'Fan 1A',
              'data': {'Reading': 4200}}
    types = classifier.classify_metric_source(source)
    assert MetricType.ENVIRONMENT_METRICS in types


def test_classify_processor_source():
    classifier = MetricClassifier()
    source = {'type': 'processor', 'id': 'CPU0', 'name': 'CPU 0',
              'data': {'TotalCores': 16, 'MaxSpeedMHz': 3600}}
    types = classifier.classify_metric_source(source)
    assert MetricType.PROCESSOR_METRICS in types


def test_classify_memory_source():
    classifier = MetricClassifier()
    source = {'type': 'memory', 'id': 'DIMM_A', 'name': 'DIMM A',
              'data': {'CapacityMiB': 16384}}
    types = classifier.classify_metric_source(source)
    assert MetricType.MEMORY_METRICS in types


def test_extract_environment_metrics():
    classifier = MetricClassifier()
    sources = [
        {'type': 'temperature', 'id': 'CPUTemp', 'name': 'CPU Temp',
         'data': {'ReadingCelsius': 55.0}}
    ]
    metrics = classifier.extract_metrics_by_type(sources, MetricType.ENVIRONMENT_METRICS)
    assert len(metrics) > 0
    assert metrics[0]['metric_name'] == 'Temperature'
    assert metrics[0]['units'] == 'Cel'


def test_extract_processor_metrics():
    classifier = MetricClassifier()
    sources = [
        {'type': 'processor', 'id': 'CPU0', 'name': 'CPU 0',
         'data': {'TotalCores': 8, 'TotalThreads': 16, 'MaxSpeedMHz': 3200}}
    ]
    metrics = classifier.extract_metrics_by_type(sources, MetricType.PROCESSOR_METRICS)
    metric_names = [m['metric_name'] for m in metrics]
    assert 'ProcessorCores' in metric_names
    assert 'ProcessorThreads' in metric_names
    assert 'ProcessorMaxSpeed' in metric_names


def test_extract_memory_metrics():
    classifier = MetricClassifier()
    sources = [
        {'type': 'memory', 'id': 'DIMM_A', 'name': 'DIMM A',
         'data': {'CapacityMiB': 32768, 'OperatingSpeedMhz': 3200}}
    ]
    metrics = classifier.extract_metrics_by_type(sources, MetricType.MEMORY_METRICS)
    metric_names = [m['metric_name'] for m in metrics]
    assert 'MemoryCapacity' in metric_names
    assert 'MemorySpeed' in metric_names


def test_no_metrics_for_empty_source():
    classifier = MetricClassifier()
    metrics = classifier.extract_metrics_by_type([], MetricType.PLATFORM_METRICS)
    assert metrics == []
