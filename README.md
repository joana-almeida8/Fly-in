*This project has been created as part of the 42 curriculum by jreis-de.*

# Fly-in
Fly-in is a drone delivery network simulation. It calculates and visualizes the movement of multiple drones across a graph of hubs and connections, optimizing for path efficiency and logical constraints.

## Description
### The Parser Engine
The project features a custom-built, tiered parsing engine designed to serve as a high-integrity data gateway. Unlike basic parsers, this engine is built to be non-crashing and comprehensive. It performs a full scan of the configuration file and aggregates all errors into a single, sorted report rather than failing at the first mistake.

The parser handles three primary responsibilities:
- **Syntax Enforcement**: Using Pydantic, it validates data types (integers, strings) and ensures the file follows the mandatory structural sequence (e.g., nb_drones initialization).
- **Logical Validation**: It identifies "Impossible Networks" by detecting overlapping coordinates, duplicate hub names, and orphaned connections.
- **Data Structuring**: It transforms raw text into a optimized dictionary format, utilizing Python's unpacking operators and set lookups to ensure the simulation engine receives a perfectly clean graph.

If the input file contains errors, the parser will raise a ValueError with a sorted list of issues:
- **Tier 1 (Format)**: Checks for missing colons, invalid types, or unknown instructions.
- **Tier 2 (Logic)**: Checks for duplicate hubs, used coordinates, or missing connection endpoints.

## Instructions

## Resources
The following resources were used for this project:
- **Grokking Algorithms**, by Aditya Y. Bhargava
- **[Pydantic docs](https://pydantic.dev/docs/validation/latest/concepts/models/)**
