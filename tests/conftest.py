import os
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def models_dir(tmp_path_factory):
    """Copy the reference models to a temp dir so nothing is written into models/."""
    target = tmp_path_factory.mktemp("models")
    shutil.copytree(ROOT / "tests" / "models_ref", target, dirs_exist_ok=True)
    os.environ["CAD_MODELS_DIR"] = str(target)
    import cadstudio.config as config

    config.MODELS_DIR = target
    return target
