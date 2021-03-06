"""
An assortment of functions that convert  models from one
type to another. Mostly used to prepare data for conversion
to JSON in web services.

(Note: django.core.serializer isn't used as much in the code
because it returns more data than is necessary and isn't as clean
as having it formatted first via these functions)
"""
from string import split


def location_to_point(location):
    """Converts a Location model to GeoJSON Point"""
    point = {
        "type": "Point",
        "coordinates": [location.latitude, location.longitude],
        "properties": {
            "id": location.id,
        }
    }

    if location.name:
        point["properties"]["name"] = location.name

    if location.description:
        point["properties"]["description"] = location.description

    if location.location_type:
        point["properties"]["location_type"] = location.location_type

    if location.ease_of_use:
        point["properties"]["ease_of_use"] = location.ease_of_use

    if location.safety:
        point["properties"]["safety"] = location.safety

    if location.capacity_type:
        point["properties"]["capacity_type"] = location.capacity_type

    if location.picture:
        point["properties"]["picture"] = location.picture

    return point


def locations_to_points(locations):
    points = []
    for location in locations:
        points.append(location_to_point(location))

    return points

def tamu_location_to_point(tamuLocationStr):
    tamuLocation = split(tamuLocationStr,',')
    point = {
        "type": "Point",
        "coordinates": [tamuLocation[3], tamuLocation[4]],
        "properties": {
            "address": "(no address for TAMU geocoding)"
        }
    }

    return point

def tamu_locations_to_points(tamuLocationsStr):
    points = []

    tamuLocationStrs = split(tamuLocationsStr, '\n')
    for tamuLocationStr in tamuLocationStrs:
        if tamuLocationStr != '':
            points.append(tamu_location_to_point(tamuLocationStr))

    return points

def geocode_cache_to_point(geocodeCache):
    point = {
        "type":"Point",
        "coordinates":[geocodeCache.latitude, geocodeCache.longitude],
        "properties": {
            "address": geocodeCache.address
        }
    }

    return point

def geocode_caches_to_points(geocodeCaches):
    points = []
    for geocodeCache in geocodeCaches:
        points.append(geocode_cache_to_point(geocodeCache))
    return points

