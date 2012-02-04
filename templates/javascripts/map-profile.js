var map;

var map = new OpenLayers.Map('map', {
    controls: [
        new OpenLayers.Control.Navigation(),
        new OpenLayers.Control.ArgParser(),
        new OpenLayers.Control.Attribution()
    ]
});

var osm = new OpenLayers.Layer.OSM();

map.addLayers([osm]);

map.zoomToMaxExtent();

map.setCenter(new OpenLayers.LonLat(0,10), 8);

var panel = new OpenLayers.Control.Panel();