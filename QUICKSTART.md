# Quick Start Guide

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/harira-microsoft/redfish-telemetry-mrd-developer.git
   cd redfish-telemetry-mrd-developer
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Quick Test

```bash
# Test CLI
python3 mrd_tool.py --help

# Test web interface
python3 app.py
# Open http://localhost:5000 in your browser
```

## First MRD Generation

```bash
# Analyze sample mockup
python3 mrd_tool.py analyze -m mockups/your_mockup.tgz

# Generate MRDs
python3 mrd_tool.py generate -m mockups/your_mockup.tgz

# Check outputs
ls output/
```

## Web Interface

1. Start the web server:
   ```bash
   python3 app.py
   ```

2. Open http://localhost:5000 in your browser

3. Upload a mockup file and follow the guided workflow

## Documentation

- CLI help: `python3 mrd_tool.py examples`
- Web documentation: Available at http://localhost:5000/docs
- Detailed guides: See `docs/` directory

## Need Help?

- Check the [documentation](docs/)
- Read the [Contributing Guide](CONTRIBUTING.md)
- Open an [issue](https://github.com/harira-microsoft/redfish-telemetry-mrd-developer/issues)