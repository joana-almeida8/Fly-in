import sys
from pydantic import ValidationError
from .pydantics import LineParser, Metas


def raw_parser() -> dict[str, str]:
    '''Parse through each line in input and return structured dict with data'''

    # Get raw_data from the input file
    config_file = sys.argv[1]
    if not config_file.endswith(".txt"):
        raise FileNotFoundError(f"Input file '{config_file}' "
                                "must have .txt format")

    parsed_data = {}
    invalid_keys = []
    pydantic_errors = {}
    with open(config_file, 'r') as file:
        line_count = 0
        for line in file:
            # Count line for error reference
            line_count += 1

            # Ignore empty or comment lines
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Split keys and values by ':'
            if ':' not in line:
                raise ValueError(f"Formatting error on line {line_count}: '{line}'")
            key, val = line.split(':', 1)
            key = key.lower()

            # nb_drones must be added first
            if not parsed_data:
                if key != "nb_drones":
                    raise ValueError("Input file must start with 'nb_drones'")
                value = int(val.strip())
                if value is None:
                    raise ValueError(f"{key} value must be an integer")
                parsed_data[key] = value
                continue

            # Append all invalid keys
            valid_keys = ["start_hub", "end_hub", "hub", "connection"]
            if key not in valid_keys:
                if not invalid_keys:
                    invalid_keys.append("\nUnknown instructions detected:")
                invalid_keys.append(f" - [Line {line_count}]: '{key}'")
                continue

            # There can only be one start and end hub
            if key in ["start_hub", "end_hub"] and key in parsed_data:
                raise KeyError(f"[Line {line_count}]: "
                               f"There can only be one '{key}'")

            try:
                # Send lines with valid keys to pydantic validation
                data = LineParser(line)

                # Add existing metadata to metadata dict
                metadata = {}
                metas = Metas(line)
                if data.metadata:
                    if metas.zone:
                        metadata['zone'] = metas.zone
                    if metas.color:
                        metadata['color'] = metas.color
                    if metas.max_drones:
                        metadata['max_drones'] = metas.max_drones
                    if metas.max_link_capacity:
                        metadata['max_link_capacity'] = metas.max_link_capacity

                # Add start and end hubs to parsed_data
                if key == "start_hub" or key == "end_hub":
                    parsed_data[key] = {
                        'name': data.name,
                        'coordinates': (data.x, data.y),
                        'metadata': metadata
                    }
                # Add hubs and connections to parsed_data
                else:
                    # Add hub and connection structure to parsed data
                    if (key == "hub" and key not in parsed_data) or \
                        (key == "connection" and key not in parsed_data):
                        parsed_data.setdefault(key, []).append(parsed_data)
                    
                    # Append hub info
                    if key == "hub":
                        parsed_data[key].append(
                            {
                                'name': data.name,
                                'coordinates': (data.x, data.y),
                                'metadata': metadata
                            }
                        )
                    # Append connection info
                    elif key == "connection":
                        parsed_data[key].append(
                            {
                                'name': data.name,
                                'metadata': metadata
                            }
                        )

            # Append all errors from pydantic validation to a list 
            except ValidationError as e:
                value_errors = []
                for error in e.errors():
                    if "Value error" in error['msg']:
                        value_errors.append("Parsing error detected:")
                        noise, msg = error['msg'].split(", ")
                        error['msg'] = f" - [Line {line_count}]: {msg}"
                    error['msg'] = f" - [Line {line_count}]: {msg}"
                    value_errors.append(error['msg'])
                    pydantic_errors['key'] = value_errors

    # Raise any errors from pydantic validation 
    if pydantic_errors or invalid_keys:
        error_msgs = []
        for e_key, e_vals in pydantic_errors.items():
            e_values = f"{'\n'.join(v for v in e_vals)}"
            error_msgs.append(f"{e_key}:\n{e_values}")
        all_pyd_errors = f"{"\n".join(error_msgs)}"
        if invalid_keys:
            all_pyd_errors = f"{all_pyd_errors}\n\n{"\n".join(invalid_keys)}"
        raise ValueError(f"{all_pyd_errors}")

    # All required keys must have been parsed through
    required_keys = ("nb_drones", "start_hub", "end_hub", "connection", "hub")
    missing = required_keys - set(parsed_data.keys())
    if missing:
        raise KeyError(f"Missing required configs: '{', '.join(missing)}")

    # Names cannot be repeated
    con_names = [n['name'] for n in parsed_data.get('connection', [])]
    hub_names = [n['name'] for n in parsed_data.get('hub', [])] + \
                [parsed_data['start']['name'], parsed_data['end']['name']]
    all_names = con_names + hub_names
    if len(all_names) != len(set(all_names)):
        raise ValueError("Hubs and Connections cannot have repeated names")

    # Coordinates cannot be repeated
    coords = [c['coordinates'] for c in parsed_data.get('hub', [])] + \
             [parsed_data['start_hub']['coordinates'],
              parsed_data['end_hub']['coordinates']]
    if len(coords) != len(set(coords)):
        raise ValueError("Hubs cannot have repeated coordinates")

    # Connection names must have known hub names
    sorted_names = set()
    for name in con_names:
        parts = name.split("-")
        if not all(n in hub_names for n in parts):
            raise ValueError(f"Connection {name} references unknown hub")

        # The same connection must not appear more than once
        pair = tuple(sorted(parts))
        if pair in sorted_names:
            raise ValueError(f"There cannot be duplicate connections: {name}")
        sorted_names.add(pair)

    return parsed_data
