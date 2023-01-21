const map = L.map('map').setView([40, -3.7], 8);
var newMarker, count = 0, cache_data = [], cache_string = "";

$(function(){
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
            maxZoom: 18
        }).addTo(map);
        newMarkerGroup = new L.LayerGroup();
        map.on('click', addMarker);
        function addMarker(e){
            newMarker = new L.marker(e.latlng).addTo(map);
        }
});

$('#addRectangle').click(function(event) {
    $('#dataRectangle').show();
    $('#cacheRow').show();
    var north = map.getBounds().getSouth();
    var south = map.getBounds().getNorth();
    var east = map.getBounds().getEast();
    var west = map.getBounds().getWest();
    bounds = [[south, west], [north, east]]
    L.rectangle(bounds, {color: "#ff7800", weight: 1}).addTo(map);
    map.fitBounds(bounds);
    $('input[name="north"]').val(north);
    $('input[name="south"]').val(south);
    $('input[name="east"]').val(east);
    $('input[name="west"]').val(west);
});

$('#map').click(function(event) {
    var coordinates = newMarker.getLatLng();
    $('#cacheRow').append(
        `<div class="row my-2">
            <div class="col-4">
                <input type="text" class="form-control w-100" value="${coordinates.lat}" readonly>
            </div>
            <div class="col-4">
                <input type="text" class="form-control w-100" value="${coordinates.lng}" readonly>
            </div>
            <div class="col-4">
                <input type="text" class="form-control w-100" name="clue${count}" placeholder="Pista" required>
            </div>
        </div>`
    );
    cache_string += count == 0 ? `{"latitude":${coordinates.lat}, "longitude": ${coordinates.lng}}` : `, {"latitude":${coordinates.lat}, "longitude": ${coordinates.lng}}`;
    console.log(cache_string);
    $('input[name="caches"]').val(cache_string);
    cache_data.push({latitude: coordinates.lat, longitude: coordinates.lng});
    count++;
});

$('#addGameData').click(function(event) {
    
});