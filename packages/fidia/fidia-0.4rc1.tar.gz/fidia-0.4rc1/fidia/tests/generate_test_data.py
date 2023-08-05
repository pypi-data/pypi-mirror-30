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

import random
import os

import numpy as np

from astropy.io import fits
from astropy.wcs import WCS
from astropy import table

class TestData:

    def __init__(self, size, skip=list()):
        self.object_ids = ["Gal{}".format(i+1) for i in range(size) if i+1 not in skip]
        self.size = len(self.object_ids)

    def data(self):
        # An empty iterator (from http://stackoverflow.com/a/26271684/1970057)
        return iter(())

    def metadata(self, object_id):
        # An empty iterator
        return iter(())


class CatalogTable(TestData):

    # def __init__(self, size):
    #     super(CatalogTable, self).__init__(size)

    def columns(self):
        return iter(())

    def table(self):
        # type: () -> table.Table
        return table.Table(self.column_data())


def checkdir(output_directory, filename):
    path = os.path.join(output_directory, filename)
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

def write_to_single_extension_fits(test_data, output_directory, filename_pattern):
    # type: (TestData, str, str) -> None
    for objid, datum in zip(test_data.object_ids, test_data.data()):
        pdu = fits.PrimaryHDU(datum.T)

        meta = test_data.metadata(objid)
        for key in meta:
            pdu.header[key] = meta[key]
        if hasattr(test_data, 'wcs'):
            w = test_data.wcs(objid)  # type: WCS
            pdu.header.extend(w.to_header())
        filename = filename_pattern.format(object_id=objid)
        checkdir(output_directory, filename)
        pdu.writeto(os.path.join(output_directory, filename))

def write_to_binary_fits_table(test_data, output_directory, filename_pattern):
    # type: (CatalogTable, str, str) -> None
    output_file = os.path.join(output_directory, filename_pattern)
    test_data.table().write(output_file, format="fits")

def write_to_csv_table(test_data, output_directory, filename_pattern):
    # type: (CatalogTable, str, str) -> None
    output_file = os.path.join(output_directory, filename_pattern)
    test_data.table().write(output_file, format="ascii.csv")


class SimpleImage(TestData):

    def data(self):
        for objid in self.object_ids:
            yield np.random.random((200, 200))

    def metadata(self, object_id):
        random.seed(hash(object_id))
        return {
            "TELESCOP": ("Anglo-Australian Telescope", "Telescope"),
            "OBJECT": (object_id, "Name of the galaxy"),
            "EXPOSED": (random.choice([3600, 2400, 3500]), "Exposure time")
        }

    def wcs(self, object_id):
        np.random.seed(hash(object_id) % 2**32 - 1)
        w = WCS(naxis=2)
        w.wcs.crpix = [10, 15]
        w.wcs.crval = np.random.uniform(-10, 10, 2)
        w.wcs.cdelt = [1/3600, 1/3600]
        w.wcs.ctype = ['RA---TAN', 'DEC--TAN']
        return w

class SpectralCube(TestData):

    def __init__(self, size, wave_start, wave_end, sampling, skip=list()):
        super(SpectralCube, self).__init__(size, skip=skip)

        self.wavescale = np.linspace(wave_start, wave_end, (wave_end - wave_start)//sampling)
        self.wave_sampling = sampling

    def data(self):
        for objid in self.object_ids:
            yield np.random.random((20, 30, len(self.wavescale)))

    def metadata(self, object_id):
        random.seed(hash(object_id))
        return {
            "TELESCOP": ("Anglo-Australian Telescope", "Telescope"),
            "OBJECT": (object_id, "Name of the galaxy"),
            "EXPOSED": (random.choice([3600, 2400, 3500]), "Exposure time")
        }

    def wcs(self, object_id):
        np.random.seed(hash(object_id) % 2**32 - 1)
        w = WCS(naxis=3)
        w.wcs.crpix = [10, 15, 1]
        w.wcs.crval = np.random.uniform(-10, 10, 3)
        w.wcs.crval[2] = self.wavescale[0]
        w.wcs.cdelt = [1/3600, 1/3600, self.wave_sampling]
        w.wcs.ctype = ['RA---TAN', 'DEC--TAN', 'WAVELEN']
        return w


class StellarMassesTable(CatalogTable):

    def column_data(self):
        cols = [
            table.Column(
                name="ID",
                data=self.object_ids),
            table.Column(
                name="StellarMass",
                data=np.random.normal(10, 0.5, self.size)),
            table.Column(
                name="StellarMassError",
                data=np.random.normal(0, 1, self.size)**2)
        ]
        return cols


class SFRsTable(CatalogTable):
    def column_data(self):
        cols = [
            table.Column(
                name="ID",
                data=self.object_ids),
            table.Column(
                name="SFR",
                data=np.random.lognormal(-0.6, 0.3, self.size)),
            table.Column(
                name="SFR_ERR",
                data=np.random.normal(0, 0.1, self.size)**2)
        ]
        return cols

class SinePngs(TestData):

    def data(self):

        import matplotlib
        matplotlib.use('AGG')
        from matplotlib import pyplot as plt
        from io import BytesIO

        for objid in self.object_ids:
            buffer = BytesIO()

            # From: https://matplotlib.org/devdocs/api/_as_gen/matplotlib.pyplot.savefig.html

            off = random.random()
            t = np.arange(0.0, 2.0, 0.01)
            s = 1 + np.sin(2 * np.pi * t + off)
            plt.plot(t, s)

            plt.xlabel('time (s)')
            plt.ylabel('voltage (mV)')
            plt.title('About as simple as it gets, folks')
            plt.grid(True)
            plt.savefig(buffer, format='png')

            bytes = buffer.getvalue()

            yield bytes

def write_binary_file(test_data, output_directory, filename_pattern):
    # type: (TestData, str, str) -> None
    for objid, datum in zip(test_data.object_ids, test_data.data()):

        filename = filename_pattern.format(object_id=objid)
        checkdir(output_directory, filename)

        with open(os.path.join(output_directory, filename), 'wb') as outfile:
            outfile.write(datum)



def generate_simple_dataset(output_directory, size, missing_data=True):

    if missing_data:
        # Delete some data to simulate missing or incomplete data for some objects, namely Gal3:
        skip = [3]
    else:
        skip = []

    # Create an image of each object at "Gal1/Gal1_red_image.fits"
    write_to_single_extension_fits(SimpleImage(size), output_directory, "{object_id}/{object_id}_red_image.fits")

    # Create a spectral cube
    write_to_single_extension_fits(SpectralCube(size, 3400, 3600, 1.34, skip=skip), output_directory, "{object_id}/{object_id}_spec_cube.fits")

    # Create some tables:
    write_to_binary_fits_table(StellarMassesTable(size), output_directory, "stellar_masses.fits")
    write_to_binary_fits_table(SFRsTable(size, skip=skip), output_directory, "sfr_table.fits")
    write_to_csv_table(SFRsTable(size, skip=skip), output_directory, "sfr_table.csv")

    # Create some png images:
    write_binary_file(SinePngs(size), output_directory, "{object_id}/{object_id}_spectra.png")

    # Write out a text file containing just the object ids:
    with open(os.path.join(output_directory, "object_list.txt"), "w") as f:
        for object_id in TestData(size).object_ids:
            f.write(object_id + "\n")

if __name__ == '__main__':
    import sys
    if type(sys.argv[1]) is str:
        generate_simple_dataset(sys.argv[1], 5)