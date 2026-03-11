# Redfish Telemetry MRD Developer - Web Interface

A modern web interface for generating Redfish Metric Report Definitions from BMC mockup data.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Flask and dependencies (see requirements.txt)

### Installation
```bash
# Clone or navigate to the project directory
cd redfish-telemetry-mrd-developer

# Install dependencies
pip3 install -r requirements.txt

# Start the web application
python3 app.py
```

### Access the Web UI
Open your browser and navigate to:
- **Local:** http://localhost:5000

## 🎯 Features

### Dashboard
- **Welcome Page**: Overview of the tool and process steps
- **Feature Cards**: Quick access to different metric types
- **Navigation**: Intuitive sidebar with step-by-step workflow

### Upload & Analysis
- **File Upload**: Drag-and-drop interface for .tgz, .zip, .tar.gz files
- **Progress Tracking**: Visual progress indicators during upload
- **File Validation**: Automatic validation of mockup file formats
- **Mockup Analysis**: Automatic parsing and metric classification

### Configuration
- **Interactive Forms**: Easy-to-use configuration interface
- **Template Loading**: Pre-configured templates (Basic, High Performance)
- **Per-Type Settings**: Override global settings for specific metric types
- **Real-time Validation**: Immediate feedback on configuration values

### Generation & Download
- **Batch Generation**: Generate all MRDs with one click
- **Individual Downloads**: Download specific MRD files
- **ZIP Archive**: Download all files as a single archive
- **Validation**: Built-in MRD validation against Redfish schema

## 🔧 API Endpoints

### Core Functionality
- `GET /` - Dashboard
- `POST /upload` - Upload mockup files
- `GET /analyze/<filename>` - Analyze mockup data
- `GET /configure/<filename>` - Configuration interface
- `POST /generate` - Generate MRDs
- `GET /results/<output_dir>` - View generation results
- `GET /download/<output_dir>/<filename>` - Download files

### Configuration API
- `GET /api/config/load/<config_type>` - Load predefined configurations
- `POST /api/validate` - Validate MRD files

## 📁 File Structure

```
redfish-telemetry-mrd-developer/
├── app.py                 # Flask web application
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Dashboard
│   ├── upload.html       # File upload
│   ├── analyze.html      # File selection
│   ├── analyze_results.html  # Analysis results
│   ├── configure_form.html   # Configuration interface
│   └── results.html      # Generation results
├── uploads/              # Uploaded mockup files
├── web_output/          # Generated MRD files
└── src/                 # Core modules (unchanged)
```

## 💡 Usage Workflow

### 1. Upload Mockup
1. Click **"Upload Mockup"** in the sidebar
2. Select your .tgz, .zip, or .tar.gz mockup file
3. Click **"Upload & Analyze"**

### 2. Review Analysis
1. View the mockup analysis results
2. See metric counts by type
3. Review discovered sensors and resources
4. Click **"Configure MRDs"** to proceed

### 3. Configure Settings
1. Select which metric types to generate
2. Set global MRD properties:
   - Report Actions (RedfishEvent, LogToMetricReportsCollection)
   - Report Updates (Overwrite, Append modes)
   - Intervals (Recurrence, Heartbeat)
3. Optionally configure per-type overrides
4. Load predefined templates for common scenarios

### 4. Generate & Download
1. Click **"Generate MRDs"** 
2. Wait for processing to complete
3. Download individual files or the complete ZIP archive
4. Validate generated MRDs against Redfish schema

## 🎨 UI Features

### Responsive Design
- **Bootstrap 5**: Modern, mobile-friendly interface
- **Progressive Steps**: Clear workflow indication
- **Icon Integration**: Bootstrap Icons for visual clarity

### Interactive Elements
- **Real-time Validation**: Form validation with immediate feedback
- **Progress Indicators**: Visual progress for long operations
- **Modal Dialogs**: File preview and validation results
- **Alert System**: Success/error notifications

### Configuration Templates
- **Basic Configuration**: Standard settings for general use
- **High Performance**: Optimized for real-time monitoring
- **Custom Templates**: Load and save custom configurations

## 🔒 Security Features

- **File Validation**: Whitelist of allowed file extensions
- **Size Limits**: 100MB maximum file size
- **Secure Filenames**: Sanitized file naming
- **Path Validation**: Prevents directory traversal

## 🚀 Production Deployment

For production use, consider:

```bash
# Use a production WSGI server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or use uWSGI
uwsgi --http :5000 --module app:app --processes 4
```

### Environment Variables
```bash
export FLASK_ENV=production
export REDFISH_MRD_SECRET_KEY=your-secret-key-here
export MAX_CONTENT_LENGTH=104857600  # 100MB
```

## 📊 Supported Configurations

### Metric Types
- ✅ **Platform Metrics**: System health, power state, boot progress
- ✅ **Environment Metrics**: Temperature, fans, thermal management
- ✅ **Processor Metrics**: CPU utilization, performance, frequency
- ✅ **Memory Metrics**: DIMM status, errors, capacity
- ✅ **Alarm Metrics**: Critical alerts, fault conditions
- ✅ **Counter Metrics**: Network statistics, performance counters

### File Formats
- ✅ **TGZ**: Compressed TAR archives
- ✅ **ZIP**: ZIP archives  
- ✅ **TAR.GZ**: GZIP compressed TAR files

### Schema Compliance
- ✅ **Redfish v1.3.0**: MetricReportDefinition schema
- ✅ **Validation**: Automatic schema validation
- ✅ **Standards**: DMTF Redfish compliance

## 🛠️ Development

### Local Development
```bash
# Enable debug mode
export FLASK_DEBUG=1

# Run development server
python3 app.py
```

### Adding Features
1. **New Templates**: Add HTML templates in `templates/`
2. **API Endpoints**: Add routes in `app.py`
3. **Static Assets**: Add CSS/JS in `static/` (if needed)
4. **Configuration**: Extend configuration options

## 📋 Troubleshooting

### Common Issues

**"No module named flask"**
```bash
pip3 install flask
```

**"File too large"**
- Check MAX_CONTENT_LENGTH setting (default: 100MB)
- Compress mockup files before upload

**"Permission denied"**
```bash
# Ensure directories are writable
chmod 755 uploads/ web_output/
```

### Debug Mode
Enable debug mode for detailed error messages:
```bash
export FLASK_DEBUG=1
python3 app.py
```

## 🎉 Success!

Your Redfish Telemetry MRD Developer web interface is now ready to use! The modern, intuitive interface makes it easy to:

- Upload and analyze Redfish mockup data
- Configure MRD generation settings  
- Generate schema-compliant v1.3.0 MRDs
- Download and deploy your MRD files

Visit http://localhost:5000 to get started!