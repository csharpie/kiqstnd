var bikeTheft = L.layerGroup();
var bikeParkingIcon = 
	L.icon({
		iconUrl: 'img/lib/parking-bicycle.png'
});

var bikeTheftIcon = 
	L.icon({
    	iconUrl: 'img/lib/theft.png'
});

var map = L.map("map", function(){
	layers : [ parking ]
});

map.setView([39.9522, -75.1642], 15);

L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://cloudmade.com">CloudMade</a>',
    maxZoom: 18
}).addTo(map);

var baseMaps = {
			    "Bike Theft": bikeTheft,
			    "Default": L.layerGroup()
};

L.control.layers(baseMaps).addTo(map);