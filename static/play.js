const map = L.map('map');
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
var data_caches = $('#dataCaches').val();
var bounds = [[south, west], [north, east]];
console.log(bounds);
map.fitBounds(bounds);

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
    return false;
};

var transform_obj = data_caches.replace(/'/g, '"');
var transform_obj2 = transform_obj.replace(/False/g, false);
var transform_obj3 = transform_obj2.replace(/True/g, true);
console.log(transform_obj3);
var obj = JSON.parse(transform_obj3);
for(var i in obj){
    // new L.marker(L.latLng(obj[i]['latitude'], obj[i]['longitude'])).addTo(map);
    if(!obj[i]['found']){
        $('#rowCachesFound').append(
            `<form action="/play" method="post" enctype = "multipart/form-data">
                <input type="text" class="form-control" name="id_play" value="${getUrlParameter('game')}" style="display:none;">
                <div class="row align-items-center my-3" id="row${i}">
                    <div class="col-3">
                        <input type="text" class="form-control" value="${obj[i]['clue']}" readonly>
                    </div>
                    <div class="col-2">
                        <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#image${i}">
                            Ver imagen
                        </button>
                        <!-- Modal -->
                        <div class="modal fade" id="image${i}" tabindex="-1" aria-hidden="true">
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title">Pista ${obj[i]['clue']}</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                    </div>
                                    <div class="modal-body">
                                        <img src="" alt="Pista imagen" id="id_image${i}" style="height:400px; width:400px;"/>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-auto">
                        <input class="btn btn-secondary" type="file" id="file" name="images${i}" accept="image/png, image/gif, image/jpeg, image/jpg"/>
                    </div>
                    <input type="text" name="cache" style="display: none;" value="${i}">
                    <div class="col-2">
                        <button class="btn btn-success" type="submit">Validar</button>
                    </div>
                </div>
            </form>
        `);
    }
    var link_image = `/static/img/${obj[i]['image']}`;
    console.log(link_image);
    console.log(i);
    console.log($('#id_image' + i));
    $('#id_image' + i).attr("src", link_image);
}