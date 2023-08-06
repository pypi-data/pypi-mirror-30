# coding=utf-8

''' Functions for calculation indices '''

import ee

import ee.data
if not ee.data._initialized: ee.Initialize()

NDVI_EXP = "(NIR-RED)/(NIR+RED)"
EVI_EXP = "G*((NIR-RED)/(NIR+(C1*RED)-(C2*BLUE)+L))"
NBR_EXP = "(NIR-SWIR)/(NIR+SWIR)"

true = ee.Number(1)
false = ee.Number(0)

FORMULAS = {
    'NDVI': '(NIR-RED)/(NIR+RED)',
    'EVI': 'G*((NIR-RED)/(NIR+(C1*RED)-(C2*BLUE)+L))',
    'NBR': '(NIR-SWIR)/(NIR+SWIR)'
}

AVAILABLE = FORMULAS.keys()

def compute(index, band_params, extra_params=None, addBand=True):
    if index not in AVAILABLE:
        raise ValueError('Index not available')

    addBandEE = true if addBand else false
    band_paramsEE = ee.Dictionary(band_params)
    extra_paramsEE = ee.Dictionary(extra_params) if extra_params else ee.Dictionary({})

    def calc(img):
        def map_params(key, val):
            return img.select([val])
        band_paramsEE_mapped = band_paramsEE.map(map_params)
        paramsEE_mapped = band_paramsEE_mapped.combine(extra_paramsEE)
        nd = img.expression(FORMULAS[index], paramsEE_mapped).select([0], [index])
        result = ee.Algorithms.If(addBandEE, img.addBands(nd), nd)
        return ee.Image(result)

    return calc

def ndvi(nir, red, addBand=True):
    """ Calculates NDVI index

    :USE:

    .. code:: python

        # use in a collection
        col = ee.ImageCollection(ID)
        ndvi = col.map(indices.ndvi("B4", "B3"))

        # use in a single image
        img = ee.Image(ID)
        ndvi = Indices.ndvi("NIR", "RED")(img)

    :param nir: name of the Near Infrared () band
    :type nir: str
    :param red: name of the red () band
    :type red: str
    :param addBand: if True adds the index band to the others, otherwise
        returns just the index band
    :type addBand: bool
    :return: The function to apply a map() over a collection
    :rtype: function
    """
    return compute('NDVI', {'NIR':nir, 'RED':red}, addBand=addBand)


def evi(nir, red, blue, G=2.5, C1=6, C2=7.5, L=1, addBand=True):
    """ Calculates EVI index

    :param nir: name of the Near Infrared () band
    :type nir: str
    :param red: name of the red () band
    :type red: str
    :param blue: name of the blue () band
    :type blue: str
    :param G: G coefficient for the EVI index
    :type G: float
    :param C1: C1 coefficient for the EVI index
    :type C1: float
    :param C2: C2 coefficient for the EVI index
    :type C2: float
    :param L: L coefficient for the EVI index
    :type L: float
    :param addBand: if True adds the index band to the others, otherwise
        returns just the index band
    :return: The function to apply a map() over a collection
    :rtype: function
    """
    G = float(G)
    C1 = float(C1)
    C2 = float(C2)
    L = float(L)

    return compute('EVI', {'NIR':nir, 'RED':red, 'BLUE':blue},
                          {'G':G, 'C1':C1, 'C2':C2, 'L':L}, addBand=addBand)

def nbr(nir, swir, addBand=True):
    """ Calculates NBR index

    :USE:

    .. code:: python

        # use in a collection
        col = ee.ImageCollection(ID)
        ndvi = col.map(indices.ndvi("B4", "B3"))

        # use in a single image
        img = ee.Image(ID)
        ndvi = Indices.ndvi("NIR", "RED")(img)

    :param nir: name of the Near Infrared () band
    :type nir: str
    :param red: name of the red () band
    :type red: str
    :param addBand: if True adds the index band to the others, otherwise
        returns just the index band
    :type addBand: bool
    :return: The function to apply a map() over a collection
    :rtype: function
    """
    return compute('NBR', {'NIR':nir, 'SWIR':swir}, addBand=addBand)


REL = {"NDVI": ndvi,
       "EVI": evi,
       "NBR": nbr
       }