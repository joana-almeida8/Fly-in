""" The input file must respect the expected structure and syntax:
• Each zone must have a unique name and valid integer coordinates.
• Connections must link only previously defined zones using connection: <zone1>-<zone2>
[metadata].
• The same connection must not appear more than once (e.g., a-b and b-a are considered duplicates).
• Any metadata block (e.g., [zone=... color=...] for zones, [max_link_capacity=...]
for connections) must be syntactically valid.
• Any other parsing error must stop the program and return a clear error message
indicating the line and cause. """

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
                raise ValueError(f"Formatting error on line '{line}'")
            key, val = line.split(':', 1)
            key = key.lower()

            # nb_drones 
            if not parsed_data:
                if key != "nb_drones":
                    raise ValueError("Input file must start with 'nb_drones'")
                value = int(val.strip())
                if not value:
                    raise ValueError(f"{key} value must be an integer")
                parsed_data[key] = value

            # Send all valid keys to pydantic class for validation
            valid_keys = ["start_hub", "end_hub", "hub", "connection"]
            pydantic_errors = {}
            invalid_keys = []
            if key in valid_keys:
                # There can only be one start and end hubs
                if key == "start_hub":
                    if "start_hub" in parsed_data.keys():
                        raise KeyError(f"There can only be one {key}")
                if key == "end_hub":
                    if "end_hub" in parsed_data.keys():
                        raise KeyError(f"There can only be one {key}")

                try:
                    # Send lines with valid keys to pydantic validation
                    data = LineParser(line)

                # Append all errors from pydantic validation to a list 
                except ValidationError as e:
                    value_errors = []
                    for error in e.errors():
                        if "Value error" in error['msg']:
                            noise, msg = error['msg'].split(", ")
                            error['msg'] = msg
                        value_errors.append(error)
                    pydantic_errors['key'] = value_errors

            # Append invalid keys errors to invalid_kerrors
            else:
                invalid_keys.append(key)
            if invalid_keys:
                invalid_kerrors = f"Invalid key(s): {", ".join(invalid_keys)}"

            # Raise any errors from pydantic validation 
            if pydantic_errors:
                e_msgs = []
                for error_dict in pydantic_errors:
                    for e_key, e_vals in error_dict:
                        e_values = f"{', '.join(v for v in e_vals)}"
                        e_msgs.append(f"{e_key}: {e_values}")
                all_pyd_errors = f"{"\n".join(e_msgs)}"
                if invalid_keys:
                    all_pyd_errors = f"{all_pyd_errors}\n{invalid_kerrors}"
                raise ValueError(f"{all_pyd_errors}")

            # Add existing metadata to metadata dict
            metadata = {}
            metas = Metas(line)
            if data.metadata:
                if metas.zone:
                    metadata['zone'] = metas.zone
                if metas.color:
                    metadata['color'] = metas.color
                if metas.color:
                    metadata['max_drones'] = metas.max_drones
                if metas.color:
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
                parsed_data[key].append(
                    {
                        'name': data.name,
                        'coordinates': (data.x, data.y),
                        'metadata': metadata
                    }
                )

    # Start and end hubs must be different
    if parsed_data['start_hub'] == parsed_data['end_hub']:
        raise ValueError("start and end hubs cannot have the same coordinates")

    # All required keys must have been parsed through
    required_keys = ()
    missing = required_keys - set(parsed_data.keys())
    if missing:
        raise KeyError(f"Missing required configs: '{', '.join(missing)}")

    # Names cannot be repeated
    names = [n['name'] for n in parsed_data['connection'] + parsed_data['hub']]
    names.append(parsed_data['start']['name'],
                 parsed_data['end']['name'])
    if len(names) != set(names):
        raise ValueError("Hubs and Connections cannot have repeated names")
    
    # Coordinates cannot be repeated
    coords = [c['coordinates'] for c in parsed_data['hub']]
    coords.append(parsed_data['start']['coordinates'],
                  parsed_data['end']['coordinates'])
    if len(coords) != set(coords):
        raise ValueError("Hubs cannot have repeated coordinates")


    # Connection names must have known hub names
    # The same connection must not appear more than once (e.g., a-b and b-a are considered duplicates)

    return parsed_data
