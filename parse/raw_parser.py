from pydantic import ValidationError
from .pydantics import LineParser


def raw_parser(config_file: str) -> dict[str, str]:
    '''Parse through each line in input and return structured dict with data'''

    # Get raw_data from the input file
    if not config_file.endswith(".txt"):
        raise FileNotFoundError(f" - Input file '{config_file}' "
                                "must have .txt format")

    parsed_data = {}
    invalid_keys = []
    pydantic_errors = []
    nb_drones_msg = False
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
                pydantic_errors.append((line_count, "Invalid format, "
                                       "missing ':'"))
                continue

            key, val = line.split(':', 1)
            key = key.lower()

            # nb_drones must be added first
            if "nb_drones" not in parsed_data:
                if key != "nb_drones" and not nb_drones_msg:
                    pydantic_errors.append((line_count, "Input file must "
                                           "start with 'nb_drones'"))
                    nb_drones_msg = True
                if key == "nb_drones":
                    try:
                        value = int(val.strip())
                        parsed_data[key] = value
                    except ValueError:
                        pydantic_errors.append((line_count, f"'{key}' value "
                                               "must be an integer"))
                    continue

            # Append all invalid keys
            valid_keys = ["start_hub", "end_hub", "hub", "connection"]
            if key not in valid_keys:
                if not invalid_keys:
                    invalid_keys.append("\nUnknown instructions detected:")
                invalid_keys.append(f" - Line {line_count}: '{key}'")
                continue

            # There can only be one start and end hub
            if key in ["start_hub", "end_hub"] and key in parsed_data:
                invalid_keys.append(f" - Line {line_count}: "
                                    f"There can only be one '{key}'")

            try:
                # Send lines with valid keys to pydantic validation
                data = LineParser.model_validate(line)

                # Add existing metadata to metadata dict
                metadata = {}
                if data.metadata:
                    metadata = data.metadata.model_dump(exclude_unset=True)

                # Add start and end hubs to parsed_data
                if key == "start_hub" or key == "end_hub":
                    parsed_data[key] = {
                        'name': data.name,
                        'coordinates': (data.x, data.y),
                        'metadata': metadata,
                        'line': line_count
                    }

                else:
                    # Add hub and connection structure to parsed data
                    if (key == "hub" and key not in parsed_data) or \
                            (key == "connection" and key not in parsed_data):
                        parsed_data.setdefault(key, [])

                    # Append hub info
                    if key == "hub":
                        parsed_data[key].append(
                            {
                                'name': data.name,
                                'coordinates': (data.x, data.y),
                                'metadata': metadata,
                                'line': line_count
                            }
                        )
                    # Append connection info
                    elif key == "connection":
                        parsed_data[key].append(
                            {
                                'name': data.name,
                                'metadata': metadata,
                                'line': line_count
                            }
                        )

            # Append all errors from pydantic validation to a list
            except ValidationError as e:
                for error in e.errors():
                    if ", " in error['msg']:
                        noise, msg = error['msg'].split(", ")
                        error['msg'] = msg
                    pydantic_errors.append((line_count, error['msg']))

    # Raise any errors from pydantic validation
    all_pyd_errors = []
    if pydantic_errors:
        pydantic_errors.sort()
        all_pyd_errors.extend([f" - Line {l_count}: {msg}"
                               for l_count, msg in pydantic_errors])
    if invalid_keys:
        if all_pyd_errors:
            all_pyd_errors.append("\n")
        all_pyd_errors.extend(invalid_keys)
    if all_pyd_errors:
        formatted_errors = '\n'.join(all_pyd_errors)
        raise ValueError(f"{formatted_errors}")

    # All required keys must have been parsed through
    required_keys = ("nb_drones", "start_hub", "end_hub", "connection", "hub")
    missing = set(required_keys) - set(parsed_data.keys())
    if missing:
        raise ValueError("[ERROR] Missing required configs: "
                         f"'{', '.join(missing)}'")

    # List every dict instruction in parsed_data together for post-validations
    post_errors = []
    parsed_items = [
        *[parsed_data[item] for item in ["start_hub", "end_hub"]
          if item in parsed_data],
        *parsed_data.get("hub", []),
        *parsed_data.get("connection", [])
    ]

    # Names cannot be repeated
    checked_names = {}
    for item in parsed_items:
        name = item['name']
        line = item['line']
        if name in checked_names:
            post_errors.append((line, f"Name '{name}' already defined at "
                               f"Line {checked_names[name]}"))
        else:
            checked_names[name] = line

    # Connection names must have known hub names
    sorted_connections = {}
    hub_names = {
        *[n['name'] for n in parsed_data.get('hub', [])],
        parsed_data.get('start_hub', {}).get('name'),
        parsed_data.get('end_hub', {}).get('name')
    }

    for item in parsed_data.get('connection', []):
        name = item['name']
        line = item['line']
        parts = name.split("-")
        for p in parts:
            if p not in hub_names:
                post_errors.append((line, f"Connection '{name}' "
                                   f"references unknown hub '{p}'"))

        # Connections cannot be repeated
        pair = tuple(sorted(parts))
        if pair in sorted_connections:
            post_errors.append((line, f"Connection '{name}' is a duplicate of "
                               f"the one at Line {sorted_connections[pair]}"))
        else:
            sorted_connections[pair] = line

    # Coordinates cannot be repeated
    checked_coords = {}
    coord_sources = [
        *[parsed_data[item] for item in ["start_hub", "end_hub"]
          if item in parsed_data],
        *parsed_data.get("hub", [])
        ]
    for item in coord_sources:
        coord = item['coordinates']
        line = item['line']
        if coord in checked_coords:
            post_errors.append((line, f"Coordinates '{coord}' already defined "
                               f"at Line {checked_coords[coord]}"))
        else:
            checked_coords[coord] = line

    # Raise post pydantic errors
    if post_errors:
        post_errors.sort()
        post_error_msgs = [f" - Line {l_count}: {msg}"
                           for l_count, msg in post_errors]
        formatted_post_errors = '\n'.join(post_error_msgs)
        raise ValueError(f"{formatted_post_errors}")

    return parsed_data
