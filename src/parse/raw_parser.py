import os
from typing import Any
from pydantic import ValidationError
from .pydantics import LineParser
from .post_validations import post_validation


def raw_parser(config_file: str) -> dict[str, Any]:
    '''Parse through each line in input and return structured dict with data'''

    # Get raw_data from the input file
    if not os.path.exists(config_file):
        raise FileNotFoundError(f" - Missing Input file '{config_file}'")
    if not config_file.endswith(".txt"):
        raise ValueError(f" - Input file '{config_file}' "
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
            if "#" in line:
                line = line.split("#")[0]

            # Split keys and values by ':'
            if ':' not in line:
                pydantic_errors.append((line_count, "Invalid format, "
                                       "missing ':'"))
                continue

            key, val = line.split(':')
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
                        if value <= 0:
                            pydantic_errors.append((line_count, f"'{key}' value"
                                                    " must be bigger than 0"))
                        parsed_data[key] = value
                    except ValueError:
                        pydantic_errors.append((line_count, f"'{key}' value "
                                               "must be a positive integer"))
                    continue

            # There can only be one start and end hub
            if key in ["start_hub", "end_hub", "nb_drones"]\
                    and key in parsed_data:
                invalid_keys.append((line_count, " -  There can only be one "
                                     f"'{key}'"))
                continue

            # Append all invalid keys
            valid_keys = ["start_hub", "end_hub", "hub", "connection"]
            if key not in valid_keys:
                invalid_keys.append((line_count, f" - Unknown key: '{key}'"))
                continue

            try:
                # Send lines with valid keys to pydantic validation
                data = LineParser.model_validate(line)

                # Add existing metadata to metadata dict
                metadata = {}
                if data.metadata:
                    metadata = data.metadata.model_dump()

                # Add start and end hubs to parsed_data
                if key == "start_hub" or key == "end_hub":
                    parsed_data[key] = {
                        'name': data.name,
                        'coordinates': (data.x, data.y),
                        **metadata,
                        'line': line_count
                    }

                else:
                    # Add hub and connection structure to parsed data
                    parsed_data.setdefault(key, [])
 
                    # Append hub info
                    if key == "hub":
                        parsed_data[key].append(
                            {
                                'name': data.name,
                                'coordinates': (data.x, data.y),
                                **metadata,
                                'line': line_count
                            }
                        )
                    # Append connection info
                    elif key == "connection":
                        parsed_data[key].append(
                            {
                                'name': data.name,
                                **metadata,
                                'line': line_count
                            }
                        )

            # Append all errors from pydantic validation to a list
            except ValidationError as e:
                for error in e.errors():
                    if ", " in error['msg']:
                        error['msg'] = error['msg'].split(", ")[1]
                    pydantic_errors.append((line_count, error['msg']))

    # Raise any errors from pydantic validation
    all_errors = sorted(pydantic_errors + invalid_keys)
    if all_errors:
        formatted_errors = '\n'.join(f" - Line {l}: {msg}" 
                                     for l, msg in all_errors)
        raise ValueError(formatted_errors)

    post_validation(parsed_data)

    return parsed_data
