from django.db import models
from hashlib import md5
import random


# Create your models here.
class Location(models.Model):
    """
    """

    # Physical location data
    latitude = models.DecimalField(max_digits=20, decimal_places=17)
    longitude = models.DecimalField(max_digits=20, decimal_places=17)
    name = models.CharField(max_length=50, blank=False, null=False)

    # Valid types
    VALID_TYPES = ("rack", "corral", "carousel", "pole", "tree", "fence", "bush")
    LOCATION_TYPES = (  # Keep this in-sync with VALID_TYPES
                        ("rack", "Rack"),
                        ("corral", "Corral"),
                        ("carousel", "Carousel"),
                        ("pole", "Pole / Post"),
                        ("tree", "Tree"),
                        ("fence", "Fence"),
                        ("bush", "Burning Bush")
    )
    location_type = models.CharField(max_length="10", choices=LOCATION_TYPES, blank=True, null=True)

    # Description
    description = models.CharField(max_length="200", blank=True, null=True)
    picture = models.ImageField(upload_to="images/locations", blank=True, null=True)

    ease_of_use = models.IntegerField(blank=True, null=True)
    safety = models.IntegerField(blank=True, null=True)

    # Capacity
    VALID_CAPACITY_TYPES = ("1", "2", "more")
    CAPACITY_TYPES = (  
                        ("1", "1 Bikes"),
                        ("2", "2 Bikes"),
                        ("more", "More than 2 Bikes")
    )
    capacity_type = models.CharField(max_length="4", choices=CAPACITY_TYPES, blank=True, null=True)

    def __unicode__(self):
        return "(" + str(self.id) + ") Latitude: " + str(self.latitude) + ", " + "Longitude: " + str(self.longitude)


class GeocodeCache(models.Model):
    address = models.CharField(max_length=200, blank=False, null=False)
    latitude = models.DecimalField(max_digits=40, decimal_places=20)
    longitude = models.DecimalField(max_digits=40, decimal_places=20)
