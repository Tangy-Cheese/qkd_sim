# QKD

QKD project

## Development Setup (us two)

### Clone the repository

```bash
git clone https://github.com/Tangy-Cheese/QKD.git
cd QKD/
```

### Install in editable mode (with test dependencies)

```bash
pip install -e .[test]
```

### To run tests

```bash
pytest
```

Obv we will change these instructions later for users. But ``-e``means pip installation in editor mode,
so it will link to src/ directory in this project. So any updates we make to the source code automatically links.
The ``.[test]`` imports all the project dependencies from pyproject.toml and also the ``[test]`` dependencies for now which
is just pytest.
