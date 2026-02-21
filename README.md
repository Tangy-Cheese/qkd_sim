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
is just pytest. Also there will be a tonne of artefacts from pip installing. Honestly not sure why or what a lot of them do
but just ignore all of them, they are all in the **.gitignore** so they wont be tracked by git anyway.

## Backend (FastAPI)

### To run the Backend Server

From the project root:

Install fastapi and uvicorn first on your venv or wherever:

```bash
pip install fastapi uvicorn
```

then

```bash
cd backend
uvicorn main:app --reload #uvicorn server host takes place at localhost:8000
```

the backend server is running if you see:

```bash
uvicorn running on http://127.0.0.1:8000
```

To interact with fastapi documentation and feed json data manually to see if it works enter this link:

```bash
http://localhost:8000/docs
```

> [!IMPORTANT]
> To close the server, DON'T close the terminal. Had to spend ages fixing it when trying to rerun the server.
> In the same terminal, exit using `ctrl + C`!

## Frontend (React)

## Requirements
- Node.js >= 22
- npm (or pnpm / yarn)

### Running the Frontend Page

```bash
cd frontend
npm install
npm run dev
```