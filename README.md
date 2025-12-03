# ogr2cityjson

A tool to convert any geospatial vector format (e.g., geopackage and shapefile) to CityJSON

## Installation

- Install Python 3.11 and `poetry`.
- Run `poetry install`

## Run

`poetry run python ogr2python.py input_path.gpkg output_path.json`

You can use the option `--name-column` to define a column from the source data to be the name of the city objects.
