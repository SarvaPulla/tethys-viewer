from tethys_sdk.base import TethysAppBase, url_map_maker


class HydroshareShapefileViewer(TethysAppBase):
    """
    Tethys app class for HydroShare Shapefile Viewer.
    """

    name = 'HydroShare Shapefile Viewer'
    index = 'hydroshare_shapefile_viewer:home'
    icon = 'hydroshare_shapefile_viewer/images/logo.png'
    package = 'hydroshare_shapefile_viewer'
    root_url = 'hydroshare-shapefile-viewer'
    color = '#2ecc71'
        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='hydroshare-shapefile-viewer',
                           controller='hydroshare_shapefile_viewer.controllers.home'),
                    UrlMap(name='map',
                           url='hydroshare-shapefile-viewer/map',
                           controller='hydroshare_shapefile_viewer.controllers.map')
        )

        return url_maps