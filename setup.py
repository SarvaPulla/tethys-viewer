import os
import sys
from setuptools import setup, find_packages
from tethys_apps.app_installation import custom_develop_command, custom_install_command

### Apps Definition ###
app_package = 'hydroshare_shapefile_viewer'
release_package = 'tethysapp-' + app_package
app_class = 'hydroshare_shapefile_viewer.app:HydroshareShapefileViewer'
app_package_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tethysapp', app_package)

### Python Dependencies ###
dependencies = []

setup(
    name=release_package,
    version='1.0.0',
    description='View shapefiles from hydroshare.org',
    long_description='',
    keywords='',
    author='Sarva Pulla',
    author_email='pulla@byu.edu',
    url='www.hydroshare.org',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['tethysapp', 'tethysapp.' + app_package],
    include_package_data=True,
    zip_safe=False,
    install_requires=dependencies,
    cmdclass={
        'install': custom_install_command(app_package, app_package_dir, dependencies),
        'develop': custom_develop_command(app_package, app_package_dir, dependencies)
    }
)
