/*
 * THIS LIBRARY ASSUMES THAT JQUERY V1.8 AND LEAFLET 0.5.1 ARE INCLUDED
 */


//if($.browser.msie == true)
//{
//    if($.browser.version < 8) {
//        alert("Please consider upgrading Internet Explorer to at least version 8 or switching to Google Chrome or " +
//            "Mozilla Firefox. This web site has not been tested for your browser and may not work as designed.")
//    }
//    else if ($.browser.version < 10) {
//        $.support.cors = true; // enable cross domain AJAX requests
//    }
//}

// Reclaim Cities object
//TODO externalize settings (don't forget about the geocoder)
var RC = {
    TILE_SET_URL: "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    CITY: "Philadelphia",
    STATE: "PA",
    COUNTRY: "USA",
    LATITUDE_DEFAULT: 39.9522,
    LONGITUDE_DEFAULT: -75.1642,
    ZOOM_DEFAULT: 15,
    ZOOM_MAX: 18,
    SEARCH_RADIUS_DEFAULT: 0.5, // miles //TODO Can we add some of these to configuration?
    MAP_ATTRIBUTION: 'Data by <a href="http://openstreetmap.org">OpenStreetMap</a>, under <a href="http://creativecommons.org/licenses/by-sa/3.0">CC BY SA</a>.'
};

//----------------------------------
/**
 * Creates a new Reclaim Cities map
 *
 * @param divId String The ID attribute of the DIV the map will appear in
 */
RC.map = function (divId) {
    var that = {};

    // Instance variables
    that.map = L.map(divId, {
            scrollWheelZoom: false
        }
    );
    that.markersArray = [];

    /**
     *
     */
    that.init = function () {
        var map = that.map.setView(L.latLng(RC.LATITUDE_DEFAULT, RC.LONGITUDE_DEFAULT), RC.ZOOM_DEFAULT);
        var tileLayer = L.tileLayer(RC.TILE_SET_URL, {
            maxZoom: RC.ZOOM_MAX,
            attribution: RC.MAP_ATTRIBUTION
        });

        tileLayer.addTo(map);
    };

    /**
     *
     * @param callbackFunction (no args)
     */
    that.clearLayers = function (callbackFunction) {
        for (var i = 0; i < that.markersArray.length; i++) {
            that.map.removeLayer(that.markersArray[i]);
        }

        if (callbackFunction != null) {
            callbackFunction();
        }
    };

    /**
     *
     * @param point GeoJSON Point
     * @param icon
     * @param callbackFunction (point, icon)
     * @returns {*}
     */
    that.addMarker = function (point, icon, callbackFunction) {
        var marker;

        if (icon != null) {
            // do nothing
        }
        else if( "properties" in point && "type" in point.properties){
            var type = point.properties.type;

            if (type == "nrs") {
                icon = RC.Pins.Nonresidential;
            }
            else if (type == "res") {
                icon = RC.Pins.Residential;
            }
            else if (type == "lot") {
                icon = RC.Pins.Lot;
            }
            else {
                icon = RC.Pins.X;
            }
        }
        else {
            icon = RC.Pins.X;
        }

        marker = L.marker(point.coordinates, {icon: icon});

        marker.addTo(that.map);
        that.markersArray.push(marker);

        if (callbackFunction != null) {
            callbackFunction(point, icon);
        }

        return marker;
    };

    that.addMarkers = function (points, icon, callbackFunction) {
        var markers = [];
        for (var i = 0; i < points.length; i++) {
            var marker = that.addMarker(points[i], icon, callbackFunction);
            markers.push(marker);
        }

        return markers;
    };

    that.focus = function (point, zoom) {
        // Convert to numbers for IE 9 or less
        var latNum = Number(point.coordinates[0]);
        var lonNum = Number(point.coordinates[1]);
        var zoomNum = (zoom == null) ? RC.ZOOM_DEFAULT : Number(zoom);

        // Center the map on the focus area and zoom
        var latLng = L.latLng(latNum, lonNum);
        that.map.setView(latLng, zoomNum);
    };

    /**
     *
     * @param streetAddress
     * @param callbackFunction (searchPoint, nearbyPoints)
     * //TODO add an error callback
     * //TODO make this synchronous and adding a searching callback
     */
    that.markNearbyLocations = function (streetAddress, callbackFunction) {
        RC.GEOCODER.geocode(streetAddress, function (points) {
            if (points.length <= 0) {
                //TODO add an error callback or could not locate the address
                alert("Sorry! Could not locate that address. Double check it and try again. Entered addresses should only be the street address (no need for city, state, zip, etc.).")
            }

            // Search point
            var searchPoint = points[0]; //TODO Future - ask user to choose which address if more than one result is returned
            that.focus(searchPoint);

            // Nearby points and callback
            RC.Data.getNearbyLocations(searchPoint, function (nearbyPoints) {
                for (var i = 0; i < nearbyPoints.length; i++) {
                    var point = nearbyPoints[i];
                    that.addMarker(point)
                        .bindPopup("<span class='addressText'>" + point.properties.address + "</span><br><a href='/location/" + point.properties.id + "'>View Details</a>", {
                            offset: L.point(0,-60)
                    });//);
                }

                if (callbackFunction != null) {
                    callbackFunction(searchPoint, nearbyPoints);
                }
            });
        });
    };

    /**
     * TODO document
     *
     * While geocoding is done asynchronously for IE8/XDocumentRequest/jQuery compatibility (versus synchronously),
     * the callbacks are called synchronously to prevent race conditions. In the future, it may be more pragmatic
     * to move the code out of callbacks and do on the server/backend.
     *
     * @param streetAddress
     * @param inDataCallback
     * @param notInDataCallback
     * @param finishedCallback
     */
    that.markPotentialLocations = function (streetAddress, inDataCallback, notInDataCallback, finishedCallback) {
        RC.GEOCODER.geocode(streetAddress, function (points) {
            for (var i = 0; i < points.length; i++) {
                var point = points[i];
                RC.Data.checkIfPointIsInData(point, inDataCallback, notInDataCallback);
            }

            if (finishedCallback != null) {
                finishedCallback();
            }
        });
    };

    that.init();
    return that;
};
//----------------------------------
// OPEN STREET MAPS (OSM)   - Functions based on OSM and converting OSM objects to GeoJSON ones
//                          - Good for Geocoding outside the USA (TAMU more complete for USA)

