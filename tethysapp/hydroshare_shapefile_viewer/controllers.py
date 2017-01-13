import tempfile
import shutil
import os
import logging
import zipfile

from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse

from oauthlib.oauth2 import TokenExpiredError
from hs_restclient import HydroShare, HydroShareAuthOAuth2, HydroShareNotAuthorized, HydroShareNotFound
from utilities import *

logger = logging.getLogger(__name__)
try:
    from tethys_services.backends.hs_restclient_helper import get_oauth_hs
except ImportError:
    logger.error("could not load: tethys_services.backends.hs_restclient_helper import get_oauth_hs")

geoserver_workspace_name = "geo_feature_viewer"

###########
geosvr_url_base = getattr(settings, "GEOSERVER_URL_BASE", "http://127.0.0.1:8181")
geosvr_user = getattr(settings, "GEOSERVER_USER_NAME", "admin")
geosvr_pw = getattr(settings, "GEOSERVER_USER_PASSWORD", "geoserver")

hs_instance_name = "www"
target_res_type = "geographicfeatureresource"

hs_hostname = "{0}.hydroshare.org".format(hs_instance_name)

###########
popup_title_WELCOME = "Welcome to the HydroShare Geographic Feature Viewer"
popup_title_ERROR = "Error"
popup_title_WARNING = "Warning"

popup_content_NOT_LAUNCHED_FROM_HYDROSHARE = "This app should be launched from <a href='https://www.hydroshare.org/my-resources/'>HydroShare</a>."
popup_content_UNKNOWN_ERROR = "Sorry, we are having an internal error!"
popup_content_NO_PERMISSION = "Sorry, you have no permission on this resource."
popup_content_NOT_FOUND = "Sorry, we cannot find this resource on HydroShare."
popup_content_ANONYMOUS_USER = "Please <a href='https://www.hydroshare.org/accounts/login/'>sign in HydroShare</a> and then launch this app again."
popup_content_TOKEN_EXPIRED = "Login timed out! Please <a href='/oauth2/login/hydroshare'>sign in with your HydroShare account</a> again."
popup_content_NOT_OAUTH_LOGIN = "Please sign out and re-sign in with your HydroShare account."
popup_content_NOT_GEOG_FEATURE_RESOURCE = "Sorry, this resource is not a HydroShare Geographic Feature Resource."
popup_content_NO_RESOURCEID_IN_SESSION = "Sorry, the resource id is missing."
popup_content_INVALID_GEOTIFF = "This resource file is not a valid ESRI Shapefile or has no projection information."

extract_base_path = '/tmp'

#Normal Get or Post Request
#http://dev.hydroshare.org/hsapi/resource/72b1d67d415b4d949293b1e46d02367d/files/referencetimeseries-2_23_2015-wml_2_0.wml/

# geotiff Name: geotiff.tif
# zip File Name: zipFile.zip
# workspace Name: ws
# storeName: store
# store_id="ws:store"
#
# spatial_dataset_engine.create_coverage_resource(store_id=store_id, coverage_file=zipFile.zip, coverage_type='geotiff')
#
# Create 1:
# /var/lib/geoserver/data/data/ws/store/geotiff.tif
#
# Create 2:
# /var/lib/geoserver/data/workspaces/ws/store/coveragestore.xml
# /var/lib/geoserver/data/workspaces/ws/store/geotiff/coverage.xml
# /var/lib/geoserver/data/workspaces/ws/store/geotiff/layer.xml
#
# Create 3:
# geoserver layer resource name: geotiff
#
# Conclusion:
# 1)Zip file name 'zipFile.zip' does not matter.But the embed tif file name (without extension) 'geotiffwill' be used for Layer Name.
# 2)Store name 'store' should be unique in one workspace. Ex. same store names with different zipfile or geotif cannot cannot be used for creating new layer resource


