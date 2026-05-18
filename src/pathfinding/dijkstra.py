from ..map.network import Network, Hub


ZONE_COST = {"priority": 1, "normal": 1, "restricted": 2}
ZONE_PRIORITY = {"priority": 0, "normal": 1, "restricted": 2}

def dijkstra(net: Network) -> list[Hub]:
    '''Dijkstra Algorithm to return each Drone's best path'''
    assert net.start is not None
    heap = [(0, net.start)]
    visited: set[Hub] = set()      # closed list
    path: list[Hub] = [net.start] # open list

    while queue:
        if len(queue) > 1:
            current = queue.pop()
            q = best_neighbour(current)
        current: Hub = queue.pop()
        if current is net.end:
            path = get_path(visited)
            return path


def best_neighbour(current: Hub) -> Hub:
    '''Use zone_cost to find best neighbours'''
    ...


def get_path(visited: set) -> set[Hub]:
    ...


def print_statistic() -> None:
    '''Print statistics for efficiency tracking'''
    ...
