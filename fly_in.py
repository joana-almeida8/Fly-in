import sys
from src.parse.raw_parser import raw_parser
from src.map.network import Network
from src.pathfinding.algorithm import dijkstra


def fly_in() -> None:
    # Args check
    if len(sys.argv) < 2:
        print("Missing config file argument")
    elif len(sys.argv) > 2:
        print("Too many arguments")

    # Parser
    try:
        data = raw_parser(sys.argv[1])
    except (ValueError, KeyError, TypeError, FileNotFoundError) as error:
        print(f"\nParsing error(s) detected:\n{error}\n")
        sys.exit(1)

    # Structure parsed_data
    try:
        network = Network.sort_data(data)
    except ValueError as error:
        print(f"{error}")
        sys.exit(1)

    # Execute algorithm
    path = dijkstra(network)

    # Display graphics

    # Export file


if __name__ == "__main__":
    fly_in()