def home(request):

    # import sys
    # sys.path.append("/home/drew/pycharm-debug")
    # import pydevd
    # pydevd.settrace('172.17.42.1', port=21000, suspend=False)

    print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    popup_title = popup_title_WELCOME
    popup_content = popup_content_NOT_LAUNCHED_FROM_HYDROSHARE
    success_flag = "true"
    resource_title = None

    if request.GET:
        res_id = request.GET.get("res_id", None)
        src = request.GET.get('src', None)
        usr = request.GET.get('usr', None)

        if res_id is None or src is None or src != "hs" or usr is None:
            success_flag = "welcome"
        elif usr.lower() == "anonymous":
            popup_title = popup_title_ERROR
            popup_content = popup_content_ANONYMOUS_USER
            success_flag = "false"
        else:
            request.session['res_id'] = res_id
            request.session['src'] = src
            request.session['usr'] = usr
            try:
                # res_id = "b7822782896143ca8712395f6814c44b"
                # res_id = "877bf9ed9e66468cadddb229838a9ced"
                # res_id = "e660640a7b084794aa2d70dc77cfa67b"
                # private res
                # res_id = "a4a4bca8369e4c1e88a1b35b9487e731"
                # request.session['res_id'] = res_id

                hs = get_oauth_hs(request)
                global hs_hostname
                hs_hostname = hs.hostname

                resource_md = hs.getSystemMetadata(res_id)
                resource_type = resource_md.get("resource_type", "")
                resource_title = resource_md.get("resource_title", "")

                if resource_type.lower() != target_res_type:
                    popup_title = popup_title_ERROR
                    popup_content = popup_content_NOT_GEOG_FEATURE_RESOURCE
                    success_flag = "false"
                    logger.debug(resource_type.lower())

            except ObjectDoesNotExist as e:
                logger.exception(e.message)
                popup_title = popup_title_ERROR
                popup_content = popup_content_NOT_OAUTH_LOGIN
                success_flag = "false"
            except TokenExpiredError as e:
                logger.exception(e.message)
                popup_title = popup_title_WARNING
                popup_content = popup_content_TOKEN_EXPIRED
                success_flag = "false"

            except HydroShareNotAuthorized as e:
                logger.exception (e.message)
                popup_title = popup_title_ERROR
                popup_content = popup_content_NO_PERMISSION
                success_flag = "false"

            except HydroShareNotFound as e:
                logger.exception(e.message)
                popup_title = popup_title_ERROR
                popup_content = popup_content_NOT_FOUND
                success_flag = "false"
            except Exception as e:
                logger.error("unknown error")
                logger.exception(e.message)
                popup_title = popup_title_ERROR
                popup_content = popup_content_UNKNOWN_ERROR
                success_flag = "false"
                # raise
    else:
        success_flag = "welcome"

    context = {"popup_title": popup_title,
               "popup_content": popup_content,
               "success_flag": success_flag,
               'resource_title': resource_title,
            }

    return render(request, 'hydroshare_shapefile_viewer/home.html', context)

