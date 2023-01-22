const map = L.map('map');
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
console.log("hoallaaa");
var north = $('#dataRectangleNorth').val();
var south = $('#dataRectangleSouth').val();
var east = $('#dataRectangleEast').val();
var west = $('#dataRectangleWest').val();
var bounds = [[south, west], [north, east]];
console.log(bounds);
map.fitBounds(bounds);