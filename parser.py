""" The input file must respect the expected structure and syntax:
• Each zone must have a unique name and valid integer coordinates.
• Zone names can use any valid characters but dashes and spaces.
• Connections must link only previously defined zones using connection: <zone1>-<zone2>
[metadata].
• The same connection must not appear more than once (e.g., a-b and b-a are considered duplicates).
• Any metadata block (e.g., [zone=... color=...] for zones, [max_link_capacity=...]
for connections) must be syntactically valid.
• Zone types must be one of: normal, blocked, restricted, priority. Any invalid
type must raise a parsing error.
• Capacity values (max_drones for zones, max_link_capacity for connections) must
be positive integers.
• Any other parsing error must stop the program and return a clear error message
indicating the line and cause. """

import sys
from pydantic import ValidationError
from parser import LineParser


def parser() -> dict[str, str]:
    '''Parse through each line in input and return structured dict with data'''
    
    # Get raw_data from the input file
    config_file = sys.argv[1]
    if not config_file.endswith(".txt"):
        raise ValueError(f"Input file '{config_file}' must have .txt format")

    parsed_data = {}
    with open(config_file, 'r') as file:
        for line in file:
            # Ignore empty or comment lines
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Split keys and values by ':'
            if ':' not in line:
                raise ValueError(f"Formatting error on line '{line}'")
            key, val = line.split(':', 1)

            # nb_drones 
            if not parsed_data:
                if key.lower() != "nb_drones":
                    raise ValueError("Input file must start with 'nb_drones'")
                value = int(val.strip())
                if not value:
                    raise ValueError(f"{key} value must be an integer")
                parsed_data[key] = value
            
            # Send all valid keys to pydantic class for validation
            valid_keys = ["start_hub", "end_hub", "hub", "connection"]
            pydantic_errors = {}
            invalid_keys = []
            if key.lower() in valid_keys:
                # There can only be one start and end hubs
                if key.lower == "start_hub":
                    if "start_hub" in parsed_data.keys():
                        raise KeyError(f"There can only be one {key}")
                if key.lower == "end_hub":
                    if "end_hub" in parsed_data.keys():
                        raise KeyError(f"There can only be one {key}")

                try:
                    # Send lines with valid keys to pydantic validation
                    data = LineParser(line)
                    
                    # Add parsed_line to parsed_data
                    parsed_data[]
                
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
                
    # Start and end hubs must be different
    if parsed_data['start_hub'] == parsed_data['end_hub']:
        raise ValueError("Entry and Exit coordenates cannot be the same")

    # All required keys must have been parsed through
    required_keys = ()
    missing = required_keys - set(parsed_data.keys())
    if missing:
        raise KeyError(f"Missing required configs: '{', '.join(missing)}")

    return parsed_data
