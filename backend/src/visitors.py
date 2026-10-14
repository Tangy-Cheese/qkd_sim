import json
import os
import threading
from pathlib import Path

#Where the visitor count is kept between server restarts. Set QKDSIM_VISITS_FILE to keep it somewhere else
DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "visits.json"


class VisitorCounter:
    """
    Counts visits to the site and saves the total to a JSON file, so restarting uvicorn does not reset it.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.lock = threading.Lock() #FastAPI runs plain def routes in a thread pool, so two visits can arrive at once

    def read(self) -> int:
        try:
            return int(json.loads(self.path.read_text())["count"])
        except (FileNotFoundError, KeyError, ValueError):
            return 0

    def count(self) -> int:
        with self.lock:
            return self.read()

    def increment(self) -> int:
        with self.lock:
            count = self.read() + 1
            self.path.parent.mkdir(parents=True, exist_ok=True)

            #write to a temporary file first so a crash mid write cannot wipe the count
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps({"count": count}))
            tmp.replace(self.path)

            return count


counter = VisitorCounter(Path(os.environ.get("QKDSIM_VISITS_FILE", DEFAULT_PATH)))
