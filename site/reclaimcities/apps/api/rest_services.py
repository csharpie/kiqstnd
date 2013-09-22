import requests

from django.core.exceptions import ValidationError
from django.http import HttpResponse, Http404, HttpResponseBadRequest, \
    HttpRequest, HttpResponseServerError, HttpResponseNotAllowed
from django.conf import settings
from reclaimcities.apps.web.models import GeocodeCache


try:
    import simplejson as json
except ImportError:
    import json
from reclaimcities.libs.services import LocationService, UserService
import reclaimcities.libs.conversions as conversions
import re
from reclaimcities.apps.web.models import Location
from django.views.decorators.csrf import csrf_exempt


#
# TODO Move more of the validation into the service classes (or take a look at the forms libraries within django)
#

# Static / Class level helper objects
LOCATION_SERVICE = LocationService()
USER_SERVICE = UserService()
VALID_LOCATION_ID_REGEX = re.compile('^\d+$')
VALID_ADDRESS_REGEX = re.compile('^(\w|\.|\s|-)+$')
VALID_DESCRIPTION_REGEX = re.compile('^(\w|\.|\s|-|!|\?|\')+$')


def json_response(response_obj):
    """
    TODO document
    :param response_obj:
    :return:
    """
    response = []
    if response_obj:
        response = json.dumps(response_obj)
    else:
        response = json.dumps(response)
    return HttpResponse(response, mimetype='application/json', content_type='application/json; charset=utf8')


@csrf_exempt
def get_locations_in_radius(request):  # , latitude, longitude, radius=0
    """
    TODO pydoc this better
    Gets a list of locations_dict within a given mile radius.

    Returned, is a GeoJSON array of Points with the following properties
    - id
    - address
    - pictures [URL , URL, URL] Up to three URLs
    - description
    - lot_type   TODO plusjeff This is coming back as the DB string, not the descriptive English version -- change that
                 (joe - I think that's because type is a Python reserved word that shows the type of an object)

    Example Request:
    http://localhost:8000/services/locations?latitude=1&longitude=2&radius=3
    GET Params
        - latitude - number
        - longitude - number
        - radius - number
    """
    # Validate request - must be GET
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    # Validate latitude - required, number only
    try:
        latitude = request.GET['latitude']
        latitude = float(latitude)
    except KeyError:
        return HttpResponseBadRequest('Missing latitude parameter')
    except ValueError:
        return HttpResponseBadRequest('Non-numeric latitude parameter')

    # Validate longitude - required number only
    try:
        longitude = request.GET['longitude']
        longitude = float(longitude)
    except KeyError:
        return HttpResponseBadRequest('Missing longitude parameter')
    except ValueError:
        return HttpResponseBadRequest('Non-numeric longitude parameter')

    # Validate radius - required, number only
    try:
        radius = request.GET['radius']
        radius = float(radius)
    except KeyError:
        return HttpResponseBadRequest('Missing radius parameter')
    except ValueError:
        return HttpResponseBadRequest('Non-numeric radius parameter')

    # Perform search
    locations_dict = LOCATION_SERVICE.get_locations(latitude, longitude, radius)
    points = conversions.locations_to_points(locations_dict)

    return json_response(points)

@csrf_exempt
def get_location_by_id(request, id):

    location = LOCATION_SERVICE.get_location(id=id)
    if not location:
        raise Http404

    points = conversions.location_to_point(location)

    return json_response(points)

