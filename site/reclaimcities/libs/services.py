from django.core.exceptions import ValidationError
from django.forms.fields import ImageField
from reclaimcities.apps.web.models import Location
from django.contrib.auth.models import User


class LocationService():
    """
    Performs convenience search and data access functions for Location objects
    """

    MILE_PER_DEGREE_LATITUDE = (1.0 / 69.0)
    MILE_PER_DEGREE_LONGITUDE = (
        1.0 / 49.0) # Approximate, since this changes depending on how far North or South, 49 is at 45 degress (or halfway between equator and poles)

    def get_locations(self, latitude, longitude, mile_radius):
        """
        Retrieves a list of all Location objects within a specified mile radius
        from a given point (latitude and longitude).

        If none are found, returns an empty list.
        """
        latitude_diff = mile_radius * LocationService.MILE_PER_DEGREE_LATITUDE
        upper_bound_latitude = latitude + latitude_diff
        lower_bound_latitude = latitude - latitude_diff

        longitude_diff = mile_radius * LocationService.MILE_PER_DEGREE_LONGITUDE
        upper_bound_longitude = longitude + longitude_diff
        lower_bound_longitude = longitude - longitude_diff

        locations = Location.objects.filter(latitude__lte=upper_bound_latitude,
                                            latitude__gte=lower_bound_latitude,
                                            longitude__lte=upper_bound_longitude,
                                            longitude__gte=lower_bound_longitude)

        return locations

    def add_location(self, latitude, longitude, name, location_type=None, picture=None, description=None, safety=None, ease_of_use=None, capacity_type=None):
        """
        Adds a new Location object to the database

        Returns the newly created Location object
        """
        new_location = Location()
        new_location.latitude = latitude
        new_location.longitude = longitude
        new_location.name = name
        new_location.location_type = location_type
        new_location.picture = picture
        new_location.description = description
        new_location.safety = safety
        new_location.ease_of_use = ease_of_use
        new_location.capacity_type = capacity_type

        new_location.save()

        return new_location

    def update_location(self, id, location_type=None, name=None, picture=None, description=None, ease_of_use=None, safety=None, capacity_type=None):
        """
        Updates an existing Location object to the database

        Returns the newly created Location object
        """
        updated = False

        locations = Location.objects.filter(id=id)
        if locations and len(locations) == 1:
            location = locations[0]
        else:
            e = Exception(self)
            e.message = "Location with that ID not found"
            raise e

        if location_type:
            location.location_type = location_type
            updated = True

        if name:
            location.name = name
            updated = True

        if description:
            location.description = description
            updated = True

        if picture:
            location.picture = picture
            updated = True

        if ease_of_use:
            location.ease_of_use = ease_of_use
            updated = True

        if safety:
            location.safety = safety
            updated = True

        if capacity_type:
            location.capacity_type = capacity_type
            updated = True

        if updated:
            location.save()

        return location


    def get_location(self, latitude=None, longitude=None, id=None):
        """
        Gets a Location object from a given point (latitude and longitude).

        If a matching Location object isn't found, returns None
        """
        try:
            if latitude and longitude:
                return Location.objects.get(latitude=latitude, longitude=longitude)
            elif id:
                return Location.objects.get(id=id)
            else:
                return None
        except:
            return None


class UserService:
    def create_user(self, username, email, password):
        user = User(username=username, email=email, password=password)
        user.full_clean()

        # Check e-mail since Django User class doesn't make it a required field
        if not email:
            raise ValidationError("Email was empty")

        user.save()

        return user
