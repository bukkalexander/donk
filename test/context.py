from pathlib import Path

PROJECT_DIR_PATH = Path(__file__).resolve().parent.parent
TEST_DIR_PATH = PROJECT_DIR_PATH / "test"
DATA_DIR_PATH = TEST_DIR_PATH / "data"
SIMPLE_DATASET_PATH = DATA_DIR_PATH / "simple"
WORKSPACE_ROOT_PATH = PROJECT_DIR_PATH / ".pytest-workspaces"
