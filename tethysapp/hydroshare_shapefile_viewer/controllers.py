import random,string,tempfile,shutil,os
from django.shortcuts import render
import urllib2
import zipfile
try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO
from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from tethys_dataset_services.engines import GeoServerSpatialDatasetEngine
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from utilities import *
from django.template.defaulttags import csrf_token
from tethys_sdk.services import *
from tethys_sdk.services import get_spatial_dataset_engine
from tethys_sdk.gizmos import MapView, MVDraw, MVView, MVLayer, MVLegendClass
from tethys_sdk.gizmos import SelectInput



url_base='http://{0}.hydroshare.org/hsapi/resource/{1}/files/{2}/'

# Default Geoserver Url
geosvr_url_base='http://127.0.0.1:8181'

def home(request):
    """
    Controller for the app home page.
    """

    geoserver_engine = get_spatial_dataset_engine(name='default_geoserver')
    response = geoserver_engine.list_workspaces()


    context = {}

    return render(request, 'hydroshare_shapefile_viewer/home.html', context)

def map(request):
    """
    Controller for the map page
    """
 # Getting all the necessary variables for initiating the process of adding a file to the Geoserver

    """
    Controller for the map page

    """
    try:
        filename= request.POST['filename']
        res_id= request.POST['resource_id']
        branch= request.POST['branch']

        WORKSPACE = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        GEOSERVER_URI = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))


        geoserver_engine = get_spatial_dataset_engine(name='default_geoserver')
        response = geoserver_engine.list_workspaces()

        if response['success']:
            workspaces = response['result']

            if WORKSPACE not in workspaces:
                response = geoserver_engine.create_workspace(workspace_id=WORKSPACE,
                                                             uri=GEOSERVER_URI)
                print response




         # make a temp directory
        temp_dir = tempfile.mkdtemp()
        print "temp folder created at " + temp_dir

        # The url format for identifying the HydroShare resource file
        url_wml = url_base.format(branch,res_id,filename)
        print "HS_REST_API: " + url_wml

         # Opening the url

        response = urllib2.urlopen(url_wml)
        print "downloading " + url_wml
        shp_obj = response.read()
        print "download complete"

        # Downloading the file from HydroShare and then adding it to the temp dir
        zipped_shp_full_path = temp_dir + "/"+ filename
        # Saving the zip file to the temp dir
        f = file(zipped_shp_full_path, "w")
        # Writes the mem space 'in_memory_zip' to a file.
        f.write(shp_obj)
        f.close()

        zip_crc=None

        # Unzipping the file as adding a shpfile to Geosrvr requires you to upload a shpfile only
        # This is a problem with the tethys functionality. Once that is fixed, this step will not be necessary
        with zipfile.ZipFile(zipped_shp_full_path, "r") as z:
            z.extractall(temp_dir)
            #zip_info = z.getinfo(filename[:-3]+'shp')
            #zip_crc1 = str(zip_info.CRC)
            #print "CRC: " + zip_crc1
            #zip_crc=zip_crc1

        print geosvr_url_base

        # Specifying the folder with the shapefiles. It is formatted this way for tethys' sake. filname[:-4] removes
        # everything .zip
        #zip_file_full_path= temp_dir + '/'+filename[:-4]
        zip_file_full_path= temp_dir + '/'+filename

        store = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(6))
        store_id = WORKSPACE + ':' + store
        response2 = geoserver_engine.create_shapefile_resource(
                        store_id=store_id,
                        shapefile_zip=zip_file_full_path,
                        overwrite=True,
                        debug=True
            )

        print response2

        response3 = geoserver_engine.list_layers(with_properties=True)

        options  =[]

        if response3['success']:
            for layer in response3['result']:
                resource_name = layer['resource']
                if WORKSPACE in resource_name:
                    options.append((resource_name, resource_name))

        map_layers = []


        geoserver_layer = MVLayer(
            source='ImageWMS',
            options={'url': 'http://127.0.0.1:8181/geoserver/wms',
                   'params': {'LAYERS': options},
                   'serverType': 'geoserver'},
            legend_title=filename,
            legend_extent=[-114, 36.5, -109, 42.5],
            legend_classes=[
                MVLegendClass('polygon', 'County', fill='#999999'),
        ])

        map_layers.append(geoserver_layer)


        view_options = MVView(
            projection='EPSG:4326',
            center=[-100, 40],
            zoom=4,
            maxZoom=18,
            minZoom=2
        )

        map_options = MapView(height='500px',
                              width='100%',
                              layers=map_layers,
                              legend=True,
                              view=view_options)
    except:
        raise Http404("Cannot locate the requested shapefile. Please check your URL and try again.")


    finally:
        if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                temp_dir=None




    context = {'map_options': map_options}




    return render(request, 'hydroshare_shapefile_viewer/map.html', context)





