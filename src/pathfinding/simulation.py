from ..map.network import Network, Hub
from .dijkstra import dijkstra
from .scheduler import scheduler


class Drone():
    '''Instatiate each drone'''
    def __init__(self, identifier: int, start: Hub):
        '''Initiate each data element of Drone'''
        self.id: str = f"D{identifier}"
        self.current_hub: Hub = start
        self.path: list[Hub] = []
        self.in_transit: bool = False
        self.transit_connection: bool = None
        self.nb_turns: int = 0


def run_simulation(network: Network) -> None:
    '''Manage drone movements with dijkstra and scheduler'''
    assert network.nb_drones is not None
    drones = [Drone(i+1, network.start) for i in range(network.nb_drones)]

    for drone in drones:
        drone.path = dijkstra(network, drone)

    return scheduler(network, drones)
