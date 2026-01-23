import sys
from ui.ui import gui_main
from ui.cli import cli_main

def main():
    if len(sys.argv) > 1:
        cli_main()
    else:
        gui_main()

if __name__ == "__main__":
    main()
