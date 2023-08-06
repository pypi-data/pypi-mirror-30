import collections

from parosm.types.osmtype import OSMBaseType


class Node(OSMBaseType):
    """
    OpenStreetMap Node Type
    """
    def __init__(self, identifier, lat, lon, **kwargs):
        """

        :param identifier: ID of object
        :param lat: latitude
        :param lon: longitude
        :param user: user name
        :param uid: user id
        :param timestamp: timestamp of last change
        :param visible: object visible?
        :param version: version of the object
        :param changeset: changeset id
        :param tags: dictionary with osm object tags
        """
        super().__init__(identifier=identifier, **kwargs)
        self._lat = lat
        self._lon = lon

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, val):
        self._lat = float(val)

    @property
    def lon(self):
        return self._lon

    @lon.setter
    def lon(self, val):
        self._lon = float(val)

    @property
    def coords(self):
        return self._lat, self._lon

    @coords.setter
    def coords(self, coords):
        if not isinstance(coords, collections.Iterable):
            raise TypeError('coords is not iterable')
        if len(coords) != 2:
            raise ValueError('coords does not have length 2')
        self._lat = float(coords[0])
        self._lon = float(coords[1])

    def __str__(self):
        attr_str = list()
        attr_str.append('(id={})'.format(self._id))
        attr_str.append('(lat={})'.format(self._lat))
        attr_str.append('(lon={})'.format(self._lon))
        if len(self._tags) > 0:
            attr_str.append('(tags={})'.format(self._tags))
        attr_str = ', '.join(attr_str)
        return 'Node<{}>;'.format(attr_str)
