# Copyright (c) Australian Astronomical Observatory (AAO), 2018.
#
# The Format Independent Data Interface for Astronomy (FIDIA), including this
# file, is free software: you can redistribute it and/or modify it under the terms
# of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, division, print_function, unicode_literals

from typing import List
import fidia

# Python Standard Library Imports

# Other Library Imports
import sqlalchemy as sa
from sqlalchemy.orm import relationship, reconstructor
from sqlalchemy.orm.collections import attribute_mapped_collection


# FIDIA Imports
import fidia.base_classes as bases
# from fidia.utilities import snake_case
# from .traits import TraitKey

# Set up logging
import fidia.slogging as slogging
log = slogging.getLogger(__name__)
log.setLevel(slogging.WARNING)
log.enable_console_logging()

__all__ = ['AstronomicalObject']


class AstronomicalObject(bases.SQLAlchemyBase):

    # Set up how Archive objects will appear in the MappingDB
    __tablename__ = "archive_objects"
    _db_id = sa.Column(sa.Integer, sa.Sequence('archive_seq'), primary_key=True)
    _db_object_class = sa.Column(sa.String)
    _db_archive_id = sa.Column(sa.Integer, sa.ForeignKey('archives._db_archive_id'))
    __mapper_args__ = {
        'polymorphic_on': '_db_object_class',
        'polymorphic_identity': 'AstronomicalObject'}

    archive = relationship('Archive')

    _identifier = sa.Column(sa.String(length=50))
    _ra = sa.Column(sa.Float)
    _dec = sa.Column(sa.Float)

    def __init__(self, sample, identifier=None, ra=None, dec=None):
        # type: (fidia.Sample, str, float, float) -> None
        if identifier is None:
            if ra is None or dec is None:
                raise Exception("Either 'identifier' or 'ra' and 'dec' must be defined.")
            self._identifier = "J{ra:3.6f}{dec:+2.4f}".format(ra=ra, dec=dec)
        else:
            self._identifier = identifier

        # Reference to the sample-like object containing this object.
        self.sample = sample

        # Dictionary of IDs for this object in the various archives attached
        # to the sample. @TODO: Initialised to None: must be populated
        # separately.
        # self._archive_id = {archive: None for archive in sample.archives}

        self._ra = ra
        self._dec = dec

        # Associate TraitPointer objects as necessary.
        self._trait_pointers = set()
        self.update_trait_pointers()

        super(AstronomicalObject, self).__init__()

    def __str__(self):
        return "FIDIA AstronomicalObject \"{}\"".format(self.identifier)

    def _repr_pretty_(self, p, cycle):
        p.text(self.__str__())

        p.break_()
        named_sub_traits = self.dir_named_sub_traits()
        if named_sub_traits:
            with p.group(8, " "*4 + "Named Traits:"):
                p.breakable()
                for name in named_sub_traits:
                    p.text(name)
                    p.breakable()


    def dir_named_sub_traits(self):
        # type: () -> List[str]
        """Return a directory of the Named SubTraits for this AstroObject, similar to what the builtin `dir()` does."""
        return list(set(self.sample.trait_mappings.keys(1)))

    @property
    def identifier(self):
        return self._identifier

    @property
    def ra(self):
        return self._ra

    @property
    def dec(self):
        return self._dec

    def update_trait_pointers(self):

        if not hasattr(self, '_trait_pointers'):
            self._trait_pointers = set()
            # This second check of initialization is necessary if the object has been restored from the database.

        from fidia.traits.trait_utilities import TraitPointer

        # Clear all existing pointers to TraitPointers
        while self._trait_pointers:
            # Set of tratit_pointers is not empty
            attr_name  = self._trait_pointers.pop()
            attr = getattr(self, attr_name)
            assert isinstance(attr, bases.TraitPointer)
            delattr(self, attr_name)

        log.debug("Creating Trait Pointers for AstroObject %s", self)
        if log.isEnabledFor(slogging.VDEBUG):
            message = str(self.sample.trait_mappings.as_nested_dict())
            log.vdebug("TraitMappings available: %s", message)
        for trait_type in self.sample.trait_mappings.keys(1):
            # pointer_name = snake_case(trait_mapping.trait_class.trait_class_name())
            log.debug("Adding TraitPointer '%s'", trait_type)
            self._trait_pointers.add(trait_type)
            setattr(self, trait_type, TraitPointer(trait_type, self.sample, self, self.sample.trait_mappings))

    def get_archive_id(self, archive):
        return self.sample.get_archive_id(archive, self._identifier)
