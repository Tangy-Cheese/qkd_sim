from visitors import VisitorCounter


def test_starts_at_zero(tmp_path):
    assert VisitorCounter(tmp_path / "visits.json").count() == 0


def test_increment_is_saved(tmp_path):
    path = tmp_path / "data" / "visits.json"
    counter = VisitorCounter(path)

    assert counter.increment() == 1
    assert counter.increment() == 2

    # a new counter on the same file, like uvicorn restarting, keeps the total
    assert VisitorCounter(path).count() == 2


def test_corrupt_file_counts_from_zero(tmp_path):
    path = tmp_path / "visits.json"
    path.write_text("not json")

    assert VisitorCounter(path).increment() == 1
