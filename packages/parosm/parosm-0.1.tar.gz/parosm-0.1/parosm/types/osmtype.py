"""
Includes the basic OpenStreetMap types
"""


class OSMBaseType:
    """
    OSM Base type bundles attributes that are shared
    by all OSM types

    :param identifier: object id
    :param user: user name
    :param uid: user id
    :param timestamp: timestamp of last change
    :param visible: object visible?
    :param version: version of the object
    :param changeset: changeset id
    :param tags: dictionary with osm object tags
    """
    def __init__(self,
                 identifier,
                 user=None,
                 uid=None,
                 timestamp=None,
                 visible=None,
                 version=0,
                 changeset=0,
                 tags=None, **kwargs):
        self._id = identifier
        self._user = "" if user is None else user
        self._uid = 0 if uid is None else uid
        self._timestamp = "" if timestamp is None else timestamp
        self._visible = "false" if visible is None else visible
        self._version = 0 if version is None else version
        self._changeset = 0 if changeset is None else changeset
        self._tags = dict() if tags is None else tags

    def add_tag(self, key, value):
        """
        add tag to object
        :param key: key name
        :param value:
        """
        self._tags[key] = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, identifier):
        self._id = identifier

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, user):
        self._user = user

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, uid):
        self._uid = uid

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, ts):
        self._timestamp = ts

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, v):
        if not isinstance(v, str):
            raise TypeError('argument not a string')
        if v.lower() == 'false':
            self._visible = 'false'
        elif v.lower() == 'true':
            self._visible = 'true'
        else:
            raise ValueError('Visible is either "true" or "false"')

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, v):
        self._version = v

    @property
    def changeset(self):
        return self._changeset

    @changeset.setter
    def changeset(self, cs):
        self._changeset = cs

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, tags):
        if not isinstance(tags, dict):
            raise TypeError('tags should be type <dict>')
        for key, value in tags:
            self._tags[key] = value


class OSM:
    """
    Basic OSM Element including the bounding box
    """
    def __init__(self, version, bbox=None):
        """
        Initialize bounding box
        :param version: Version of open street map
        :param bbox: dict[minlat, minlon, maxlat, maxlon]
        """
        self._version = version
        self._bounds = {
            'minlat': None,
            'minlon': None,
            'maxlat': None,
            'maxlon': None
        }
        if bbox is not None:
            self.set_bounds(**bbox)

    def set_bounds(self,
                   minlat=None,
                   minlon=None,
                   maxlat=None,
                   maxlon=None):
        """
        Set bounding box
        :param minlat: Y-min
        :param minlon: X-min
        :param maxlat: Y-max
        :param maxlon: X-max
        """
        self._bounds['minlat'] = minlat
        self._bounds['minlon'] = minlon
        self._bounds['maxlat'] = maxlat
        self._bounds['maxlon'] = maxlon

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    @property
    def bounds(self):
        return self._bounds

    @bounds.setter
    def bounds(self, bounds):
        if not isinstance(bounds, dict):
            raise TypeError('argument is not a dict')
        keys = ['minlat', 'maxlat', 'minlon', 'maxlon']
        for key, value in bounds.items():
            if key in keys:
                self._bounds[key] = value
        for key in keys:
            if key not in bounds:
                raise ValueError('{} not specified')

    def __str__(self):
        attr_str = list()
        attr_str.append('(version={})'.format(self._version))
        for key, value in self._bounds.items():
            attr_str.append('({}={})'.format(key, value))
        attr_str = ', '.join(attr_str)

        return 'OSM<{}>'.format(attr_str)
