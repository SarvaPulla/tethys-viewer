from tethys_sdk.base import TethysAppBase, url_map_maker


class HydroshareShapefileViewer(TethysAppBase):
    """
    Tethys app class for HydroShare Shapefile Viewer.
    """

    name = 'HydroShare Geographic Feature Viewer'
    index = 'hydroshare_shapefile_viewer:home'
    icon = 'hydroshare_shapefile_viewer/images/icon.gif'
    package = 'hydroshare_shapefile_viewer'
    root_url = 'hydroshare-shapefile-viewer'
    color = '#2ecc71'
    description = 'View geographic feature files (shapefiles) that are stored in HydroShare.'
        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='hydroshare-shapefile-viewer',
                           controller='hydroshare_shapefile_viewer.controllers.home'),

                    UrlMap(name='draw_geog_feature',
                           url='draw-geog-feature',
                           controller='hydroshare_shapefile_viewer.controllers.draw_geog_feature'),
                    )



        return url_maps