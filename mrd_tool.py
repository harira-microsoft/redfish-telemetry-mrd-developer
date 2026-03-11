#!/usr/bin/env python3
# Copyright (c) 2026 Hari Ramachandran
# SPDX-License-Identifier: Apache-2.0
# See the LICENSE file in the project root for details.
"""
BMC Metric Report Definition Developer Tool

A tool for generating Redfish Metric Report Definitions from mockup data.
"""

import click
import logging
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID

from src.mockup_parser import MockupParser
from src.metric_classifier import MetricClassifier, MetricType
from src.mrd_generator import MRDGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

console = Console()


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.version_option(version='1.0.0', prog_name='Redfish Telemetry MRD Developer')
@click.pass_context
def cli(ctx, verbose):
    """
    Redfish Telemetry MRD Developer - Generate Redfish Metric Report Definitions
    
    This tool processes Redfish mockup data to generate MetricReportDefinition 
    files compliant with Redfish v1.3.0 schema. It supports classification of
    metrics into 6 categories and allows extensive customization through
    configuration files.
    
    Examples:
      # Analyze a mockup file
      python3 mrd_tool.py analyze -m mockup.tgz
      
      # Generate MRDs with custom configuration
      python3 mrd_tool.py generate -m mockup.tgz -c config.yaml -o output/
      
      # Validate a generated MRD file
      python3 mrd_tool.py validate -f output/environmentmetrics_mrd.json
    
    For detailed help on any command, use: python3 mrd_tool.py COMMAND --help
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Ensure context object exists
    ctx.ensure_object(dict)


@cli.command()
@click.option('--mockup-path', '-m', required=True, type=click.Path(exists=True),
              help='Path to Redfish mockup directory or tgz file')
@click.option('--output-dir', '-o', default='./output', type=click.Path(),
              help='Output directory for generated MRD files (default: ./output)')
@click.option('--metric-types', '-t', 
              help='Comma-separated list of metric types: PlatformMetrics,EnvironmentMetrics,ProcessorMetrics,MemoryMetrics,AlarmsMetrics,StatusAndCounterMetrics')
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Path to YAML configuration file for customizing MRD properties and metric mappings')
@click.option('--validate', is_flag=True, default=True,
              help='Validate generated MRD files against Redfish schema (default: enabled)')
def generate(mockup_path, output_dir, metric_types, config, validate):
    """
    Generate Metric Report Definitions from Redfish mockup data.
    
    This command processes a Redfish mockup and generates MetricReportDefinition
    files compliant with Redfish v1.3.0 schema. It classifies metrics into six
    categories and creates separate MRD files for each type containing metrics.
    
    Metric Categories:
      - PlatformMetrics: System power state, boot progress, system health
      - EnvironmentMetrics: Temperature, power consumption, fan speeds
      - ProcessorMetrics: CPU speed, core count, thread count
      - MemoryMetrics: Memory capacity, operating speed, ECC errors
      - AlarmsMetrics: Health faults, warning and critical alerts
      - StatusAndCounterMetrics: Network counters, packet rates, throughput
      
    Configuration Options:
      Use --config to specify a YAML file that can customize:
      • MRD properties (name, description, schedule)
      • Custom metric ID mappings
      • Per-metric-type settings
      
    Examples:
      # Generate all metric types with default settings
      python3 mrd_tool.py generate -m redfish_mockup.tgz
      
      # Generate only platform and environmental metrics
      python3 mrd_tool.py generate -m mockup/ -t PlatformMetrics,EnvironmentMetrics
      
      # Use custom configuration and output to specific directory
      python3 mrd_tool.py generate -m mockup.tgz -c config.yaml -o /output/mrds/
    """
    
    output_path = Path(output_dir)
    console.print(f"[bold green]Generating MRDs from mockup: {mockup_path}[/bold green]")
    console.print(f"Output directory: {output_path}")
    
    # Parse metric types filter
    selected_types = None
    if metric_types:
        try:
            selected_types = [MetricType(t.strip()) for t in metric_types.split(',')]
            console.print(f"Selected metric types: {[t.value for t in selected_types]}")
        except ValueError as e:
            console.print(f"[red]Error: Invalid metric type - {e}[/red]")
            return
    
    # Load custom configuration if provided
    mappings_config = None
    mrd_config = {}
    if config:
        try:
            import yaml
            with open(config, 'r') as f:
                config_data = yaml.safe_load(f)
                # Extract metric mappings for classifier
                if 'metric_mappings' in config_data:
                    # Convert to the format expected by MetricClassifier
                    mappings_config = config_data
                # MRD generator config (everything except metric_mappings for classifier)
                mrd_config = {k: v for k, v in config_data.items() 
                             if k not in ['metric_mappings']}
            console.print(f"Loaded configuration from: {config}")
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to load config - {e}[/yellow]")
    
    try:
        with Progress() as progress:
            # Parse mockup
            task = progress.add_task("Parsing mockup...", total=None)
            with MockupParser(mockup_path) as parser:
                mockup_data = parser.parse()
                metric_sources = parser.get_metric_sources()
            progress.update(task, completed=1, total=1)
            
            console.print(f"Found {len(metric_sources)} metric sources")
            
            # Classify metrics
            task = progress.add_task("Classifying metrics...", total=None)
            classifier = MetricClassifier(mappings_config)
            classified_metrics = {}
            
            # Initialize all metric types
            all_types = selected_types or list(MetricType)
            for metric_type in all_types:
                classified_metrics[metric_type.value] = classifier.extract_metrics_by_type(
                    metric_sources, metric_type
                )
            progress.update(task, completed=1, total=1)
            
            # Generate MRDs
            task = progress.add_task("Generating MRDs...", total=len(classified_metrics))
            # Pass complete config data to generator (includes metric_mappings for custom MetricId/Properties)
            if config:
                with open(config, 'r') as cf:
                    config_data = yaml.safe_load(cf)
            else:
                config_data = {}
            generator = MRDGenerator(config=config_data)
            mrds = generator.generate_all_mrds(classified_metrics)
            progress.update(task, completed=len(classified_metrics))
            
            # Save MRDs
            if mrds:
                task = progress.add_task("Saving MRDs...", total=len(mrds))
                generator.save_mrds_to_files(mrds, output_path)
                
                # Save collection
                collection = generator.create_collection_mrd(mrds)
                collection_path = output_path / "collection.json"
                with open(collection_path, 'w') as f:
                    json.dump(collection, f, indent=2)
                
                progress.update(task, completed=len(mrds))
                
                # Display results
                _display_results(mrds, classified_metrics)
                
                # Validate if requested
                if validate:
                    _validate_mrds(mrds)
                
                console.print(f"\n[bold green]✓ Generated {len(mrds)} MRDs in {output_path}[/bold green]")
            else:
                console.print("[yellow]No MRDs generated - no metrics found[/yellow]")
                
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Failed to generate MRDs")


@cli.command()
@click.option('--mrd-file', '-f', required=True, type=click.Path(exists=True),
              help='Path to MetricReportDefinition JSON file to validate')
def validate(mrd_file):
    """
    Validate a MetricReportDefinition file against Redfish schema.
    
    This command validates an existing MRD JSON file to ensure it conforms
    to the Redfish MetricReportDefinition v1.3.0 schema specification.
    It checks for:
    
    • Required properties and structure
    • Proper @odata.type and @odata.id format
    • Valid metric definitions and references
    • Correct enum values and data types
    • Schema compliance and best practices
    
    The validation provides detailed error messages for any issues found,
    making it easy to identify and fix problems in MRD files.
    
    Examples:
      python3 mrd_tool.py validate -f output/environmentalmetrics_mrd.json
      python3 mrd_tool.py validate -f /path/to/custom_mrd.json
    """
    try:
        with open(mrd_file, 'r') as f:
            mrd = json.load(f)
        
        generator = MRDGenerator()
        errors = generator.validate_mrd(mrd)
        
        if errors:
            console.print(f"[red]Validation failed for {mrd_file}:[/red]")
            for error in errors:
                console.print(f"  - {error}")
        else:
            console.print(f"[green]✓ {mrd_file} is valid[/green]")
            
    except Exception as e:
        console.print(f"[red]Error validating {mrd_file}: {e}[/red]")


@cli.command('examples')
def show_examples():
    """Show comprehensive usage examples and workflow guides."""
    console.print("""
