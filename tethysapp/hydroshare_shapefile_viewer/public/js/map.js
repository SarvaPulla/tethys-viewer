
var popupDiv = $('#error-popup');
var popupDiv_welcome = $('#welcome-popup');

var map_zoom = 6;
var openstreet_layer = new ol.layer.Tile({
          source: new ol.source.OSM()
        });

var hs_layer_tiled;
var hs_layer_single_tile;

var sld_body_temple_polygon = '<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0.0" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd">'
    +'<NamedLayer><Name>_WS_AND_LAYER_NAME_</Name><UserStyle><Name>mysld</Name><Title>Polygon with default label</Title>'
    +'<FeatureTypeStyle><Rule><PolygonSymbolizer><Fill><CssParameter name="fill">#AAAAAA</CssParameter></Fill><Stroke><CssParameter name="stroke">#000000</CssParameter><CssParameter name="stroke-width">1</CssParameter></Stroke></PolygonSymbolizer>'
    +'<TextSymbolizer><Geometry><ogc:Function name="centroid"><ogc:PropertyName>the_geom</ogc:PropertyName></ogc:Function></Geometry><Label><ogc:PropertyName>_LABLE_FIELD_NAME_</ogc:PropertyName></Label></TextSymbolizer></Rule></FeatureTypeStyle></UserStyle></NamedLayer></StyledLayerDescriptor>'

var sld_body_temple_point = '<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0.0" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd">'
    +'<NamedLayer><Name>_WS_AND_LAYER_NAME_</Name><UserStyle><Name>mysld</Name><Title>Point with default label</Title>'
    +'<FeatureTypeStyle><Rule><PointSymbolizer><Graphic><Mark><WellKnownName>square</WellKnownName><Fill><CssParameter name="fill">#FF0000</CssParameter></Fill></Mark><Size>6</Size></Graphic></PointSymbolizer>'
    +'<TextSymbolizer><Label><ogc:PropertyName>_LABLE_FIELD_NAME_</ogc:PropertyName></Label>'
    +'<LabelPlacement><PointPlacement><AnchorPoint><AnchorPointX>0.5</AnchorPointX><AnchorPointY>0.0</AnchorPointY></AnchorPoint><Displacement><DisplacementX>0</DisplacementX><DisplacementY>5</DisplacementY></Displacement></PointPlacement></LabelPlacement>'
    +'</TextSymbolizer></Rule></FeatureTypeStyle></UserStyle></NamedLayer></StyledLayerDescriptor>'

var sld_body_temple_line = '<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.0.0" xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd">'
    +'<NamedLayer><Name>_WS_AND_LAYER_NAME_</Name><UserStyle><Name>mysld</Name><Title>Point with default label</Title>'
    +'<FeatureTypeStyle><Rule><LineSymbolizer><Stroke><CssParameter name="stroke">#0000FF</CssParameter></Stroke></LineSymbolizer>'
    +'<TextSymbolizer><Label><ogc:PropertyName>_LABLE_FIELD_NAME_</ogc:PropertyName></Label>'
    +'<LabelPlacement><PointPlacement><AnchorPoint><AnchorPointX>0.5</AnchorPointX><AnchorPointY>0.0</AnchorPointY></AnchorPoint><Displacement><DisplacementX>0</DisplacementX><DisplacementY>5</DisplacementY></Displacement></PointPlacement></LabelPlacement>'
    +'</TextSymbolizer></Rule></FeatureTypeStyle></UserStyle></NamedLayer></StyledLayerDescriptor>'

var layer_id;
var json_response;
var geo_type;

slc_lonlat = [-111.8833, 40.75];
san_fran_lonlat = [-122.4167, 37.7833];
slc_3857 = ol.proj.transform(slc_lonlat, 'EPSG:4326', 'EPSG:3857');
san_fran_3857 = ol.proj.transform(san_fran_lonlat, 'EPSG:4326', 'EPSG:3857');

function refreshmap()
{
    if (map!=null && hs_layer_single_tile!=null)
    {

        var field_dropdown = document.getElementsByName('field-dropdown')[0];
        var field_name = field_dropdown.options[field_dropdown.selectedIndex].value

        if (geo_type == "point")
        {
            sld_body = sld_body_temple_point
        }
        else if (geo_type == "line")
        {
            sld_body = sld_body_temple_line
        }
        else if (geo_type == "polygon")
        {
            sld_body = sld_body_temple_polygon
        }

        console.log("geo_type:", geo_type)
        sld_body = sld_body.replace("_WS_AND_LAYER_NAME_", layer_id);
        sld_body = sld_body.replace("_LABLE_FIELD_NAME_", field_name);

        console.log(sld_body)


        var oseamNew = hs_layer_tiled.getSource();
	    oseamNew.updateParams({'sld_body': sld_body});
	    map.render();
    }
}

