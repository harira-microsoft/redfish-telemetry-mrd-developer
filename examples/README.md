# Example Usage

This directory contains example outputs from the Redfish Telemetry MRD Developer.

## Sample Commands

```bash
# Generate all MRDs from a mockup directory
python mrd_tool.py generate --mockup-path /path/to/mockup --output-dir ./output

# Generate only specific metric types
python mrd_tool.py generate --mockup-path /path/to/mockup --metric-types PlatformMetrics,EnvironmentMetrics --output-dir ./output

# Analyze mockup without generating MRDs
python mrd_tool.py analyze --mockup-path /path/to/mockup

# Validate generated MRD
python mrd_tool.py validate --mrd-file ./output/platformmetrics_mrd.json
```

## Sample Output Files

- `platformmetrics_mrd.json` - Platform metrics MRD (power state, health, boot progress)
- `environmentmetrics_mrd.json` - Environment metrics MRD (temperature, fan speed)
- `collection.json` - Collection resource linking all generated MRDs

## Customization

You can customize metric classification by providing a custom YAML configuration file:

```bash
python mrd_tool.py generate --mockup-path /path/to/mockup --config ./custom_mappings.yaml --output-dir ./output
```

The configuration file should follow the same structure as `config/metric_mappings.yaml`.