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

import os
import tempfile

import numpy as np

import pytest

import fidia
from fidia.exceptions import *
from fidia.archive.archive import BasePathArchive
from fidia.archive.example_archive import ExampleArchive
from fidia.column.column_definitions import FITSDataColumn, FixedValueColumn
from fidia.column.columns import FIDIAColumn
from fidia.traits import TraitMapping, TraitPropertyMapping, TraitCollection

# Pytest fixture 'test_data_dir' now session wide and stored in conftest.py
# @pytest.yield_fixture(scope='module')
# def test_data_dir():
#     with tempfile.TemporaryDirectory() as tempdir:
#         testdata.generate_simple_dataset(tempdir, 5)
#
#         yield tempdir


class TestArchiveAndColumns:
    @pytest.fixture
    def ArchiveWithColumns(self):

        my_column = FixedValueColumn("data",
                                     ndim=2,
                                     timestamp=1)


        class ArchiveWithColumns(fidia.ArchiveDefinition):

            # For general testing, this should be set to True (commented out)
            # For testing of the system without database persistence, it should be False.
            # is_persisted = False


            archive_id = "testArchive"

            contents = ["Gal1"]

            archive_type = BasePathArchive

            column_definitions = fidia.ColumnDefinitionList([
                ("col", my_column),
                (FITSDataColumn("{object_id}/{object_id}_red_image.fits", 0,
                                ndim=2,
                                timestamp=1))

            ])

            trait_mappings = [
                TraitMapping(TraitCollection, "trait", [
                    TraitPropertyMapping("direct", ":".join([archive_id,  my_column.id, str(my_column.get_timestamp())])),
                    TraitPropertyMapping("alias", "col"),
                ])
            ]

        return ArchiveWithColumns

    def test_archive_with_unknown_columns(self, ArchiveWithColumns, test_data_dir):

        # Add a couple of mappings that reference missing columns:
        class ArchiveWithMissingColumns(ArchiveWithColumns):

            trait_mappings = ArchiveWithColumns.trait_mappings + [
                TraitMapping(TraitCollection, "missing", [
                    TraitPropertyMapping('missing', "random_column")
                ])
            ]

        ar = ArchiveWithColumns(basepath=test_data_dir)

        with pytest.raises(ValidationError):
            ar.validate(raise_exception=True)

    # def test_archive_instance_columns_not_class_columns(self, ArchiveWithColumns):
    #     ar = ArchiveWithColumns(basepath='/')
    #
    #     assert ar.columns[0] is not ArchiveWithColumns.column_definitions[0]

    # def test_associated_columns_have_correct_association(self, ArchiveWithColumns):
    #     basepath = '/'
    #
    #     ar = ArchiveWithColumns(basepath=basepath)
    #     assert ar.columns.red_image._archive_id == ar.archive_id
    #     assert ar.columns.red_image._archive is ar

    # def test_instanciating_archive_doesnt_affect_class_columns(self):
    #
    #     class ArchiveWithColumns(BasePathArchive):
    #
    #         class columns:
    #             red_image = FITSDataColumn("{object_id}/{object_id}_red_image.fits", 0,
    #                                        ndim=2)
    #
    #     class_column = ArchiveWithColumns.columns.red_image
    #     ar = ArchiveWithColumns(basepath='/')
    #     assert class_column is ArchiveWithColumns.columns.red_image
    #     assert class_column._archive_id is None
    #     assert class_column._archive is None

    def test_get_column_with_id(self, test_data_dir, ArchiveWithColumns):
        ar = ArchiveWithColumns(basepath=test_data_dir)  # type: fidia.archive.archive.Archive
        print(ar.archive_id)
        print(ar.columns.keys())

        column = ar.columns["testArchive:FixedValueColumn:data:1"]
        assert isinstance(column, FIDIAColumn)

        column = ar.columns["testArchive:FITSDataColumn:" +
                            "{object_id}/{object_id}_red_image.fits[0]:1"]
        assert isinstance(column, FIDIAColumn)


    def test_retrieve_trait_value(self, test_data_dir, ArchiveWithColumns):
        ar = ArchiveWithColumns(basepath=test_data_dir)  # type: fidia.archive.archive.Archive

        assert ar["Gal1"].trait_collection["trait"].direct == "data"

    def test_retrieve_trait_value_with_alias(self, test_data_dir, ArchiveWithColumns):
        """Fixed in ASVO-1000"""
        ar = ArchiveWithColumns(basepath=test_data_dir)  # type: fidia.archive.archive.Archive

        assert ar["Gal1"].trait_collection["trait"].alias == "data"

    def test_retrieve_data_from_path_column(self, test_data_dir, ArchiveWithColumns):
        ar = ArchiveWithColumns(basepath=test_data_dir)
        value = ar.columns["testArchive:FITSDataColumn:" +
                           "{object_id}/{object_id}_red_image.fits[0]:1"].get_value('Gal1')

        assert value.shape == (200, 200)


