import sys
from parser.pydantic import ValidationError
from parser.parser import parser


def fly_in() -> None:
    # Args check
    if len(sys.argv) < 2:
            print("Missing config file argument")
    elif len(sys.argv) > 2:
        print("Too many arguments")

    try:
        # Parser
        data = parser()
    except (ValueError, KeyError, TypeError, FileNotFoundError) as error:
         print(f"Something went wrong:\n{error}")


if __name__ == "__main__":
    fly_in()
