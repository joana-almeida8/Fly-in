from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator


class Zone(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Metas(BaseModel):
    color: Optional[str] = Field(default="black")
    zone: Optional[Zone] = Field(default=Zone.NORMAL)
    max_drones: Optional[int] = Field(default=1, gt=0)
    max_link_capacity: Optional[int] = Field(default=1, gt=0)

    @field_validator('color', mode="after")
    @classmethod
    def color_validator(cls, color: str) -> str:
        '''Post-pydantic validations for color'''
        # Check if value is a single word
        if not color.isalpha():
            raise ValueError(f"'{color}' must be a single word (letters only)")
        
        return color

    @field_validator('zone', mode="after")
    @classmethod
    def zone_validator(cls, zone: Zone) -> Zone:
        '''Post-pydantic validation for zone'''
        # Zone names can use any valid characters but dashes and spaces
        if " " in zone.value or "_" in zone.value:
            raise ValueError(f"{zone.value} name must not have spaces/dashes")

        return zone


class LineParser(BaseModel):
    key: str
    name: str
    x: Optional[int] = Field(default=None, ge=0)
    y: Optional[int] = Field(default=None, ge=0)
    metadata: Optional[Metas] = None

    @model_validator(mode="before")
    @classmethod
    def parse_to_dict(cls, line: Any) -> dict:
        '''Get line from input file and transform it into a raw_data dict'''

        if not isinstance(line, str):
            return line

        # Split keys and values by ':'
        if ':' not in line:
            raise ValueError(f"Formatting error on line '{line}'")

        l_key, l_val = line.split(':', 1)
        l_key = l_key.lower().strip()
        l_val = l_val.strip()

        # Raise error if val is missing
        if not l_val:
            raise ValueError(f"{l_key} has missing values")

        parts = l_val.split()

        # If metadata exists, remove it and add it to metadata_str
        metadata_str = None
        if parts and parts[-1].startswith("["):
            metadata_str = parts.pop()

        # Split values of key 'connection'
        if l_key == "connection":
            if len(parts) != 1:
                raise ValueError("Connections cannot have coordinates")
            return {
                "key": l_key,
                "name": parts[0],
                "metadata": metadata_str
            }

        # Return hubs values
        if len(parts) != 3:
            raise ValueError("Hubs require name and two coordinates")
        return {
            "key": l_key,
            "name": parts[0],
            "x": parts[1],
            "y": parts[2],
            "metadata": metadata_str
        }

    @field_validator('metadata', mode="before")
    @classmethod
    def metas_to_dict(cls, metadata: Any) -> Optional[dict]:
        '''Transform metadata str into a dict'''
        # Metadata is optional so return may be none
        if not metadata or not isinstance(metadata, str):
            return

        # Validate format and remove []
        if not (metadata.startswith('[') and metadata.endswith(']')):
            raise ValueError(f"Metadata must be inside '[]' brackets")
        metadata = metadata.strip('[]')

        # Add each meta to metadict
        metadict = {}
        for m in metadata.split():
            if "=" not in m:
                raise ValueError(f"Invalid metadata format in '{m}'")
            key, val = m.split("=", 1)
            if key not in ["color", "zone", "max_drones", "max_link_capacity"]:
                raise ValueError(f"Unknown metadata detected: '{key}'")
            metadict[key] = val
        return metadict

    @model_validator(mode="after")
    def post_validator(self) -> 'LineParser':
        '''Post-pydantic validations for each data instruction'''
        m = self.metadata
        errors = []

        # Start and end hubs don't have max_drones or zone
        if self.key in ["start_hub", "end_hub"]:
            if m and (m.zone != Zone.NORMAL or\
                      m.max_drones != 1 or\
                      m.max_link_capacity != 1):
                errors.append(f"{self.key} only supports 'color' metadata")

        # Connection metadata validation
        elif self.key == "connection":
            if m and (self.x or self.y):
                errors.append("Connections cannot have coordinates")
            if m and (m.zone != Zone.NORMAL or m.max_drones != 1):
                errors.append("Connections cannot have 'zone' "
                              "or 'max_drones' metadata")

            # Connection syntax forbids dashes; <name>-<name>
            if "_" in self.name:
                errors.append("Connection names cannot have dashes "
                              f"in '{self.name}'")
            if "-" not in self.name:
                errors.append("Connection names must have '-' "
                              "separating hub names")

        # Hubs metadata validation
        elif self.key == "hub":
            if m and m.max_link_capacity != 1:
                errors.append("Hubs cannot have a max_link_capacity")

        if errors:
            raise ValueError("\n".join(errors))

        return self
