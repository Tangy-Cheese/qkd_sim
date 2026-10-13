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
cd backend/src
python -m uvicorn main:app --reload
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

Open `http://localhost:5173`. Start the backend first: the frontend sends its requests to `/api`, which the Vite dev server forwards to `http://127.0.0.1:8000`. The sidebar shows whether the backend is reachable.

To use a backend running somewhere else, set `VITE_API_URL` (e.g. `VITE_API_URL=http://localhost:9000 npm run dev`) and add the frontend's address to `allow_origins` in `backend/src/main.py`.
