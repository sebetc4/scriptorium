"""The capture writes into the repository's library/, wherever it lives."""
import fetch


def test_fetch_points_at_library(repo):
    assert fetch.LIBRARY == repo / "library"
    assert fetch.ROOT == repo
