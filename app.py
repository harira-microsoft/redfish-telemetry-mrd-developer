# Copyright (c) 2026 Hari Ramachandran
# SPDX-License-Identifier: Apache-2.0
# See the LICENSE file in the project root for details.

"""
Web UI for Redfish Telemetry MRD Developer
Flask-based interface for generating Redfish Metric Report Definitions
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import json
import yaml
import tempfile
import zipfile
from pathlib import Path
import logging
from datetime import datetime
import shutil

# Import our existing modules
from src.mockup_parser import MockupParser
from src.metric_classifier import MetricClassifier, MetricType
from src.mrd_generator import MRDGenerator

app = Flask(__name__)
# Use environment variable for secret key
_secret_key = os.environ.get('REDFISH_MRD_SECRET_KEY')
if not _secret_key:
    import warnings
    warnings.warn(
        "REDFISH_MRD_SECRET_KEY environment variable is not set. "
        "Using an insecure fallback key. Set this variable before exposing the web UI.",
        stacklevel=2
    )
    _secret_key = 'change-this-in-production'
app.secret_key = _secret_key
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = '.temp/uploads'
app.config['OUTPUT_FOLDER'] = 'outputs/web_output'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'tgz', 'tar.gz', 'zip', 'yaml', 'yml', 'json'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index() -> str:
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file() -> str:
    """Handle mockup file uploads"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'mockup_file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['mockup_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            flash(f'File {file.filename} uploaded successfully!', 'success')
            return redirect(url_for('analyze', filename=filename))
        else:
            flash('Invalid file type. Please upload .tgz, .tar.gz, .zip, .yaml, or .json files', 'error')
    
    return render_template('upload.html')

@app.route('/analyze')
@app.route('/analyze/<filename>')
def analyze(filename: str = None) -> str:
    """Analyze uploaded mockup and show metrics breakdown"""
    if not filename:
        uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
        mockup_files = [f for f in uploaded_files if f.endswith(('.tgz', '.tar.gz', '.zip'))]
        return render_template('analyze.html', files=mockup_files)
    
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            flash('File not found', 'error')
            return redirect(url_for('upload_file'))
        
        # Parse mockup
        with MockupParser(filepath) as parser:
            mockup_data = parser.parse()
            metric_sources = parser.get_metric_sources()
        
        # Classify metrics
        classifier = MetricClassifier()
        classified_metrics = {}
        
        for metric_type in MetricType:
            metrics = classifier.extract_metrics_by_type(metric_sources, metric_type)
            if metrics:
                classified_metrics[metric_type.value] = {
                    'count': len(metrics),
                    'metrics': metrics[:10]  # Show first 10 for preview
                }
        
        # Prepare summary data
        analysis_data = {
            'filename': filename,
            'total_sources': len(metric_sources),
            'total_metrics': sum(data['count'] for data in classified_metrics.values()),
            'metric_types': classified_metrics,
            'mockup_info': {
                'systems': len(mockup_data.get('systems', {})),
                'chassis': len(mockup_data.get('chassis', {})),
                'managers': len(mockup_data.get('managers', {}))
            }
        }
        
        return render_template('analyze_results.html', data=analysis_data)
        
    except Exception as e:
        logger.exception("Failed to analyze mockup")
        flash(f'Error analyzing mockup: {str(e)}', 'error')
        return redirect(url_for('upload_file'))

