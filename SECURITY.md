# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes     |

## Reporting a Vulnerability

Please **do not** report security vulnerabilities via GitHub Issues.

Instead, report them privately using one of these methods:

- **GitHub Private Vulnerability Reporting**: Use the [Security tab](https://github.com/harira-microsoft/redfish-telemetry-mrd-developer/security/advisories/new) in this repository (preferred)
- **Email**: Open a GitHub issue requesting a private contact channel

### What to include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if known)

### Response timeline

- **Acknowledgement**: Within 48 hours
- **Initial assessment**: Within 7 days
- **Fix and disclosure**: Coordinated with reporter

## Scope

This tool processes locally-supplied Redfish mockup files and generates JSON output files. It does not make network connections to BMC hardware. The primary security considerations are:

- Flask web server exposure (run only on trusted networks or localhost)
- File upload handling (`werkzeug` secure filename, size limits enforced)
- Temporary file cleanup after processing

## Security Best Practices

- Always set `REDFISH_MRD_SECRET_KEY` as an environment variable before running the web UI
- Do not expose the web interface (`app.py`) on a public network interface
- Only upload mockup files from trusted sources
