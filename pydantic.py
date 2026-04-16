from typing import Optional
from pydantic import BaseModel, ValidationError, ValidationInfo, model_validator


class Metas(BaseModel):
    color: str
    zone: str
    max_drones: int

    @model_validator(mode="after")
    def metas_validator(self, line: ValidationInfo):
        '''Post-pydantic validations for metadata per key type'''
        key = line.context.get()
        if 


class LineParser(BaseModel):
    key: str
    name: str
    x: Optional[int]
    y: Optional[int]
    metadata: Optional[list[Metas]]

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

    @model_validator(mode="after")
    def validator(self):
        '''Post-pydantic validations for each data instruction'''
        errors = []
        if self.metadata_data:
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
