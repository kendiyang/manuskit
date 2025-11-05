# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Manuskit is a Python-based browser automation toolkit leveraging Steel SDK, browser-use, and CDP (Chrome DevTools Protocol). The project is in early development stages.

## Environment Setup

### Prerequisites
- Python 3.12+
- Virtual environment at `venv/`

### Installation
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies (once requirements.txt is created)
pip install -r requirements.txt
```

### Environment Variables
Copy `.env.example` to `.env` and configure:
- `STEEL_API_KEY`: Required for Steel browser automation API
- `STEEL_BASE_URL`: Optional custom Steel API endpoint (format: `http://IP:PORT`)
- `DOMAIN`: Application domain (default: `http://localhost:3000`)
- `PORT`: Server port (default: `8080`)
- `HOST`: Server host (default: `0.0.0.0`)

**Important**: Never commit `.env` files or tokens. The repository is configured to ignore `tokens/` directory and `*_tokens.json` files.

## Key Dependencies

- **steel-sdk** (0.13.0): Browser automation via Steel API
- **browser-use** (0.9.5): Browser automation utilities
- **cdp-use** (1.4.3): Chrome DevTools Protocol integration
- **anthropic** (0.72.0): Claude AI integration
- **google-genai** (1.48.0): Google Generative AI
- **playwright**: Browser automation framework
- **aiohttp**: Async HTTP client/server

## Development Commands

### Python Virtual Environment
```bash
# Activate environment
source venv/bin/activate

# Deactivate environment
deactivate

# Freeze current dependencies
pip freeze > requirements.txt
```

### Running Tests
```bash
# Once test framework is established
pytest

# Run specific test
pytest tests/test_module.py

# Run with coverage
pytest --cov=src tests/
```

### Code Quality
```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy .
```

## Architecture Notes

### Browser Automation Strategy
The project uses a multi-layered approach to browser automation:
1. **Steel SDK**: Primary browser automation service with API-based control
2. **CDP-use**: Direct Chrome DevTools Protocol access for low-level control
3. **browser-use**: High-level browser utilities and helpers

### Security Considerations
- OAuth tokens must be stored in `tokens/` directory (gitignored)
- All credentials should be in `.env` files (never committed)
- Steel API keys should be stored securely and rotated regularly

## Project Status

This is an early-stage project. As the codebase develops, update this file with:
- Actual entry points and main modules
- Testing framework and test commands
- Build/deployment procedures
- Architecture patterns and design decisions
- Common development workflows
