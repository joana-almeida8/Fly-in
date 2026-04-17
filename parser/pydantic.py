from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator


class Zone(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Metas(BaseModel):
    color: Optional[str] = Field(default=True)
    zone: Optional[Zone] = Field(default="normal")
    max_drones: Optional[int] = Field(default=1)
    max_link_capacity: Optional[int] = Field(default=1)

    @field_validator('color', mode="after")
    def color_validator(self):
        '''Post-pydantic validations for color'''
        # Check if value is a color
        # Accepted values for color are any valid single-word strings
        # (e.g., red, blue, gray). There is no fixed list of allowed colors :'(
        valid_colors = ["white", "black", "blue", "red", "yellow",
                        "green", "orange", "purple", "pink", "grey"]
        if self.color not in valid_colors:
            raise ValueError(f"{self.color} is not a valid color "
                             f"(Valid colors: {", ".join(valid_colors)})")


class LineParser(BaseModel):
    key: str
    name: str
    x: Optional[int]
    y: Optional[int]
    metadata: Optional[dict[Metas]]

    @model_validator(mode="before")
    @classmethod
    def parse_to_dict(cls, line: str) -> dict:
        '''Get line from input file and transform it into a raw_data dict'''
        # Split keys and values by ':'
        if ':' not in line:
            raise ValueError(f"Formatting error on line '{line}'")
        l_key, l_val = line.split(':', 1)

        # Raise error if val is missing
        if not l_val:
            raise TypeError(f"{l_key} has missing values")

        # Split values of key 'connection'
        if l_key == "connection":
            if " " in l_val:
                l_name, l_metadata = l_val.split(' ')
                return {
                    "key": l_key,
                    "name": l_name,
                    "metadata": l_metadata
                }
            # Metadata is optional
            return {
                "key": l_key,
                "name": l_name,
            }

        # Split values of other keys
        if "[" in l_val:
            l_name, l_x, l_y, l_metadata = l_val.split(' ')
            return {
                "key": l_key,
                "name": l_name,
                "x": l_x,
                "y": l_y,
                "metadata": l_metadata
            }
        # Metadata is optional
        else:
            l_name, l_x, l_y = l_val.split(' ')
            return {
                "key": l_key,
                "name": l_name,
                "x": l_x,
                "y": l_y,
            }

    @field_validator('metadata', mode="before")
    @classmethod
    def metas_to_dict(cls, metadata: str) -> Any[None, dict]:
        '''Transform metadata str into a dict'''
        # Metadata is optional so return may be none
        if not metadata:
            return

        # Validate format and remove []
        if not (metadata.startswith('[') and metadata.endswith(']')):
            raise ValueError(f"Metadata must be inside '[]' brackets")
        metadata = metadata.strip('[]', 1)

        # Add each meta to metadict
        metadict = {}
        metas: list = metadata.split()
        for m in metas:
            if "=" not in m:
                raise ValueError("Invalid format")
            key, val = m.split("=", 1)
            metadict[key] = val

        return metadict

    @model_validator(mode="after")
    def validator(self):
        '''Post-pydantic validations for each data instruction'''
        errors = []

        # Start and end hubs don't have max_drones or zone
        if self.key == "start_hub" or self.key == "end_hub":
            self.metadata

        if self.key == "connection":
            # Connection metadata validation
            if self.x or self.y:
                raise ValueError("Connections don't have coordinates")
            if self.metadata['zone'] or self.metadata['max_drones']:
            # if any('zone', 'max_drones') in self.metadata.keys()
                raise ValueError("Connections cannot have 'zone' "
                                 "or 'max_drones' metadata")
            
            # Connection syntax forbids dashes; <name>-<name>
            if "_" in self.name:
                raise ValueError("Connection names cannot have dashes "
                                 f"in {self.name}")
            if "-" not in self.name:
                raise ValueError("Connection names must have '-' "
                                 "separating hub names")

        # Hubs metadata validation
        if self.key == "hub":
            if self.metadata['max_link_capacity']:
                raise ValueError("Hubs cannot have a max_link_capacity")

        if errors:
            raise ValueError("\n".join(errors))
        return self
