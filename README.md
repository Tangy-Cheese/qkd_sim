# Quantum Communication Networks

Website which displays how various quantum communication protocols can interact.

## What is this?

QKDSim is a simulator for quantum key distribution (QKD): ways for two parties to agree on a secret key using single photons, such that anyone listening in on the line disturbs the photons and gives themselves away. A Python backend runs the simulations and a React frontend, styled like a 90s home page, lets you set them up and see the results.

### What you can do

- **BB84 over a single fibre.** Choose the number of qubits Alice sends, the fibre length and its attenuation, and optionally put an eavesdropper (Eve) on the line. The simulation models photon loss, detector dark counts, basis sifting, error correction and privacy amplification, and reports the qubit error rate (QBER), the secure key rate and the final secure key. If the error rate is too high for any secure key to be left, the run is aborted.
- **Networks of trusted nodes.** Build a network of nodes joined by fibre links, each with its own length, attenuation and optional eavesdropper. The simulator finds the lowest loss route between a sender and a receiver with Dijkstra's algorithm, runs BB84 over every link on that route and relays the key hop by hop, XOR-encrypting it with each link's key. The route is drawn on a map with the error rate of each link.

### Current state

This is a working prototype.

| Part | Status |
| --- | --- |
| BB84 protocol | Working |
| Multi-node network simulation | Working (BB84 on every link) |
| E91 protocol | Not implemented yet. The page exists, but the backend answers `501 Not Implemented` |

Some simplifications to be aware of:

- Error correction and privacy amplification are not carried out bit by bit. The key is shortened to the length those steps would leave.
- Intermediate nodes in a network are trusted: each one sees the key it relays.
- Every node in a network shares one dark count rate.
- Results are random, so two runs with the same settings give slightly different numbers.

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
