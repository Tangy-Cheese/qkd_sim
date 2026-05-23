# Quantum Communication Networks

Website which displays how various quantum communication protocols can interact.

## Development Setup

```bash
git clone https://github.com/Tangy-Cheese/QKD.git
cd QKD/

# Create a python virtual environment
python -m venv .venv

# MacOS/Linux
source /.venv/bin/activate

# Windows
.venv\Scripts\activate

# Intall package dependencies
pip install -e .[test]
```

`-e` installs in editable mode, linking to `src/` so source changes reflect immediately. `.[test]` pulls project dependencies plus pytest.

### Tests

```bash
pytest
```

## Backend (FastAPI)

### Requirements

```bash
pip install fastapi uvicorn
```

### Running

From project root:

```bash
cd backend
uvicorn main:app --reload
```

Server is up when you see `uvicorn running on http://127.0.0.1:8000`.

Interactive API docs: `http://localhost:8000/docs`

> [!IMPORTANT]
> To stop the server, use `Ctrl + C` in the same terminal. Do not close the terminal window.

## Frontend (React)

### Requirements

- Node.js >= 22
- npm (or pnpm / yarn)

### Running

```bash
cd frontend
npm ci
npm run dev
```
