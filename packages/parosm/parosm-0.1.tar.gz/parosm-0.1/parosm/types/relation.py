from parosm.types.osmtype import OSMBaseType


class Relation(OSMBaseType):
    def __init__(self, identifier, members=None, **kwargs):
        """

        :param identifier: Object ID
        :param members: Dict[id: Tuple[MemberType, Role]]
        :param user: user name
        :param uid: user id
        :param timestamp: timestamp of last change
        :param visible: object visible?
        :param version: version of the object
        :param changeset: changeset id
        :param tags: dictionary with osm object tags
        """
        super().__init__(identifier, **kwargs)
        self._members = dict() if members is None else members

    def add_member(self, identifier, mtype, role):
        self._members[identifier] = (mtype, role)

    @property
    def members(self):
        for identifier, (mtype, role) in self._members.items():
            yield (identifier, mtype, role)

    def __str__(self):
        attr_str = list()
        attr_str.append('(id={})'.format(self._id))
        attr_str.append('(members={})'.format(len(self._members)))
        if len(self._tags) > 0:
            attr_str.append('(tags={})'.format(self._tags))
        attr_str = ', '.join(attr_str)
        return 'Relation<{}>;'.format(attr_str)
