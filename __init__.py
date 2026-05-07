from .lib.data_manager import ensure_data_dir
from .lib import handlers  # noqa: F401

ensure_data_dir()

__all__ = ["handlers"]