function resetmap()
{
    if (map!=null && hs_layer_tiled!=null)
    {
        var oseamNew = hs_layer_tiled.getSource();
	    var original_sld = "point"
        if (geo_type == "point")
        {
            original_sld = 'point'
        }
        else if (geo_type == "line")
        {
            original_sld = 'line'
        }
        else if (geo_type == "polygon")
        {
            original_sld = 'polygon'
        }
        oseamNew.updateParams({'styles': original_sld, 'sld_body': null});
	    map.render();
    }
}

function format_coord(coord)
{
    func1 = ol.coordinate.createStringXY(4)
    lon_lat_str = func1(coord)
    var lon_lat_array = lon_lat_str.split(",");
    output = "Lon = " + lon_lat_array[0] + ", Lat = " + lon_lat_array[1]

    return output
}


function removeOptions(selectbox){
    for(var i=selectbox.options.length-1; i>=0; i--)
    {
        selectbox.remove(i);
    }
}


var mousePositionControl = new ol.control.MousePosition({
        className: 'custom-mouse-position',
        projection: 'EPSG:4326',
        target: document.getElementById('location'),
        coordinateFormat: format_coord,
        undefinedHTML: 'Lon = NaN, Lat = NaN'
      });

var map = new ol.Map({
	layers: [ openstreet_layer],
    controls: ol.control.defaults({
          attribution: false
        }).extend([mousePositionControl]),
	target: 'map',
	view: new ol.View({
		center: san_fran_3857,
		zoom: map_zoom,
        projection: "EPSG:3857"
	})
});

map.getView().on('change:resolution', function(evt) {
        var resolution = evt.target.get('resolution');
        var units = map.getView().getProjection().getUnits();
        var dpi = 25.4 / 0.28;
        var mpu = ol.proj.METERS_PER_UNIT[units];
        var scale = resolution * mpu * 39.37 * dpi;
        if (scale >= 9500 && scale <= 950000) {
          scale = Math.round(scale / 1000) + "K";
        } else if (scale >= 950000) {
          scale = Math.round(scale / 1000000) + "M";
        } else {
          scale = Math.round(scale);
        }

        document.getElementById('scale').innerHTML = "Scale = 1 : " + scale;
      });


//map.on('singleclick', function(evt) {
//        document.getElementById('nodelist').innerHTML = "Loading... please wait...";
//        var view = map.getView();
//        var viewResolution = view.getResolution();
//        var source = hs_layer_tiled.get('visible') ? hs_layer_tiled.getSource() : null;
//        if (source != null)
//        {
//          //  var url = source.getGetFeatureInfoUrl(
//          //evt.coordinate, viewResolution, view.getProjection(),
//          //{'INFO_FORMAT': 'application/json', 'FEATURE_COUNT': 3});
//
//            var url = source.getGetFeatureInfoUrl(
//          evt.coordinate, viewResolution, view.getProjection(),
//          {'INFO_FORMAT': 'text/html', 'FEATURE_COUNT': 5});
//            console.log(url)
//            if (url) {
//
//
//              document.getElementById('nodelist').innerHTML = '<iframe seamless src="' + url + '"></iframe>';
//            }
//        }
//      });


$('#btn-testing-url').on('click', function () {
        res_id = $('#res-id').val()
        window.location = "/apps/hydroshare-shapefile-viewer/?src=hs&usr=demo&res_id=" + res_id
});