@app.route('/configure')
@app.route('/configure/<filename>')
def configure(filename: str = None) -> str:
    """Configuration page for MRD generation settings"""
    if not filename:
        uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
        mockup_files = [f for f in uploaded_files if f.endswith(('.tgz', '.tar.gz', '.zip'))]
        return render_template('configure.html', files=mockup_files)
    
    # Load default configuration
    default_config = {
        'report_actions': ['RedfishEvent', 'LogToMetricReportsCollection'],
        'report_updates': 'Overwrite',
        'append_limit': 100,
        'heartbeat_interval': 'PT0S',
        'recurrence_interval': 'PT60S',
        'metric_type_configs': {
            'EnvironmentMetrics': {
                'recurrence_interval': 'PT30S',
                'heartbeat_interval': 'PT5M'
            },
            'ProcessorMetrics': {
                'recurrence_interval': 'PT10S',
                'report_actions': ['RedfishEvent']
            }
        },
        'selected_types': list(MetricType.__members__.keys())
    }
    
    return render_template('configure_form.html', 
                         filename=filename, 
                         config=default_config,
                         metric_types=list(MetricType.__members__.keys()))

@app.route('/generate', methods=['POST'])
def generate_mrds() -> 'Response':
    """Generate MRDs based on configuration"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        config = data.get('config', {})
        
        if not filename:
            return jsonify({'error': 'No mockup file specified'}), 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Mockup file not found'}), 404
        
        # Parse mockup
        with MockupParser(filepath) as parser:
            mockup_data = parser.parse()
            metric_sources = parser.get_metric_sources()
        
        # Classify metrics
        classifier = MetricClassifier(config)
        classified_metrics = {}
        
        # Filter by selected metric types
        selected_types = config.get('selected_types', [])
        for metric_type_name in selected_types:
            try:
                metric_type = MetricType[metric_type_name]
                metrics = classifier.extract_metrics_by_type(metric_sources, metric_type)
                if metrics:
                    classified_metrics[metric_type.value] = metrics
            except KeyError:
                logger.warning(f"Unknown metric type: {metric_type_name}")
        
        # Generate MRDs
        generator = MRDGenerator(config=config)
        mrds = generator.generate_all_mrds(classified_metrics)
        
        if not mrds:
            return jsonify({'error': 'No MRDs generated - no metrics found'}), 400
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(app.config['OUTPUT_FOLDER']) / f"mrds_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save MRDs
        generator.save_mrds_to_files(mrds, output_dir)
        
        # Save collection
        collection = generator.create_collection_mrd(mrds)
        collection_path = output_dir / "collection.json"
        with open(collection_path, 'w') as f:
            json.dump(collection, f, indent=2)
        
        # Prepare response data
        results = {
            'success': True,
            'output_dir': str(output_dir.name),
            'mrds_generated': len(mrds),
            'metric_summary': {
                metric_type: len(metrics) 
                for metric_type, metrics in classified_metrics.items()
            },
            'files': list(mrds.keys()) + ['collection']
        }
        
        return jsonify(results)
        
    except Exception as e:
        logger.exception("Failed to generate MRDs")
        return jsonify({'error': f'Failed to generate MRDs: {str(e)}'}), 500

@app.route('/download/<output_dir>')
@app.route('/download/<output_dir>/<filename>')
def download_file(output_dir: str, filename: str = None) -> 'Response':
    """Download generated MRD files"""
    try:
        output_path = Path(app.config['OUTPUT_FOLDER']) / output_dir
        
        if not output_path.exists():
            flash('Output directory not found', 'error')
            return redirect(url_for('index'))
        
        if filename:
            # Download specific file
            if filename == 'collection':
                filename = 'collection.json'
            elif not filename.endswith('.json'):
                filename = f"{filename.lower()}_mrd.json"
            
            file_path = output_path / filename
            if file_path.exists():
                return send_file(file_path, as_attachment=True)
            else:
                flash('File not found', 'error')
                return redirect(url_for('results', output_dir=output_dir))
        else:
            # Create and download zip of all files
            zip_path = output_path / "mrds.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file_path in output_path.glob('*.json'):
                    zipf.write(file_path, file_path.name)
            
            return send_file(zip_path, as_attachment=True, 
                           download_name=f"mrds_{output_dir}.zip")
            
    except Exception as e:
        logger.exception("Failed to download file")
        flash(f'Download failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/results/<output_dir>')
def results(output_dir: str) -> str:
    """Show generation results"""
    try:
        output_path = Path(app.config['OUTPUT_FOLDER']) / output_dir
        
        if not output_path.exists():
            flash('Output directory not found', 'error')
            return redirect(url_for('index'))
        
        # List generated files
        files = []
        for file_path in output_path.glob('*.json'):
            if file_path.name == 'collection.json':
                files.append({
                    'name': 'Collection',
                    'filename': 'collection',
                    'size': file_path.stat().st_size,
                    'type': 'Collection'
                })
            else:
                metric_type = file_path.stem.replace('_mrd', '').title()
                files.append({
                    'name': f'{metric_type} MRD',
                    'filename': file_path.stem,
                    'size': file_path.stat().st_size,
                    'type': 'MRD'
                })
        
        return render_template('results.html', 
                             output_dir=output_dir,
                             files=files)
        
    except Exception as e:
        logger.exception("Failed to show results")
        flash(f'Error loading results: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/config/load/<config_type>')
def load_config(config_type: str) -> 'Response':
    """Load predefined configuration"""
    try:
        config_files = {
            'basic': 'config/mrd_config_example.yaml',
            'performance': 'config/high_performance_config.yaml',
            'schema': 'config/mrd_config_schema.yaml'
        }
        
        if config_type not in config_files:
            return jsonify({'error': 'Unknown configuration type'}), 400
        
        config_path = config_files[config_type]
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            return jsonify(config_data)
        else:
            return jsonify({'error': 'Configuration file not found'}), 404
            
    except Exception as e:
        logger.exception("Failed to load configuration")
        return jsonify({'error': f'Failed to load configuration: {str(e)}'}), 500

@app.route('/api/validate', methods=['POST'])
def validate_mrd() -> 'Response':
    """Validate a generated MRD"""
    try:
        data = request.get_json()
        mrd_data = data.get('mrd')
        
        if not mrd_data:
            return jsonify({'error': 'No MRD data provided'}), 400
        
        generator = MRDGenerator()
        errors = generator.validate_mrd(mrd_data)
        
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors
        })
        
    except Exception as e:
        logger.exception("Failed to validate MRD")
        return jsonify({'error': f'Validation failed: {str(e)}'}), 500

@app.route('/docs')
def documentation_index() -> str:
    """Display documentation index page"""
    try:
        docs_dir = Path('docs')
        doc_files = []
        
        if docs_dir.exists():
            for file_path in docs_dir.glob('*.md'):
                if file_path.name != 'README.md':  # Skip the directory README
                    doc_files.append({
                        'name': file_path.name,
                        'title': file_path.stem.replace('_', ' ').title(),
                        'path': file_path.name
                    })
        
        # Sort by title for better organization
        doc_files.sort(key=lambda x: x['title'])
        
        return render_template('documentation_index.html', doc_files=doc_files)
        
    except Exception as e:
        logger.exception("Failed to load documentation index")
        flash(f'Error loading documentation: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/docs/<path:filename>')
def view_documentation(filename: str) -> str:
    """Display a specific documentation file"""
    try:
        # Security check - prevent directory traversal
        if '..' in filename or filename.startswith('/'):
            flash('Invalid documentation file requested', 'error')
            return redirect(url_for('documentation_index'))
        
        doc_path = Path('docs') / filename
        
        if not doc_path.exists() or not doc_path.suffix == '.md':
            flash('Documentation file not found', 'error')
            return redirect(url_for('documentation_index'))
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title from filename
        title = filename.replace('_', ' ').replace('.md', '').title()
        
        return render_template('documentation_viewer.html', 
                             content=content, 
                             title=title,
                             filename=filename)
        
    except Exception as e:
        logger.exception(f"Failed to load documentation file: {filename}")
        flash(f'Error loading documentation: {str(e)}', 'error')
        return redirect(url_for('documentation_index'))

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=5000)