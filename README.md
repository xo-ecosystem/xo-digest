# XO Core

A modular foundation for XO projects, providing core functionality and utilities.

## Project Structure

```
xo-core/
├── src/
│   └── xo_core/
│       ├── core/       # Core functionality
│       ├── cli/        # Command-line interface
│       ├── utils/      # Utility functions
│       ├── models/     # Data models
│       └── services/   # Service integrations
├── tests/             # Test suite
├── 3d_printables/     # 3D printable models
│   ├── stl/          # STL files
│   ├── step/         # STEP files
│   └── blend/        # Blender files
└── docs/             # Documentation
```

## Development Setup

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

3. Run tests:
```bash
tox
```

## Features

- Modular architecture
- Comprehensive test suite
- CLI interface
- 3D printable models support
- Service integrations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License