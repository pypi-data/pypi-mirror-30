from abc import ABCMeta
from abc import abstractmethod
import os
import logging

from osgeo import ogr
from osgeo import gdal

from threedigrid.orm import constants
from threedigrid.orm.base.exceptions import DriverNotSupportedError

logger = logging.getLogger(__name__)


class BaseExporterObject:
    __metaclass__ = ABCMeta

    @abstractmethod
    def save(self):
        """
        exporter objects must implement the save method
        """
        pass


class BaseOgrExporter(BaseExporterObject):

    driver = None

    def set_driver(self, driver_name='', extension=''):
        assert any((driver_name, extension)), \
            'either driver_name or extension must be given'
        if not driver_name:
            driver_name = constants.EXTENSION_TO_DRIVER_MAP[extension.lower()]
        if all([driver_name == constants.GEO_PACKAGE_DRIVER_NAME,
                int(gdal.VersionInfo('VERSION_NUM')) < 2000000]):
            logger.error('Requires GDAL >= 2.0(dev)')
            raise DriverNotSupportedError('Requires GDAL >= 2.0(dev)')
        self.driver = ogr.GetDriverByName(str(driver_name))

    @property
    def driver_name(self):
        if self.driver:
            return self.driver.GetName()

    def del_datasource(self, file_name):
        if not os.path.exists(file_name):
            return
        logger.info('[*] Replacing %s ...', file_name)
        self.driver.DeleteDataSource(str(file_name))
