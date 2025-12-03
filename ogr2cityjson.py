import argparse
import json

import geopandas as gpd
import shapely


CITYJSON_TEMPLATE = {
  "type": "CityJSON",
  "version": "2.0",
  "transform": {
    "scale": [1.0, 1.0, 1.0],
    "translate": [0.0, 0.0, 0.0]
  },
  "CityObjects": {},
  "vertices": []
}


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("input_path", type=str, help="Path to input file")
    args.add_argument("output_path", type=str, help="Path to output CityJSON file")
    args.add_argument("--name-column", type=str, default=None, help="The column to use as city object name")
    parsed_args = args.parse_args()

    gdf = gpd.read_file(parsed_args.input_path)
    if parsed_args.name_column is not None:
        gdf.set_index(parsed_args.name_column, inplace=True)

    gdf_polys = gdf[gdf.geometry.geom_type == "MultiPolygon"]
    geom_type, coords, offsets = shapely.to_ragged_array(gdf_polys.geometry, include_z=True)

    cityjson = CITYJSON_TEMPLATE.copy()
    cityjson["vertices"] = coords.tolist()

    rings, polys, geoms = offsets

    for i, (idx, feature) in enumerate(gdf_polys.iterrows()):
        cityobject_id = str(idx)

        boundaries = []
        for poly in range(geoms[i], geoms[i+1] if (i + 1) < len(geoms) else len(geoms) - 1):
            ring_list = []
            for ring in range(polys[poly], polys[poly + 1] if (poly + 1) < len(polys) else len(rings) - 1):
                ring_list.append(
                    [j for j in range(rings[ring], rings[ring + 1] if (ring + 1) < len(rings) else len(coords) - 1)][::-1]
                )
            boundaries.append(ring_list)

        attributes = {
            k: str(feature[k])
            for k in feature.keys()
            if k != "geometry"
        }

        cityjson["CityObjects"][cityobject_id] = {
            "type": "Building",
            "attributes": attributes,
            "geometry": [
                {
                    "type": "MultiSurface",
                    "boundaries": boundaries
                }
            ]
        }

    with open(parsed_args.output_path, "w") as f:
        json.dump(cityjson, f)

    print(f"CityJSON file written to {parsed_args.output_path}")
