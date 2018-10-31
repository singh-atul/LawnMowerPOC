function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(initialize);
    } else { 
        x.innerHTML = "Geolocation is not supported by this browser.";
    }
}


var hostServer='http://127.0.0.1:5000';
var map ;
var myPolygon ;
function initialize(position){

var myLatLng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);

var mapOptions = {
    zoom: 50,
    center: myLatLng,
    mapTypeId: google.maps.MapTypeId.SATELLITE
  };

map = new google.maps.Map(document.getElementById('map'),mapOptions);

 // Polygon Coordinates
  var triangleCoords = [

    new google.maps.LatLng(position.coords.latitude-0.0001, position.coords.longitude+0.0001),
    new google.maps.LatLng(position.coords.latitude+0.0001, position.coords.longitude+0.0001),
    new google.maps.LatLng(position.coords.latitude+0.0001, position.coords.longitude-0.0001),
    new google.maps.LatLng(position.coords.latitude-0.0001, position.coords.longitude-0.0001)

    // new google.maps.LatLng(position.coords.latitude+0.0001, position.coords.longitude+0.0001),
    // new google.maps.LatLng(position.coords.latitude+0.0001, position.coords.longitude-0.0001),
    // new google.maps.LatLng(position.coords.latitude-0.0001, position.coords.longitude-0.0001),
    // new google.maps.LatLng(position.coords.latitude-0.0001, position.coords.longitude+0.0001)
    
  ];
  // Styling & Controls
  myPolygon = new google.maps.Polygon({
    paths: triangleCoords,
    draggable: true, 
    editable: true,
    strokeColor: '#228B22',
    strokeOpacity: 0.8,
    strokeWeight: 2,
    fillColor: '#00FF00',
    fillOpacity: 0.35
  });

  myPolygon.setMap(map);
  google.maps.event.addListener(myPolygon.getPath(), "insert_at", getPolygonCoords);
  google.maps.event.addListener(myPolygon.getPath(), "set_at", getPolygonCoords);
	
}

var mowerPath=""
function gloabl_path_coverage(locations){
var infowindow = new google.maps.InfoWindow();
var marker, i;
var lawn_mowing_path = []
for (i = 0; i < locations.length; i++){
  lawn_mowing_path.push({'lat':locations[i][0],'lng':locations[i][1]});
}
// for (i = locations.length; i > 0; i--){
//   lawn_mowing_path.push({'lat':locations[i][0],'lng':locations[i][1]});
// }
 mowerPath = new google.maps.Polyline({
  path:lawn_mowing_path,
  geodesic: true,
  strokeColor: '#FF0000',
  strokeOpacity: 1.0,
  strokeWeight: 2
});

mowerPath.setMap(map);
document.getElementById("info").innerHTML = 'Points Plotted',Object.prototype.toString.call(locations);
}




var htmlStr = "";
function getPolygonCoords() {
  var len = myPolygon.getPath().getLength();
  htmlStr = "";
  for (var i = 0; i < len; i++) {
    htmlStr += "\n" + myPolygon.getPath().getAt(i).toUrlValue(5)+"#";
  }
  document.getElementById('info').innerHTML = htmlStr;
}
json_format = '';

function download() {
  $("#gif").show();
  product_store = {}
	console.log("Data is "+htmlStr);

      var formData = new FormData();
      formData.append('data',htmlStr);
      $.ajax({
        url: hostServer + '/control/recordPoints',
        cache: false,
        type: "POST",
        data: formData,
        timeout: 120000,
        processData: false,
        contentType: false,
        success: function (resp) {
          console.log('Its working' , resp);
          setTimeout(function(){ 
          $("#gif").hide(); }, 
          500);
          
          json_format = JSON.parse(JSON.parse(resp));
          console.log(json_format[0]);
          gloabl_path_coverage(json_format);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
          $("#gif").hide();
        }
    });

}


function copyToClipboard(text) {
  download(htmlStr, 'json.txt', 'text/plain');
  window.prompt("Copy to clipboard: Ctrl+C, Enter", text);
}


function clear_points(){
  mowerPath.setMap(null);
}


//Start Mower

function startMower() {
  
	console.log("In startMower function");
      
      $.ajax({
        url: hostServer + '/control/startMower',
        cache: false,
        type: "POST",
        timeout: 120000,
        processData: false,
        contentType: false,
        success: function (resp) {
          console.log('startMower Response : ' , resp);
          setTimeout(function(){ 
          $("#gif").hide(); }, 
          500);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
          console.log('startMower Function encountered Error');
          $("#gif").hide();
        }
    });

}

// stop Mower 
function stopMower() {
  
 
	console.log("In stopMower function");
  
      $.ajax({
        url: hostServer + '/control/stopMower',
        cache: false,
        type: "POST",
        timeout: 120000,
        processData: false,
        contentType: false,
        success: function (resp) {
          console.log('stopMower Response : ' , resp);
          setTimeout(function(){ 
          $("#gif").hide(); }, 
          500);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
          console.log('stopMower Function encountered Error');
          $("#gif").hide();
        }
    });

}