RC.OSM = {
    GEOCODE_BASE_URL: "http://nominatim.openstreetmap.org/search"
};

RC.OSM.geocode = function (streetAddress, callbackFunction) {
    var url = RC.Utils.addUrlParams(RC.OSM.GEOCODE_BASE_URL, {
            street: streetAddress,
            city: RC.CITY,
            state: RC.STATE,
            country: RC.COUNTRY,
            format: "json"
        }
    );

    $.ajax({
        dataType: "json",
        url: url,
        data: null,
        crossDomain: true,
        async: true,
        cache: false,
        success: function (osmLocations) {
            RC.OSM.locationsToPoints(osmLocations, callbackFunction);
        },
        error: function (jqxhr, msg, errorThrown) {
            alert("Sorry! Our server had an error trying to locate the address. Please let us know and/or try back later.");
        }
    });
};

RC.OSM.locationsToPoints = function (osmLocations, callbackFunction) {
    var points = [];
    for (var i = 0; i < osmLocations.length; i++) {
        points.push(RC.OSM.locationToPoint(osmLocations[i]));
    }

    if (callbackFunction != null) {
        callbackFunction(points);
    }

    return points;
};

RC.OSM.locationToPoint = function (osmLocation) {
    return {
        type: "Point",
        coordinates: [osmLocation.lat, osmLocation.lon],
        properties: {
            address: osmLocation.display_name
        }
    };
};

