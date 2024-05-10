// Initialize the map with Chicago as the center
var map = L.map('map').setView({ Coordinates }, 13); // [latitude, longitude], zoom level

// Add a tile layer
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attribution">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
}).addTo(map);

// Loop through the stations and add a smaller marker for each
var stations_data = { stations };
var markers = L.markerClusterGroup();


for (var i = 0; i < stations_data.length; i++) {
    var station = stations_data[i];
    var marker = L.marker([station[0], station[1]]);
    markers.addLayer(marker);
};

map.addLayer(markers);


