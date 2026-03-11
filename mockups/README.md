# Mockup Files

This directory is where you place Redfish mockup files for processing.

## Supported Formats

- **Directory**: An uncompressed Redfish mockup directory containing `redfish/v1/` structure
- **`.tgz` archive**: A compressed tar archive of a mockup directory
- **`.zip` archive**: A zip archive of a mockup directory

## Getting Public Mockup Files

The DMTF provides official public Redfish mockup files for testing:

- **DMTF Redfish Mockup Creator**: https://github.com/DMTF/Redfish-Mockup-Creator  
  Generate mockups from live Redfish endpoints.

- **DMTF Redfish Mockup Server**: https://github.com/DMTF/Redfish-Mockup-Server  
  Includes sample mockup files you can use directly.

- **DMTF Redfish Tools**: https://github.com/DMTF/Redfish-Tools  
  Additional sample data and schemas.

- **OpenBMC**: https://github.com/openbmc/openbmc  
  OpenBMC firmware includes Redfish endpoints you can capture mockups from.

## Usage

```bash
# Analyze a mockup
python3 mrd_tool.py analyze -m mockups/your_mockup.tgz

# Generate MRDs from a mockup
python3 mrd_tool.py generate -m mockups/your_mockup.tgz
```

## Notes

- Mockup files are listed in `.gitignore` — your hardware data stays private
- The tool supports any Redfish v1.x compliant mockup