@csrf_exempt
def add_location(request): #, latitude, longitude, lot_type, address=None, pictures=None, description=None
    """
    TODO document
    TODO allow it to accept GeoJSON point as input too
    """

    # Validate request - must be POST
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # Validate latitude - required, number only
    try:
        latitude = request.POST['latitude']
        latitude = float(latitude)
    except KeyError:
        return HttpResponseBadRequest('Missing latitude parameter')
    except ValueError:
        return HttpResponseBadRequest('Non-numeric latitude parameter')

    # Validate longitude - required, number only
    try:
        longitude = request.POST['longitude']
        longitude = float(longitude)
    except KeyError:
        return HttpResponseBadRequest('Missing longitude parameter')
    except ValueError:
        return HttpResponseBadRequest('Non-numeric longitude parameter')

    # Validate location_type - required, must be be a valid type
    try:
        location_type = request.POST['location_type']
        if not Location.VALID_TYPES.count(location_type):
            return HttpResponseBadRequest('Invalid type parameter. Valid options are: ' + str(Location.VALID_TYPES))
    except KeyError:
        location_type = None

    # Validate pictures - optional, must be under a certain size limit
    try:
        picture = request.FILES.get('picture')
    except KeyError:
        picture = None

    # Validate description - optional; limit to 200 characters; only letters, numbers, common punctuation, dashes
    try:
        description = request.POST['description']
        if description and len(description) > 200 and not VALID_DESCRIPTION_REGEX.match(description):
            return HttpResponseBadRequest(
                'Invalid description parameter. Can only contain periods, spaces, question marks, exclamations, letters, numbers, and dashes')
    except KeyError:
        description = None

    # Name -- do validation later
    try:
        name = request.POST['name']
    except KeyError:
        return HttpResponseBadRequest('Missing name parameter.')

    # Validate location_type - required, must be be a valid type
    try:
        capacity_type = request.POST['capacity_type']
        if not Location.VALID_CAPACITY_TYPES.count(capacity_type):
            return HttpResponseBadRequest('Invalid type parameter. Valid options are: ' + str(Location.VALID_CAPACITY_TYPES))
    except KeyError:
        capacity_type = None

    # Safety
    try:
        safety = request.POST['safety']
    except KeyError:
        safety = None


    # Ease of Use
    try:
        ease_of_use = request.POST['ease_of_use']
    except KeyError:
        ease_of_use = None

    # Add the location
    try:
        location = LOCATION_SERVICE.add_location(latitude, longitude, name, location_type, picture, description, safety, ease_of_use, capacity_type)
    except Exception as e:
        return HttpResponseServerError('Was unable to add the new location due to an error: %s' % e)

    # return the location that was just added
    return get_location_by_id(request, location.id)

@csrf_exempt
def update_location(request, id): # lot_type=None, address=None, pictures=None, description=None
    """
    TODO document
    TODO allow it to accept GeoJSON point as input too
    TODO when adding new pictures, first fill any empty slots before replacing
    """
    # Validate request - must be POST
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # Validate location_type - required, must be be a valid type
    try:
        location_type = request.POST['location_type']
        if not Location.VALID_TYPES.count(location_type):
            return HttpResponseBadRequest('Invalid type parameter. Valid options are: ' + str(Location.VALID_TYPES))
    except KeyError:
        location_type = None

    # Validate location_type - required, must be be a valid type
    try:
        capacity_type = request.POST['capacity_type']
        if not Location.VALID_CAPACITY_TYPES.count(capacity_type):
            return HttpResponseBadRequest('Invalid type parameter. Valid options are: ' + str(Location.VALID_CAPACITY_TYPES))
    except KeyError:
        capacity_type = None

    # Validate name
    try:
        name = request.POST.get('name', None)
    except KeyError:
        name = None

    # Validate pictures - optional, must be under a certain size limit
    try:
        picture = request.FILES.get('picture')
    except KeyError:
        picture = None

    # Ease of Use
    try:
        ease_of_use = request.POST.get('ease_of_use')
    except KeyError:
        ease_of_use = None

    # Safety
    try:
        safety = request.POST.get('safety')
    except KeyError:
        safety = None

    # Validate description - optional; limit to 200 characters; only letters, numbers, common punctuation, dashes
    try:
        description = request.POST['description']
        if description and len(description) > 200 and not VALID_DESCRIPTION_REGEX.match(description):
            return HttpResponseBadRequest(
                'Invalid description parameter. Can only contain spaces, periods, question marks, exclamations, letters, numbers, and dashes')
    except KeyError:
        description = None

    # Add the location
    try:
        location = LOCATION_SERVICE.update_location(id=id, location_type=location_type, name=name, picture=picture, description=description, ease_of_use=ease_of_use, safety=safety, capacity_type=capacity_type)
    except Exception as e:
        return HttpResponseServerError('Was unable to add the new location due to an error: ' + e.message)

    # return the location that was just updated
    if location:
        return get_location_by_id(request, location.id)
    else:
        return HttpResponseBadRequest("No update was made")

@csrf_exempt
def geocode(request, streetAddress):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    if not streetAddress:
        raise Http404

    # Try to get from cache first
    geocodeCaches = GeocodeCache.objects.filter(address=streetAddress.lower())
    if(geocodeCaches):
        points = conversions.geocode_caches_to_points(geocodeCaches)
        return json_response(points)

    # Retrieve from Geocoder
    # TODO parameterize some of this information in a config file
    params = {
        "apiKey": settings.TAMU_GEOCODING_API_KEY,
        "version": "4.01",
        "streetAddress": streetAddress,
        "city": "Philadelphia",
        "state": "PA",
        "allowTies": True,
        "format": "csv",
        "notStore": True,
        "includeHeader": False
    }

    r = requests.get("http://geoservices.tamu.edu/Services/Geocode/WebService/GeocoderWebServiceHttpNonParsed_V04_01.aspx", params=params)
    points = conversions.tamu_locations_to_points(r.text)

    # Save in cache
    for point in points:
        geocodeCache = GeocodeCache()
        geocodeCache.address = streetAddress.lower()
        geocodeCache.latitude = point["coordinates"][0];
        geocodeCache.longitude = point["coordinates"][1];
        geocodeCache.save()

    return json_response(points)

