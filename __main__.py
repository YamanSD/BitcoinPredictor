from __future__ import annotations

import asyncio
from os import name as os_name

# Enable ANSI support on Windows & apply asyncio patches
if os_name == 'nt':
    try:
        from colorama import just_fix_windows_console
    except ImportError:
        def just_fix_windows_console() -> None:
            return

    just_fix_windows_console()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from Server import start


def main() -> None:
    start()


if __name__ == '__main__':
    main() # TODO fix observation gap every 4 minutes.
