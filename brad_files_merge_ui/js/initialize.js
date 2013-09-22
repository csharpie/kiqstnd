var bikeParkingTypes = ["Rack", "Corral", "Special Art Rack", "Pole", "Tree"];
var parkingSpotsSelect = $( "#parkingSpots" );
var stolenBikeLocationsSelect = $( "#stolenBikeLocations" );



$(document).ready(function() {
	var parkingSpotsSlider = $( "<div id='parkingSpotsSlider'></div>" ).insertAfter( parkingSpotsSelect ).slider({
		min: 1,
		max: 20,
		range: "min",
		value: parkingSpotsSelect[ 0 ].selectedIndex + 1,
		slide: function( event, ui ) {
			parkingSpotsSelect[ 0 ].selectedIndex = ui.value - 1;
		}
	});
	var stolenBikeLocationsSlider = $( "<div id='stolenBikeLocationsSlider'></div>" ).insertAfter( stolenBikeLocationsSelect ).slider({
		min: 1,
		max: 20,
		range: "min",
		value: stolenBikeLocationsSelect[ 0 ].selectedIndex + 1,
		slide: function( event, ui ) {
			stolenBikeLocationsSelect[ 0 ].selectedIndex = ui.value - 1;
		}
	});

	$( "#parkingSpots" ).change(function() {
		parkingSpotsSlider.slider( "value", this.selectedIndex + 1 );
	});

	$( "#stolenBikeLocations" ).change(function() {
		stolenBikeLocationsSlider.slider( "value", this.selectedIndex + 1 );
	});

	for (var i = 0; i < bikeParkingTypes.length; i++)
	{
		$("#parkingType")
			.append($("<option></option>")
	        .attr("value", bikeParkingTypes[i])
	        .text(bikeParkingTypes[i]));
	}

	$("#details-form").dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            "Ok": function() {
                $(this).dialog("close");
            },
            "Cancel": function() {
                $(this).dialog("close");
                return false;
            }
        }
    });

    $("#easeOfUse").raty({
    	score: 0,
    	starOn: "img/lib/star-on.png",
		starOff: "img/lib/star-off.png"
    });

    $("#safety").raty({
    	score: 0,
    	starOn: "img/lib/star-on.png",
		starOff: "img/lib/star-off.png"
    });
});