@csrf_exempt
def load_file(request):

    LOAD_URLS = ['http://gis.phila.gov/ArcGIS/rest/services/Streets/Bike_Racks/MapServer/1/query?text=&geometry=%7B%22spatialReference%22%3A%7B%22wkid%22%3A4326%7D%2C%22rings%22%3A%5B%5B%5B-75.18733978271484%2C39.95422755797634%5D%2C%5B-75.13446807861328%2C39.95106936461956%5D%2C%5B-75.13652801513672%2C39.92448212528485%5D%2C%5B-75.12931823730467%2C39.905259175197614%5D%2C%5B-75.14305114746094%2C39.88365983864681%5D%2C%5B-75.19351959228516%2C39.88207913214082%5D%2C%5B-75.22064208984375%2C39.92764154592116%5D%2C%5B-75.18733978271484%2C39.95422755797634%5D%5D%5D%7D&geometryType=esriGeometryPolygon&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&objectIds=&where=1%3D1&time=&returnCountOnly=false&returnIdsOnly=false&returnGeometry=true&maxAllowableOffset=&outSR=4326&outFields=*&f=pjson',
                 'http://gis.phila.gov/ArcGIS/rest/services/Streets/Bike_Racks/MapServer/1/query?text=&geometry=%7B%22spatialReference%22%3A%7B%22wkid%22%3A4326%7D%2C%22rings%22%3A%5B%5B%5B-75.18733978271484%2C39.95422755797634%5D%2C%5B-75.13446807861328%2C39.95106936461956%5D%2C%5B-75.0864028930664%2C39.97659391922923%5D%2C%5B-75.05413055419922%2C40.004212850519885%5D%2C%5B-75.05207061767578%2C40.024985445869156%5D%2C%5B-75.20793914794922%2C40.02261926678969%5D%2C%5B-75.20622253417969%2C39.98264473554439%5D%2C%5B-75.18630981445312%2C39.95291166179976%5D%5D%5D%7D%0D%0A&geometryType=esriGeometryPolygon&inSR=&spatialRel=esriSpatialRelIntersects&relationParam=&objectIds=&where=1%3D1&time=&returnCountOnly=false&returnIdsOnly=false&returnGeometry=true&maxAllowableOffset=&outSR=4326&outFields=*&f=pjson']

    location_list = []

    for load_url in LOAD_URLS:
        
        in_file = requests.get(load_url)

        if in_file.status_code != 200:
            return HttpResponseBadRequest("HTTP request failed - status code %d" % in_file.status)

        in_json = in_file.json()

        points_list = in_json["features"]

        for point in points_list:
            geometry = point["geometry"]
            attributes = point["attributes"]

            x = round(geometry["x"], 17)
            y = round(geometry["y"], 17)
            print("x: " + str(x) + ", y: " + str(y))
            # x = 1
            # y = 1
            name = attributes["LOCATION"]

            newLocation = Location(latitude=y, longitude=x, name=name, location_type="rack")

            # newLocation.save()

            location_list.append(newLocation)

    Location.objects.all().delete()
    Location.objects.bulk_create(location_list)

    return HttpResponse("Load OK")

@csrf_exempt
def get_theft_points(request):

    # Validate latitude - required, number only
    try:
        latitude = request.GET['latitude']
        latitude = float(latitude)
    except KeyError:
        return HttpResponseBadRequest('Missing latitude parameter')
    except ValueError:
        return HttpResponseBadRequest('Non-numeric latitude parameter')

    # Validate longitude - required, number only
    try:
        longitude = request.GET['longitude']
        longitude = float(longitude)
    except KeyError:
        return HttpResponseBadRequest('Missing longitude parameter')
    except ValueError:
        return HttpResponseBadRequest('Non-numeric longitude parameter')

    location_data = {'latitude' : latitude, 'longitude' : longitude, 'radius': 0.1}
    re = requests.get("http://127.0.0.1:8100/search", params=location_data)
    return json_response(re.json())