[bold blue]Redfish Telemetry MRD Developer - Usage Examples[/bold blue]

[bold yellow]Basic Workflow:[/bold yellow]
1. Analyze mockup to see available metrics
2. Generate MRDs with desired configuration  
3. Validate generated files

[bold yellow]Quick Start Examples:[/bold yellow]

[cyan]# Analyze a mockup file[/cyan]
python3 mrd_tool.py analyze -m redfish_mockup.tgz

[cyan]# Generate all MRD types with defaults[/cyan]  
python3 mrd_tool.py generate -m redfish_mockup.tgz

[cyan]# Generate specific metric types only[/cyan]
python3 mrd_tool.py generate -m mockup/ -t PlatformMetrics,EnvironmentMetrics

[cyan]# Use custom configuration[/cyan]
python3 mrd_tool.py generate -m mockup.tgz -c config/high_performance_config.yaml

[cyan]# Validate a generated MRD[/cyan]
python3 mrd_tool.py validate -f output/platformmetrics_mrd.json

[bold yellow]Advanced Configuration:[/bold yellow]

Create a config.yaml file to customize MRD generation:
```yaml
# Global MRD properties
report_actions:
  - "RedfishEvent"
  - "LogToMetricReportsCollection"
recurrence_interval: "PT60S"

# Custom metric ID mappings
metric_mappings:
  "Temp_CPU0_Temperature": "CPU0_CoreTemperature"
  "Fan_1A_FanSpeed": "SystemFan_1A_Speed"

# Per-metric-type overrides
metric_type_configs:
  ProcessorMetrics:
    recurrence_interval: "PT5S"
```

