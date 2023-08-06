#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import ee
from .. import satcol, scores, bap, season, masks, filters, functions
from geetools import tools
from .. import __version__

ee.Initialize()

class TestBAP(unittest.TestCase):

    def setUp(self):

        print('Testing Best Available Pixel Composite version {}'.format(__version__))
        # FILTERS
        self.filtro = filters.CloudsPercent()

        # MASKS
        self.nubes = masks.Clouds()

        # SEASON
        self.temporada = season.Season.Growing_South()

        # COLLECTIONS
        self.coleccion = satcol.ColGroup.Landsat()

        # SCORES
        self.psat = scores.Satellite()
        self.pop = scores.AtmosOpacity()
        self.pmascpor = scores.MaskPercent()
        self.pindice = scores.Index()
        self.pout = scores.Outliers(("ndvi",))
        self.pdoy = scores.Doy()

        # SITES
        self.sitio = ee.Geometry.Polygon(
        [[[-71.78, -42.79],
          [-71.78, -42.89],
          [-71.57, -42.89],
          [-71.57, -42.79]]])
        self.centroid = self.sitio.centroid()

    def test_bap2016_0(self):
        pmulti = scores.MultiYear(2016, self.temporada)
        objbap = bap.Bap(year=2016,
                         # colgroup=self.coleccion,
                         season=self.temporada,
                         scores=(self.pindice, self.pmascpor, self.psat,
                                 self.pout, self.pop, self.pdoy, pmulti),
                         masks=(self.nubes,),
                         filters=(self.filtro,),
                         )

        # objbap.debug = True
        sitio = self.sitio

        unpix = objbap.bestpixel(sitio, indices=("ndvi",))
        img = unpix.image
        col = unpix.col

        self.assertIsInstance(img, ee.Image)
        self.assertIsInstance(col, ee.ImageCollection)

        idict = img.getInfo()
        cdict = col.getInfo()
        self.assertIsInstance(idict, dict)
        self.assertIsInstance(cdict, dict)

        value = tools.get_value(img, self.centroid, 30, 'client')
        print(value)

        self.assertIsInstance(value, dict)

        visual = img.visualize(bands=['NIR','SWIR','RED'], min=0, max=0.5)
        url = visual.getThumbUrl({'region':tools.getRegion(img)})
        print('Result:', url)