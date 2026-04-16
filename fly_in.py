import sys
from pydantic import ValidationError
from parser import parser


def fly_in() -> None:
    # Args check
    if len(sys.argv) < 2:
            print("Missing config file argument")
    elif len(sys.argv) > 2:
        print("Too many arguments")

    try:
        # Parser
        data = parser()
    except ValueError as error:
         print(f"Something went wrong:\n{error}")


if __name__ == "__main__":
    fly_in()