class TestExampleArchive:
    """Tests which are based on the Example Archive.

    These tests make much of the real, practical tests of the system, rather
    than being individual, 'unit' tests.

    """

    @pytest.fixture
    def example_archive(self, test_data_dir):
        return ExampleArchive(basepath=test_data_dir)

    @pytest.fixture
    def sample(self, example_archive):
        return fidia.Sample.new_from_archive(example_archive)

    def test_example_archive_contents(self, example_archive, test_data_dir):

        ea_contents = set(example_archive.contents)

        with open(os.path.join(test_data_dir, "object_list.txt")) as f:
            available_contents = set([t.strip() for t in f.readlines()])

        assert ea_contents == available_contents

        assert "Gal1" in ea_contents

    def test_red_image_data(self, example_archive):
        img = example_archive.columns["ExampleArchive:FITSDataColumn:{object_id}/{object_id}_red_image.fits[0]:1"].get_value('Gal1')
        assert img.shape == (200, 200)

    def test_red_image_exposed_data(self, example_archive):
        img = example_archive.columns["ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[EXPOSED]:1"].get_value('Gal1')
        assert img in (3500, 3600, 2400)

    def test_example_archive_columns_available(self, example_archive):
        example_archive.columns

    def test_example_archive_image_trait(self, sample):

        print("dir of AstroObject:")
        print(dir(sample['Gal1']))

        print(sample['Gal1'].image)

        image = sample['Gal1'].image['red']

        print(image.exposed)
        assert isinstance(image.exposed, (int, float))

        print(image.data)
        assert isinstance(image.data, np.ndarray)
        assert image.data.ndim == 2

    def test_ordering_of_trait_property_mappings_preserved(self):

        from fidia.traits import TraitPropertyMapping, DMU, TraitMapping, SubTraitMapping, ImageWCS

        tpm_list = [TraitPropertyMapping('crpix1',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CRVAL1]:1'),
                    TraitPropertyMapping('crpix2',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CRVAL2]:1'),
                    TraitPropertyMapping('crval1',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CRPIX1]:1'),
                    TraitPropertyMapping('crval2',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CRPIX2]:1'),
                    TraitPropertyMapping('cdelt1',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CDELT1]:1'),
                    TraitPropertyMapping('cdelt2',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CDELT2]:1'),
                    TraitPropertyMapping('ctype1',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CTYPE1]:1'),
                    TraitPropertyMapping('ctype2',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CTYPE2]:1')]

        class ArchiveWithOrder(fidia.ArchiveDefinition):

            # For general testing, this should be set to True (commented out)
            # For testing of the system without database persistence, it should be False.
            # is_persisted = False


            archive_id = "testArchiveWithOrder"

            contents = ["Gal1"]

            archive_type = fidia.Archive

            trait_mappings = [
                TraitMapping(DMU, "trait", tpm_list) #[
                    # SubTraitMapping('wcs', ImageWCS, tpm_list)
                # ])
            ]

        ar = ArchiveWithOrder()

        assert isinstance(ar, fidia.Archive)

        print(list(ar.trait_mappings.keys()))

        tm = ar.trait_mappings[ArchiveWithOrder.trait_mappings[0].mapping_key]
        # tm = list(ar.trait_mappings.values())[0]
        assert isinstance(tm, TraitMapping)
        keys = list(tm.trait_property_mappings.keys())

        keys_original_order = list(map(lambda x: x.name, tpm_list))

        print("Expected Order: %s" % keys_original_order)
        print("Actual Order: %s" % keys)

        assert keys_original_order == keys

    def test_ordering_of_trait_property_mappings_preserved_in_subtraits(self):
        from fidia.traits import TraitPropertyMapping, DMU, TraitMapping, SubTraitMapping, ImageWCS, Image

        tpm_list = [TraitPropertyMapping('crpix1',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CRVAL1]:1'),
                    TraitPropertyMapping('crpix2',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CRVAL2]:1'),
                    TraitPropertyMapping('crval1',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CRPIX1]:1'),
                    TraitPropertyMapping('crval2',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CRPIX2]:1'),
                    TraitPropertyMapping('cdelt1',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CDELT1]:1'),
                    TraitPropertyMapping('cdelt2',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CDELT2]:1'),
                    TraitPropertyMapping('ctype1',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CTYPE1]:1'),
                    TraitPropertyMapping('ctype2',
                                         'ExampleArchive:FITSHeaderColumn:{object_id}/{object_id}_red_image.fits[0].header[CTYPE2]:1')]

        tpm_image_list = [
            TraitPropertyMapping('data', "mydatacolumn"),
            SubTraitMapping('wcs', ImageWCS, tpm_list)
        ]

        class ArchiveWithOrder(fidia.ArchiveDefinition):
            # For general testing, this should be set to True (commented out)
            # For testing of the system without database persistence, it should be False.
            # is_persisted = False


            archive_id = "testArchiveWithOrder2"

            contents = ["Gal1"]

            archive_type = fidia.Archive

            trait_mappings = [
                TraitMapping(Image, "image", tpm_image_list)
            ]

        ar = ArchiveWithOrder()

        assert isinstance(ar, fidia.Archive)

        print(list(ar.trait_mappings.keys()))

        tm = ar.trait_mappings[ArchiveWithOrder.trait_mappings[0].mapping_key]
        # tm = list(ar.trait_mappings.values())[0]
        assert isinstance(tm, TraitMapping)
        stm = tm.sub_trait_mappings['wcs']
        assert isinstance(stm, SubTraitMapping)
        keys = list(stm.trait_property_mappings.keys())

        keys_original_order = list(map(lambda x: x.name, tpm_list))

        print("Expected Order: %s" % keys_original_order)
        print("Actual Order: %s" % keys)

        assert keys_original_order == keys

    def test_ordering_of_named_sub_traits_preserved_in_trait_collections(self):
        from fidia.traits import TraitPropertyMapping, DMU, TraitMapping, Table, ImageWCS, Image

        tm_list = [
            TraitMapping(Table, "a1", []),
            TraitMapping(Table, "a2", []),
            TraitMapping(Table, "a3", []),
            TraitMapping(Table, "a4", []),
            TraitMapping(Table, "a5", []),
            TraitMapping(Table, "a6", [])
        ]

        class ArchiveWithOrder(fidia.ArchiveDefinition):
            # For general testing, this should be set to True (commented out)
            # For testing of the system without database persistence, it should be False.
            # is_persisted = False


            archive_id = "testArchiveWithOrder3"

            contents = ["Gal1"]

            archive_type = fidia.Archive

            trait_mappings = [
                TraitMapping(DMU, "dmu", tm_list)
            ]

        ar = ArchiveWithOrder()

        assert isinstance(ar, fidia.Archive)

        print(list(ar.trait_mappings.keys()))

        tm = ar.trait_mappings[ArchiveWithOrder.trait_mappings[0].mapping_key]
        assert isinstance(tm, TraitMapping)
        keys = [i[1] for i in tm.named_sub_mappings.keys()]

        keys_original_order = list(map(lambda x: str(x.trait_key), tm_list))

        print("Expected Order: %s" % keys_original_order)
        print("Actual Order: %s" % keys)

        assert keys_original_order == keys


class TestKnownArchives:
    """These tests check whether the archive persistance is working correctly.

    They should perhaps be stored in database_tools tests, but anyway...

    """

    def test_known_archives_exists(self):
        import fidia.archive.archive
        assert isinstance(fidia.known_archives, fidia.archive.archive.KnownArchives)

    def test_known_archives_get_by_id(self, test_data_dir):
        # Guarantee that ExampleArchive will appear it the persistence database:
        ExampleArchive(basepath=test_data_dir)
        ar = fidia.known_archives.by_id["ExampleArchive"]

        print(ar)
        # assert False

    def test_known_archives_get_all(self, test_data_dir):
        # Guarantee that ExampleArchive will appear it the persistence database:
        ExampleArchive(basepath=test_data_dir)


        import fidia.archive.archive
        all_archives = fidia.known_archives.all
        assert isinstance(all_archives, list)
        if len(all_archives) > 0:
            for ar in all_archives:
                assert isinstance(ar, fidia.Archive)
        print(all_archives)
        print([ar.archive_id for ar in all_archives])


        # assert False

class TestArchive:
    pass
    # @pytest.fixture
    # def example_spectral_map(self):
    #
    #     return ExampleSpectralMap
    #
    # @pytest.fixture
    # def example_spectral_map_with_extra(self):
    #
    #     return ExampleSpectralMapExtra

    # @pytest.fixture
    # def example_spectral_map_with_extra_inherit(self, example_spectral_map):
    #     """Define a trait with an extra property."""
    #     class ExampleSpectralMap2(example_spectral_map):
    #         @trait_property('float')
    #         def extra_value(self):
    #             return np.random.random()
    #     return ExampleSpectralMap2



    # @pytest.fixture
    # def example_archive(self):
    #     return ExampleArchive()

    # @pytest.fixture
    # def simple_archive(self, example_spectral_map, example_spectral_map_with_extra):
    #
    #     class ExampleArchive(Archive):
    #
    #         def __init__(self):
    #             self._contents = ['Gal1', 'Gal2']
    #
    #             # Local cache for traits
    #             self._trait_cache = dict()
    #
    #             super().__init__()
    #
    #         @property
    #         def contents(self):
    #             return self._contents
    #
    #         @property
    #         def name(self):
    #             return 'ExampleArchive'
    #
    #         def define_available_traits(self):
    #             self.available_traits.register(example_spectral_map)
    #             self.available_traits.register(example_spectral_map_with_extra)
    #             return self.available_traits
    #
    #     return ExampleArchive

    # Basic Archive Functionality tests

    # def test_can_create_simple_archive(self, simple_archive):
    #     simple_archive()

    # def test_retrieve_correct_trait(self, simple_archive, example_spectral_map, example_spectral_map_with_extra):
    #     # ar = simple_archive()
    #     # assert ar.available_traits.retrieve_with_key(TraitKey('spectral_map')) is example_spectral_map
    #     # assert ar.available_traits.retrieve_with_key(TraitKey('spectral_map', branch='other')) is example_spectral_map
    #     # assert ar.available_traits.retrieve_with_key(TraitKey('spectral_map', branch='extra')) is example_spectral_map_with_extra
    #     pass

    # def test_trait_has_data(self, simple_archive):
    #     # sample = simple_archive().get_full_sample()
    #     # trait = sample['Gal1']['spectral_map']
    #     # trait.value()
    #     # assert isinstance(trait.value(), np.ndarray)
    #     pass

    # def test_trait_inherited_has_parent_data(self, simple_archive):
    #     # sample = simple_archive().get_full_sample()
    #     # trait = sample['Gal1'][TraitKey(trait_type='spectral_map', branch='extra')]
    #     # trait.value()
    #     # assert isinstance(trait.value(), np.ndarray)
    #     pass

    # def test_trait_has_correct_schema(self, simple_archive):
    #     # ar = simple_archive()
    #     # trait = ar.available_traits.retrieve_with_key(TraitKey('spectral_map', branch='other'))
    #     # schema = trait.schema()
    #     # assert schema == {'value': 'float.array.3', 'variance': 'float.array.3'}
    #     pass

    # def test_trait_extra_has_correct_schema(self, simple_archive):
    #     ar = simple_archive()
    #     trait = ar.available_traits.retrieve_with_key(TraitKey('spectral_map', branch='extra'))
    #     schema = trait.schema()
    #     print(trait.schema())
    #     assert schema == {'value': 'float.array.3', 'variance': 'float.array.3', 'extra_value': 'float'}

    # def test_trait_inherited_has_correct_schema(self, simple_archive):
    #     ar = simple_archive()
    #     trait = ar.available_traits.retrieve_with_key(TraitKey('spectral_map', branch='extra'))
    #     schema = trait.schema()
    #     assert schema == {'value': 'float.array.3', 'variance': 'float.array.3', 'extra_value': 'float'}
    #
    # def test_archive_has_correct_schema(self, simple_archive):
    #     ar = simple_archive()
    #     schema_by_trait_type = ar.schema(by_trait_name=False)
    #     assert schema_by_trait_type == {'spectral_map': {None: {
    #         'value': 'float.array.3', 'variance': 'float.array.3', 'extra_value': 'float'}}}
    #
    #     schema_by_trait_name = ar.schema(by_trait_name=True)
    #     assert schema_by_trait_name == {'spectral_map': {
    #         'value': 'float.array.3', 'variance': 'float.array.3', 'extra_value': 'float'}}
    #
    # def test_all_object_traits_in_schema(self, simple_archive):
    #     ar = simple_archive()
    #     schema_by_trait_type = ar.schema(by_trait_name=False)
    #     schema_by_trait_name = ar.schema(by_trait_name=True)
    #     sample = ar.get_full_sample()
    #     for astro_object in sample:
    #         trait_key_list = sample[astro_object].keys()
    #         for tk in trait_key_list:
    #             assert tk.trait_name in schema_by_trait_name
    #             assert tk.trait_type in schema_by_trait_type

    # Other tests.

    # def test_create_inmemory_archive(self):
    #     m = MemoryArchive()
    #     assert isinstance(m, BaseArchive)
    #
    # # Trait related tests:
    #
    # def test_trait_documentation(self, simple_archive):
    #     sample = simple_archive().get_full_sample()
    #     trait = sample['Gal1']['spectral_map:other']
    #
    #     assert trait.value.doc == "TheSpectralMapDocumentation"
    #
    # def test_trait_property_list(self, simple_archive):
    #     sample = simple_archive().get_full_sample()
    #     trait = sample['Gal1']['spectral_map:other']
    #     for trait_property, expected in zip(trait._trait_properties(), ('value', 'variance')):
    #         assert trait_property.name == expected
    #
    # # Feature data functionality
    #
    # def test_archive_has_feature_data(self, example_archive):
    #     # type: (ExampleArchive) -> None
    #     assert example_archive.feature_catalog_data is not None
    #
    #     for elem in example_archive.feature_catalog_data:
    #         assert isinstance(elem, TraitPath)
    #
    #
    # #
    # # Schema related Tests
    # #
    #
    # def test_get_type_for_trait_path(self, example_archive):
    #     assert isinstance(example_archive, Archive)
    #     assert issubclass(example_archive.type_for_trait_path(('simple_heir_trait',)), Trait)
    #     assert issubclass(example_archive.type_for_trait_path(('simple_heir_trait', 'value')), TraitProperty)
    #     assert issubclass(example_archive.type_for_trait_path(('simple_heir_trait', 'sub_trait')), Trait)
    #     assert issubclass(example_archive.type_for_trait_path(('simple_heir_trait', 'sub_trait', 'extra')), TraitProperty)
    #
    # def test_schema_for_traits_with_qualifiers_differs(self, example_archive):
    #     schema = example_archive.schema(by_trait_name=False)
    #
    #     assert 'extra_property_blue' in schema['image']['blue']
    #     assert 'extra_property_blue' not in schema['image']['red']
    #     assert 'extra_property_red' in schema['image']['red']
    #     assert 'extra_property_red' not in schema['image']['blue']
    #
    # def test_schema_for_subtraits_with_qualifiers_differs(self, example_archive):
    #     schema = example_archive.schema(by_trait_name=False)
    #
    #     sub_schema = schema['image']['blue']
    #     assert 'extra_property_blue' in sub_schema['image']['blue']
    #     assert 'extra_property_blue' not in sub_schema['image']['red']
    #     assert 'extra_property_red' in sub_schema['image']['red']
    #     assert 'extra_property_red' not in sub_schema['image']['blue']
