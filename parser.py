""" The input file must respect the expected structure and syntax:
• The first line must define the number of drones using nb_drones: <positive_integer>.
• The program must be able to handle any number of drones.
• There must be exactly one start_hub: zone and one end_hub: zone.
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
from typing import Optional
from pydantic import BaseModel, Field, ValidationError, model_validator


""" class Metadata(Enum):
    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"
 """

class LineParser(BaseModel):
    key_data: str
    name_data: str
    x_data: int
    y_data: int
    metadata_data: Optional[str]

    @model_validator(mode="after")
    def validator(self):
        errors = []
        if not self.metadata_data:
            return self
        if not (self.metadata_data.startswith('[')
                and self.metadata_data.endswith(']')):
            raise ValueError(f"Metadata in {self.key_data} must "
                             "be inside '[]' brackets")
        self.metadata_data = self.metadata_data.strip('[]', 1)

        # Start and end hubs don't have max_drones or zone
        if self.key_data == "start_hub" or self.key_data == "end_hub":
            self.metadata_data


            errors.append("Contact ID must start with 'AC' (Alien Contact)")
        
        if errors:
            raise ValueError("\n".join(errors))
        return self


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

            # nb_drones #######################################################
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
            if key.lower() in valid_keys:
                try:
                    LineParser(line)
                except ValidationError as e:
                    value_errors = []
                    for error in e.errors():
                        if "Value error" in error['msg']:
                            noise, msg = error['msg'].split(", ")
                            error['msg'] = msg
                        value_errors.append(error)
                    pydantic_errors['key'] = value_errors

            # Raise any errors from pydantic validation
            if pydantic_errors:
                for p_error in 
                raise ValueError(f"{"\n".join(error_line)}")

            # start_hub #######################################################
            if key.lower == "start_hub":
                if "start_hub" in parsed_data.keys():
                    raise KeyError(f"There can only be one {key}")
                name, x, y, metadata = val.split(' ')
                data = LineParser(
                    key_data=key,
                    name_data=name
                    x_data=x,
                    y_data=y,
                    metadata_data=metadata,
                )
                value = f"{name} {x} {y} {metadata}"
                

    # Start and end hubs must be different
    if parsed_data['start_hub'] == parsed_data['end_hub']:
        raise ValueError("Entry and Exit coordenates cannot be the same")

    # All required keys must have been parsed through
    required_keys = ()
    missing = required_keys - set(parsed_data.keys())
    if missing:
        raise KeyError(f"Missing required configs: '{', '.join(missing)}")

    return parsed_data
