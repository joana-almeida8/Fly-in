from itertools import chain


def post_validation(parsed_data: dict) -> None:
    '''Post-validate parsed dict'''

    # All required keys must have been parsed through
    required_keys = ("nb_drones", "start_hub", "end_hub", "connection", "hub")
    missing = set(required_keys) - set(parsed_data.keys())
    if missing:
        raise ValueError("[ERROR] Missing required configs: "
                         f"'{', '.join(missing)}'")

    # List every dict instruction in parsed_data together for post-validations
    post_errors = []
    connection_items = parsed_data.get('connection', [])
    hub_items = list(chain(
        [parsed_data[item] for item in ["start_hub", "end_hub"]
          if item in parsed_data],
        parsed_data.get("hub", [])
    ))

    # Coordinates cannot be repeated
    checked_coords = {}
    for item in hub_items:
        coord = item['coordinates']
        line = item['line']
        if coord in checked_coords:
            post_errors.append((line, f"Coordinates '{coord}' already defined "
                               f"at Line {checked_coords[coord]}"))
        else:
            checked_coords[coord] = line

    # Names cannot be repeated
    checked_names = {}
    for item in chain(hub_items, connection_items):
        name = item['name']
        line = item['line']
        if name in checked_names:
            post_errors.append((line, f"Name '{name}' already defined at "
                               f"Line {checked_names[name]}"))
        else:
            checked_names[name] = line

    # Connection names must have known hub names
    sorted_connections = {}
    required_connections = set()
    hub_names = {
        *[n['name'] for n in hub_items],
        parsed_data.get('start_hub', {}).get('name'),
        parsed_data.get('end_hub', {}).get('name')
    }

    for item in connection_items:
        name = item['name']
        line = item['line']
        parts = name.split("-")
        for p in parts:
            if p not in hub_names:
                post_errors.append((line, f"Connection '{name}' "
                                   f"references unknown hub '{p}'"))
            if p == parsed_data['start_hub']['name']:
                required_connections.add("start")
            if p == parsed_data['end_hub']['name']:
                required_connections.add("end")

        # Connections cannot be repeated
        pair = tuple(sorted(parts))
        if pair in sorted_connections:
            post_errors.append((line, f"Connection '{name}' is a duplicate of "
                               f"the one at Line {sorted_connections[pair]}"))
        else:
            sorted_connections[pair] = line

    # Start and end hubs must be connected
    if "start" not in required_connections:
        name = parsed_data['start_hub']['name']
        line = parsed_data['start_hub']['line']
        post_errors.append((line, f"Start hub '{name}' must be connected"))
    if "end" not in required_connections:
        name = parsed_data['end_hub']['name']
        line = parsed_data['end_hub']['line']
        post_errors.append((line, f"End hub '{name}' must be connected"))

    # Raise post pydantic errors
    if post_errors:
        post_errors.sort()
        post_error_msgs = [f" - Line {l_count}: {msg}"
                           for l_count, msg in post_errors]
        formatted_post_errors = '\n'.join(post_error_msgs)
        raise ValueError(f"{formatted_post_errors}")
