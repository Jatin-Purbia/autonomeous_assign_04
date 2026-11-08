"""Keep E2E artifacts inside the project with inherited Windows permissions."""
from pathlib import Path
from uuid import uuid4
import pytest


@pytest.fixture
def tmp_path():
    # Explicitly use inherited ACLs: mode=0700 temp directories are inaccessible
    # to restricted execution tokens on some Windows course/lab machines.
    target=Path(__file__).resolve().parents[1]/'tmp'/'test_artifacts'/uuid4().hex
    target.mkdir(parents=True)
    return target
