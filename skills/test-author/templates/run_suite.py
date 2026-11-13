"""Copy alongside runtime.py into the exported immutable suite."""

import sys

sys.dont_write_bytecode = True

from runtime import main


if __name__ == "__main__":
    raise SystemExit(main())
