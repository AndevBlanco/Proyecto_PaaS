const map = L.map('map');
newMarkerGroup = new L.LayerGroup();
$(function(){
    L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
            maxZoom: 18
        }).addTo(map);
});
console.log("hoallaaa");
var north = $('#dataRectangleNorth').val();
var south = $('#dataRectangleSouth').val();
var east = $('#dataRectangleEast').val();
var west = $('#dataRectangleWest').val();
var bounds = [[south, west], [north, east]];
console.log(bounds);
map.fitBounds(bounds);

var transform_obj = data_caches.replace(/'/g, '"');
var transform_obj2 = transform_obj.replace(/False/g, false);
var transform_obj3 = transform_obj2.replace(/True/g, true);
console.log(transform_obj3);
var obj = JSON.parse(transform_obj3);
for(var i in obj){
    if(obj[i]['found']){
        console.log(obj[i]);

        let coords = L.latLng(obj[i]['latitude'], obj[i]['longitude']);
        console.log("Coood. ", coords);
        new L.marker(coords).addTo(map);
    }
}