//----------------------------------
// TEXAS A&M UNIVERSITY GEOSERVICES (TAMU) - Geocoder. Good for USA, based on census data.
//  - Requests are proxied through reclaimcities because of cross domain calls not working for text requests
//      and JSONP not working for this purpose because of MIME type mismatch. This is also good to keep the
//      API key behind closed doors

RC.TAMU = {
    GEOCODE_BASE_URL: "/services/geocode/",
};

RC.TAMU.geocode = function (streetAddress, callbackFunction) {
    var url = RC.Utils.addUrlParams(RC.TAMU.GEOCODE_BASE_URL + streetAddress, {});

    $.ajax({
        dataType: "json",
        url: url,
        data: null,
        async: true,
        cache: false,
        success: function (points) {
            if(callbackFunction != null) {
                callbackFunction(points);
            }
        },
        error: function (jqxhr, msg, errorThrown) {
            alert("Sorry! Our server had an error trying to locate the address. Please let us know and/or try back later.");
        }
    });
};

//----------------------------------
// Set GEOCODER (now that they are defined)
RC.GEOCODER = RC.TAMU;
//RC.GEOCODER = RC.OSM;


//----------------------------------
RC.Data = {
    SEARCH_BASE_URL: "/services/locations"
};

/**
 *
 * @param latitude
 * @param longitude
 * @param callbackFunction (rcLocation)
 */
RC.Data.getNearbyLocations = function (searchPoint, callbackFunction) {
    var searchUrl = RC.Utils.addUrlParams(RC.Data.SEARCH_BASE_URL, {
        latitude: searchPoint.coordinates[0],
        longitude: searchPoint.coordinates[1],
        radius: RC.SEARCH_RADIUS_DEFAULT
    });

    $.getJSON(searchUrl, null, function (nearbyPoints) {
        if (callbackFunction != null) {
            callbackFunction(nearbyPoints);
        }
    });
};

/**
 * TODO document
 *
 * This is done synchronously to allow the callbacks to be used for display code
 * without race conditions.
 *
 * @param searchPoint
 * @param inDataCallback
 * @param notInDataCallback
 * @returns {Array}
 */
RC.Data.checkIfPointIsInData = function (searchPoint, inDataCallback, notInDataCallback) {
    var searchUrl = RC.Utils.addUrlParams(RC.Data.SEARCH_BASE_URL, {
        latitude: searchPoint.coordinates[0],
        longitude: searchPoint.coordinates[1],
        radius: 0.01
    });

    var matchingPoints = [];
    $.ajax({
        url: searchUrl,
        async: false,
        cache: false,
        success: function (points, msg, jqxhr) {
            var numPointsInData = points.length;
            if (numPointsInData > 0) {
                for (var i = 0; i < numPointsInData; i++) {
                    inDataCallback(points[i]);
                }
            }
            else {
                notInDataCallback(searchPoint);
            }
        },
        error: function (jqxhr, msg, errorThrown) {
            alert("Sorry! Our server had an error trying to locate the address. Please let us know and/or try back later.");
        }
    });

    return matchingPoints;
};


//----------------------------------


RC.Utils = {};

/**
 *
 * @param baseUrl
 * @param params
 * @returns {string}
 */
RC.Utils.addUrlParams = function (baseUrl, params) {
    var finalUrl = baseUrl + "?";

    for (var key in params) {
        finalUrl += key + "=" + params[key] + "&";
    }

    return encodeURI(finalUrl);
};


//----------------------------------


RC.Pins = {
    X: L.icon({
        iconUrl: reclaim.globals.STATIC_URL + 'images/pin-x.png',
        iconAnchor: [24, 65]
    }),
    Nonresidential: L.icon({
        iconUrl: reclaim.globals.STATIC_URL + 'images/pin-nonresidential.png',
       	iconAnchor: [24, 65]
    }),
    Residential: L.icon({
        iconUrl: reclaim.globals.STATIC_URL + 'images/pin-residential.png',
        iconAnchor: [24, 65]
    }),
    Lot: L.icon({
        iconUrl: reclaim.globals.STATIC_URL + 'images/pin-lot.png',
        iconAnchor: [24, 65]
    })
};