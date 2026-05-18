from typing import Any, Optional
from itertools import chain


class Hub():
    '''Sort hub data, including start and end'''
    def __init__(self, raw_hub: dict):
        '''Instantiate each data element of Hub'''
        self.name: str = raw_hub['name']
        self.coords: tuple = raw_hub['coordinates']
        self.zone: str = raw_hub['zone']
        self.colour: str = raw_hub['color']
        self.max_drones: int = raw_hub['max_drones']
        self.neighbours: list[Hub] = []


class Connection():
    '''Instatiate each connection'''
    def __init__(self, raw_con: dict):
        '''Instantiate each data element of Hub'''
        self.name: str = raw_con['name']
        self.max_link: int = raw_con['max_link_capacity']


class Drone():
    def __init__(self, identifier: int, start: Hub):
        self.id = f"D{identifier}"
        self.current_hub = start
        self.path = []
        self.in_transit = False
        self.transit_connection = None
        self.turns_in_transit = 0


class Network():
    def __init__(self) -> None:
        '''Initiate each graph element'''
        self.nb_drones: Optional[int] = None
        self.start: Optional[Hub] = None
        self.end: Optional[Hub] = None
        self.hubs: list[Hub] = []
        self.connections: list[Connection] = []
        self.drones: Optional[list[Hub]] = None

    @classmethod
    def sort_data(cls, parsed_data: dict[str, Any]) -> 'Network':
        '''Transform parsed_data into workable data'''
        network = cls()

        # Add workable data to the network
        network.nb_drones = parsed_data['nb_drones']
        network.start = Hub(parsed_data['start_hub'])
        network.end = Hub(parsed_data['end_hub'])
        for hub in parsed_data.get('hub', []):
            network.hubs.append(Hub(hub))
        for connection in parsed_data.get('connection', []):
            network.connections.append(Connection(connection))
        assert network.nb_drones is not None
        network.drones = [Drone(i+1, network.start)
                          for i in range(network.nb_drones)]

        # Fill neighbours lists for each hub
        network._get_neighbours()

        # Valid path check
        if not network._is_viable():
            raise ValueError("No viable path from start to end")

        return network

    def _get_neighbours(self) -> None:
        '''Get hub neighbours from each Connection'''
        assert self.start is not None
        assert self.end is not None

        all_hubs: list[Hub] = list(chain(self.hubs, [self.start], [self.end]))
        for con in self.connections:
            parts = con.name.split("-")
            hub_a: Hub = next(filter(lambda n: n.name == parts[0], all_hubs))
            hub_b: Hub = next(filter(lambda n: n.name == parts[1], all_hubs))
            if hub_b.zone != 'blocked':
                hub_a.neighbours.append(hub_b)
            if hub_a.zone != 'blocked':
                hub_b.neighbours.append(hub_a)

    def _is_viable(self) -> bool:
        '''Check viable path with Depth-First Search (DFS)'''
        assert self.start is not None
        assert self.end is not None

        visited: set[Hub] = set()
        queue: list[Hub] = [self.start]
        while queue:
            current = queue.pop()
            if current is self.end:
                return True
            if current in visited:
                continue
            visited.add(current)
            queue.extend(current.neighbours)
        return False