def draw_geog_feature(request):

    res_id = request.session.get("res_id", None)
    temp_res_extracted_dir = None
    temp_dir = None
    map_dict = {}
    map_dict["success"] = False

    try:
        if res_id is not None:

            map_dict = getMapParas(geosvr_url_base=geosvr_url_base, wsName=geoserver_workspace_name, store_id=res_id, \
                        layerName=res_id, un=geosvr_user, pw=geosvr_pw)

            if map_dict["success"]: # find cached raster
               logger.debug("find cached layer on geoserver")

            else: # no cached raster or raster has no projection

                hs = get_oauth_hs(request)
                global hs_hostname
                hs_hostname = hs.hostname
                logger.debug("Begin download res: {0}".format(res_id))
                hs.getResource(res_id, destination=extract_base_path, unzip=True)
                logger.debug ("End download res")
                temp_res_extracted_dir = extract_base_path + '/' + res_id
                logger.debug(temp_res_extracted_dir)
                contents_folder = extract_base_path + '/' + res_id + '/' + res_id +'/data/contents/'
                logger.debug(contents_folder)
                file_list = os.listdir(contents_folder)


                for fn in file_list:
                    logger.debug(fn)

                temp_dir = tempfile.mkdtemp()
                zip_file_full_path = temp_dir + "/" + "zip_shapefile.zip"

                with zipfile.ZipFile(zip_file_full_path, 'a') as myzip:
                    for fn in file_list:
                        shapefile_fp = contents_folder + fn # tif full path
                        new_file_name = res_id + os.path.splitext(fn)[1]
                        myzip.write(shapefile_fp, arcname=new_file_name)


                rslt = addZippedShapefile2Geoserver(geosvr_url_base=geosvr_url_base, uname=geosvr_user, upwd=geosvr_pw, ws_name=geoserver_workspace_name, \
                                              store_name=res_id, zippedTif_full_path=zip_file_full_path, res_url='appsdev.hydroshare.org/apps/hydroshare-shapefile-viewer')
                if(rslt):
                    map_dict = getMapParas(geosvr_url_base=geosvr_url_base, wsName=geoserver_workspace_name, store_id=res_id, \
                                                   layerName=res_id, un=geosvr_user, pw=geosvr_pw)

            map_dict['geosvr_url_base'] = geosvr_url_base
            map_dict['ws_name'] = geoserver_workspace_name
            map_dict['store_name'] = res_id
            map_dict['layer_name'] = res_id
            if map_dict["success"] == False:
                map_dict['popup_title'] = popup_title_ERROR
                map_dict['popup_content'] = popup_content_INVALID_GEOTIFF

        else:
            map_dict["success"] = False
            map_dict['popup_title'] = popup_title_ERROR
            map_dict['popup_content'] = popup_content_NO_RESOURCEID_IN_SESSION


    except ObjectDoesNotExist as e:
        logger.exception(e.message)
        popup_title = popup_title_ERROR
        popup_content = popup_content_NOT_OAUTH_LOGIN
        map_dict["success"] = False
        map_dict['popup_title'] = popup_title
        map_dict['popup_content'] = popup_content
    except TokenExpiredError as e:
        logger.exception(e.message)
        popup_title = popup_title_WARNING
        popup_content = popup_content_TOKEN_EXPIRED
        map_dict["success"] = False
        map_dict['popup_title'] = popup_title
        map_dict['popup_content'] = popup_content

    except HydroShareNotAuthorized as e:
        logger.exception(e.message)
        popup_title = popup_title_ERROR
        popup_content = popup_content_NO_PERMISSION
        map_dict["success"] = False
        map_dict['popup_title'] = popup_title
        map_dict['popup_content'] = popup_content

    except HydroShareNotFound as e:
        logger.exception(e.message)
        popup_title = popup_title_ERROR
        popup_content = popup_content_NOT_FOUND
        map_dict["success"] = False
        map_dict['popup_title'] = popup_title
        map_dict['popup_content'] = popup_content
    except Exception as e:
        logger.error ("unknown error")
        logger.exception(e.message)
        popup_title = popup_title_ERROR
        popup_content = popup_content_UNKNOWN_ERROR
        map_dict["success"] = False
        map_dict['popup_title'] = popup_title
        map_dict['popup_content'] = popup_content
        # raise
    finally:
        if temp_dir is not None:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                logger.debug (temp_dir + " deleted")
        if temp_res_extracted_dir is not None:
            if os.path.exists(temp_res_extracted_dir):
                shutil.rmtree(temp_res_extracted_dir)
                logger.debug(temp_res_extracted_dir + " deleted")
        return JsonResponse(map_dict)



def login_callback(request):

    context = {}
    if request.user.is_authenticated():
        context["login"] = "yes"
    else:
        context["login"] = "no"

    return render(request, 'hydroshare_shapefile_viewer/login_callback.html', context)