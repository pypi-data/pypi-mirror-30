#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2018 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c20671.ad.smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
"""


from pyspectral.near_infrared_reflectance import Calculator
from pyspectral.radiance_tb_conversion import RadTbConverter
from pyspectral.blackbody import blackbody_rad2temp
import numpy as np

sunz = np.array([68.98597217,  68.9865146,  68.98705756,  68.98760105, 68.98814508])
tb37 = np.array([298.07385254, 297.15478516, 294.43276978, 281.67633057, 273.7923584])
tb11 = np.array([271.38806152, 271.38806152, 271.33453369, 271.98553467, 271.93609619])

viirs = RadTbConverter('Suomi-NPP', 'viirs', 'M12')
refl_m12 = Calculator('Suomi-NPP', 'viirs', 'M12')

m12r = refl_m12.reflectance_from_tbs(sunz, tb37, tb11)
print m12r
rad = (1 - m12r) * viirs.tb2radiance(tb11)['radiance']
print rad
tb = blackbody_rad2temp(viirs.rsr['M12']['det-1']['central_wavelength'] * 1e-6, rad)
print tb
tb = viirs.radiance2tb(rad)
print tb
print refl_m12.emissive_part_3x()