$(document).ready(function () {

    chkbox = create_check_box("basemap", "basemap", "Base Map", true, chkbox_callback)
    document.getElementById('layer_control_div').appendChild(chkbox);
    var br = document.createElement('br');
    document.getElementById('layer_control_div').appendChild(br);

    if ($('#success_flag').text().indexOf("true") > -1)
    {
        var wait_text = "<br><strong>Loading data...</strong><br>" +
        "<img src='/static/hydroshare_shapefile_viewer/images/globe_spinning_small.gif'>";
        document.getElementById('data_loading_div').innerHTML = wait_text;

        $.ajax({
            type: 'GET',
            url: 'draw-geog-feature',
            dataType: 'json',
            data: {
                'ok': 'ok'
            },
            success: function (data) {

                if (data["success"])
                {
                    document.getElementById('data_loading_div').innerHTML = "";
                    var geosvr_url_base = data["geosvr_url_base"];
                    var ws_name = data["ws_name"];
                    var store_name = data["store_name"];
                    var layer_name = data["layer_name"];
                    var minx = data["minx"];
                    var miny = data["miny"];
                    var maxx = data["maxx"];
                    var maxy = data["maxy"];
                    console.log("minx", minx, "maxx", maxx, "miny", miny, "maxy", maxy);

                    json_response = data["json_response"]

                    chkbox = create_check_box("geog-feature", "geog-feature", "Geographic Feature Resource Layer", true, chkbox_callback)
                    document.getElementById('layer_control_div').appendChild(chkbox);
                    var br = document.createElement('br');
                    document.getElementById('layer_control_div').appendChild(br);

                    var field_dropdown = document.getElementsByName('field-dropdown')[0];
                    removeOptions(field_dropdown);
                    var field_array = json_response.featureType.attributes.attribute;
                    for (var i=0;i<field_array.length; i++)
                    {
                        var field_name = field_array[i].name;
                        if (field_name.toLowerCase() == "the_geom" || field_name.toLowerCase() == "geom")
                        {
                            var geo_type_json = field_array[i].binding.toLowerCase();
                            console.log("geo_type_json", geo_type_json)
                            if (geo_type_json.indexOf("point") > -1)
                            {
                                geo_type = "point"
                            }
                            else if (geo_type_json.indexOf("line") > -1)
                            {
                                geo_type = "line"
                            }
                            else if (geo_type_json.indexOf("polygon") > -1)
                            {
                                geo_type = "polygon"
                            }
                            else
                            {
                                geo_type=null;
                            }
                            continue;
                        }
                        var opt = document.createElement('option');
                        opt.value = field_name;
                        opt.innerHTML = field_name;
                        field_dropdown.appendChild(opt);
                    }
                    draw_geog_feature_layer(geosvr_url_base, ws_name, store_name, layer_name, minx, miny, maxx, maxy, json_response)
                }
                else
                {
                    popup_title = data["popup_title"]
                    popup_content = data["popup_content"]
                    $('#error-title').html(popup_title)
                    $('#error-info').html(popup_content)
                    popupDiv.modal("show")

                    //alert(popup_content)
                    document.getElementById('data_loading_div').innerHTML = "";
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                $('#error-title').html("Error")
                $('#error-info').html("Looks like this is a large size geographic feature resource. Please try refreshing this page later.")
                popupDiv.modal("show")
                console.log(textStatus, errorThrown);
                document.getElementById('data_loading_div').innerHTML = "";
            }
        }); //$.ajax
    } // if
    else if ($('#success_flag').text().indexOf("welcome") > -1)
    {
        popupDiv_welcome.modal('show');
    }
    else // false
    {
        popupDiv.modal('show');
    }

}) // $(document).ready(function ()


function create_check_box(name, vaule, text, check_state, fn_callback)
{
    // styling of this checkbox control is at raster_viewer/public/css/main.css
    var label= document.createElement("label");
    var description = document.createTextNode(text);
    var checkbox = document.createElement("input");

    checkbox.type = "checkbox";    // make the element a checkbox
    checkbox.name = name;      // give it a name we can check on the server side
    checkbox.value = vaule;         // make its value "pair"
    checkbox.checked = check_state;
    checkbox.addEventListener('change', fn_callback);

    label.appendChild(checkbox);   // add the box to the element
    label.appendChild(description);// add the description to the element
    return label
}

function chkbox_callback(evt){

    var checkbox = evt.target;
    if (checkbox.name == "basemap")
    {
        openstreet_layer.setVisible(checkbox.checked)
    }
    else if (checkbox.name == "geog-feature") {
        if (hs_layer_tiled != null) {
            hs_layer_tiled.setVisible(checkbox.checked)
        }
    }
}


function draw_geog_feature_layer (geosvr_url_base, ws_name, store_name, layer_name, minx, miny, maxx, maxy, json_response)
{

    if(geo_type == null)
    {
        $('#label-panel').css('visibility', 'hidden');
    }
    else
    {
        $('#label-panel').css('visibility', 'visible');
    }
    var field_dropdown = document.getElementsByName('field-dropdown')[0];
    if (field_dropdown.options.length<1)
    {
        $('#label-panel').css('visibility', 'hidden');
    }


    geo_server_wms = geosvr_url_base + '/geoserver/wms'
    layer_id = ws_name + ':' + layer_name
    extent_4326 = [minx, miny, maxx, maxy]
    extent_3857 = ol.proj.transformExtent(extent_4326, 'EPSG:4326', 'EPSG:3857')
    center_3857 =[(extent_3857[0]+extent_3857[2])/2, (extent_3857[1]+extent_3857[3])/2]

    hs_layer_tiled = new ol.layer.Tile({
      source: new ol.source.TileWMS({
      url: geo_server_wms,
      params: {'LAYERS': layer_id,
               'TILED': true},
      serverType: 'geoserver' }) })


    hs_layer_single_tile = new ol.layer.Image({
        source: new ol.source.ImageWMS({
          ratio: 1,
          url: geo_server_wms,
          params: {
                LAYERS: layer_id,
                //STYLES: 'my_sld',
                //sld: 'http://127.0.0.1:8080/geoserver/www/styles/sld.sld'
                //"sld_body": sld_body
                  }
        })
      });

    // map.addLayer(hs_layer_single_tile)
    map.addLayer(hs_layer_tiled);
    map.getView().setCenter(center_3857);

    if (Math.abs(maxx - minx) < 100)
    {
        map.getView().setZoom(8);
        map.getView().setCenter(center_3857);
    }
    else
    {
        map.getView().setZoom(4);
        map.getView().setCenter(san_fran_3857);
    }
}