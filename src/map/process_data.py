from .connections import Connections
from .hubs import Hubs
from typing import Any


class ProcessData():
    '''Process parsed_data and initiate each type'''

    def process_all(self, data: dict[str, Any]) -> None:
        for k, v in data:
            if k == "connection":
                for c in v:
                    Connections().add_connection(c)
            if k == "hub":
                for c in v:
                    Hubs().add_hub(c)
