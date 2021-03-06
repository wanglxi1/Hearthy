from hearthstone import enums
from hearthstone.enums import GameTag

from hearthy.protocol.utils import (
    TAG_CUSTOM_NAME, TAG_POWER_NAME, format_tag_name, format_tag_value
    )
from hearthy.exceptions import CardNotFound
from hearthy.db import cards

class EntityBase:
    def __init__(self, eid, tag_list):
        self._eid = eid
        self._tags = dict(tag_list)

    @property
    def id(self):
        return self._eid

    def __getitem__(self, tag):
        return self._tags.get(tag, None)

    def __contains__(self, tag):
        return tag in self._tags

    def __str__(self):
        # TODO: find a nice representation
        custom = self[TAG_CUSTOM_NAME]
        if custom:
            return '[{0!r}]'.format(custom)

        power = self[TAG_POWER_NAME]
        if power:
            try:
                cardname = cards.get_by_id(power)
            except CardNotFound:
                cardname = power
        else:
            cardname = '?'

        zone = self[GameTag.ZONE]
        if zone:
            where = enums.Zone(zone).name.capitalize()
        else:
            where = '?'

        whom = 'Player{0}'.format(self[GameTag.CONTROLLER])

        return '[{0}: {1!r} of {2} in {3}]'.format(self.id, cardname, whom, where)

class Entity(EntityBase):
    pass

class MutableEntity(EntityBase):
    def __setitem__(self, tag, value):
        self._tags[tag] = value

    def freeze(self):
        self.__class__ = Entity
        return self

class MutableView(EntityBase):
    def __init__(self, entity):
        self._e = entity
        self._eid = entity.id
        self._tags = dict()

    @property
    def id(self):
        return self._eid

    def __getitem__(self, tag):
        value = self._tags.get(tag, None)
        if value is None:
            value = self._e[tag]
        return value

    def __setitem__(self, tag, value):
        oldvalue = self[tag]
        if oldvalue != value:
            self._tags[tag] = value

    def __contains__(self, tag):
        return tag in self._tags or tag in self._e

    def __str__(self):
        ret = super().__str__()
        for key, val in self._tags.items():
            oldval = self._e[key]
            ret += ('\n\ttag {1}:{2} {3} -> {4}'.format(
                            self,
                            key,
                            format_tag_name(key),
                            format_tag_value(key, oldval) if oldval else '(unset)',
                            format_tag_value(key, val)))
        return ret