[bold yellow]Metric Categories:[/bold yellow]
• [green]PlatformMetrics[/green]: System power state, boot progress, system health
• [blue]EnvironmentMetrics[/blue]: Temperature, power consumption, fan speeds
• [magenta]ProcessorMetrics[/magenta]: CPU speed, core count, thread count
• [red]MemoryMetrics[/red]: Memory capacity, operating speed, ECC errors
• [yellow]AlarmsMetrics[/yellow]: Health faults, warning and critical alerts
• [cyan]StatusAndCounterMetrics[/cyan]: Network counters, packet rates, throughput

[bold yellow]Output Files:[/bold yellow]
Generated MRDs are named by metric type:
• platformmetrics_mrd.json
• environmentmetrics_mrd.json
• processormetrics_mrd.json
• memorymetrics_mrd.json
• alarmsmetrics_mrd.json
• statusandcountermetrics_mrd.json
• collection.json

[bold yellow]Web Interface:[/bold yellow]
Launch the web UI for easier interaction:
```bash
python3 app.py
```
Then open http://localhost:5000 in your browser.

For detailed help on any command: python3 mrd_tool.py COMMAND --help
    """)


@cli.command()
@click.option('--mockup-path', '-m', required=True, type=click.Path(exists=True),
              help='Path to Redfish mockup directory or tgz file')
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Path to YAML configuration file (optional)')
def analyze(mockup_path, config):
    """
    Analyze Redfish mockup data and classify available metrics.
    
    This command performs comprehensive analysis of a Redfish mockup to identify
    and classify all available metrics into the six supported categories.
    It provides detailed information about:
    
    • Total number of telemetry sources found
    • Metric classification breakdown by type
    • Sample metrics for each category
    • Configuration suggestions for customization
    
    The analysis helps you understand what metrics are available in your
    mockup before generating MetricReportDefinitions, allowing you to
    make informed decisions about which metric types to generate.
    
    Use this command to:
    - Explore available metrics in a new mockup
    - Verify metric classification accuracy
    - Plan MRD generation strategy
    - Test configuration file effects
    
    Examples:
      python3 mrd_tool.py analyze -m redfish_mockup.tgz
      python3 mrd_tool.py analyze -m /path/to/mockup/ -c test_config.yaml
    """
    console.print(f"[bold blue]Analyzing mockup: {mockup_path}[/bold blue]")
    
    # Show configuration info if provided
    if config:
        console.print(f"[blue]📋 Using configuration: {config}[/blue]")
    
    try:
        with MockupParser(mockup_path) as parser:
            mockup_data = parser.parse()
            metric_sources = parser.get_metric_sources()
        
        # Display overview
        _display_analysis(mockup_data, metric_sources)
        
        # Classify and show potential metrics
        classifier = MetricClassifier()
        console.print("\n[bold]Potential Metrics by Type:[/bold]")
        
        for metric_type in MetricType:
            metrics = classifier.extract_metrics_by_type(metric_sources, metric_type)
            if metrics:
                console.print(f"\n[cyan]{metric_type.value}[/cyan] ({len(metrics)} metrics)")
                for metric in metrics[:5]:  # Show first 5
                    console.print(f"  - {metric['metric_name']} ({metric['source_name']})")
                if len(metrics) > 5:
                    console.print(f"  ... and {len(metrics) - 5} more")
            else:
                console.print(f"\n[dim]{metric_type.value}[/dim] (no metrics found)")
                
    except Exception as e:
        console.print(f"[red]Error analyzing mockup: {e}[/red]")
        logger.exception("Failed to analyze mockup")


def _display_results(mrds: dict, classified_metrics: dict):
    """Display generation results in a table."""
    table = Table(title="Generated Metric Report Definitions")
    table.add_column("Metric Type", style="cyan")
    table.add_column("Metrics Count", style="magenta")
    table.add_column("MRD Generated", style="green")
    
    for metric_type in MetricType:
        type_name = metric_type.value
        metrics_count = len(classified_metrics.get(type_name, []))
        mrd_generated = "✓" if type_name in mrds else "✗"
        table.add_row(type_name, str(metrics_count), mrd_generated)
    
    console.print(table)


def _validate_mrds(mrds: dict):
    """Validate all generated MRDs."""
    console.print("\n[bold]Validation Results:[/bold]")
    generator = MRDGenerator()
    
    for metric_type, mrd in mrds.items():
        errors = generator.validate_mrd(mrd)
        if errors:
            console.print(f"[red]✗ {metric_type}[/red]")
            for error in errors:
                console.print(f"    - {error}")
        else:
            console.print(f"[green]✓ {metric_type}[/green]")


def _display_analysis(mockup_data: dict, metric_sources: list):
    """Display mockup analysis results."""
    table = Table(title="Mockup Data Analysis")
    table.add_column("Resource Type", style="cyan")
    table.add_column("Count", style="magenta")
    table.add_column("Examples", style="dim")
    
    # Analyze resource types
    for resource_type, resources in mockup_data.items():
        if isinstance(resources, list):
            count = len(resources)
            examples = ", ".join([r.get('Name', r.get('Id', '')) for r in resources[:3]])
            if count > 3:
                examples += f" ... +{count-3} more"
        else:
            count = len(resources) if isinstance(resources, dict) else 0
            examples = "N/A"
        
        table.add_row(resource_type.title(), str(count), examples)
    
    console.print(table)
    
    # Show metric sources breakdown
    source_types = {}
    for source in metric_sources:
        source_type = source['type']
        source_types[source_type] = source_types.get(source_type, 0) + 1
    
    if source_types:
        console.print(f"\n[bold]Metric Sources Found:[/bold] {len(metric_sources)} total")
        for source_type, count in sorted(source_types.items()):
            console.print(f"  - {source_type}: {count}")


if __name__ == '__main__':
    cli()