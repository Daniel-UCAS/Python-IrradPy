### 10-HLJ 1976

###References:
# Hottel, H. C. (1976). A simple model for estimating the transmittance of direct solar radiation through clear atmospheres. Solar energy, 18(2), 129-134.
# Gueymard, C. A. (2012). Clear-sky irradiance predictions for solar resource mapping and large-scale applications: Improved validation methodology and detailed performance analysis of 18 broadband radiative models. Solar Energy, 86(8), 2145-2169.

###Inputs:
#  Esc=1353   [Wm-2]      (Solar constant)
#  sza        [radians]   (zenith_angle)
#  altitude   [m]         (location's altitude)

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from .solarGeometry import time2dayth, time2yearth

class ClearSkyHLJ:
    def __init__(self, time, elev):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.elev = elev

    def HLJ(self, sza):
        # Extraterrestrial irradiance
        Esc = 1353
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Solar transmittance a0+a1*exp(-a2/cos(sza))
        a0 = 0.4237 - 0.00821 * np.power((6 - self.elev / 1000), 2)
        a1 = 0.5055 + 0.00595 * np.power((6.5 - self.elev / 1000), 2)
        if self.elev / 1000 <= 2.5:
            a2=0.2711+0.01858 * np.power((2.5- self.elev/ 1000), 2)
        else:
            a2=-0.02173+3.3693e-4 * self.elev  # Gueymard2012-section4.2-equation5

        # Direct beam irradiance
        Ebnhlj = Eext * (a0 + a1 * np.exp(-a2 / np.cos(sza)))

        # Diffuse horizontal irradiance
        Edhhlj = (0.2710 * Eext - 0.2939 * Ebnhlj) * np.cos(sza)

        # Global horizontal irradiance
        Eghhlj = Ebnhlj * np.cos(sza) + Edhhlj

        # Quality control
        lower = 0
        Ebnhlj[Ebnhlj < lower] = 0
        Edhhlj[Edhhlj < lower] = 0
        Eghhlj[Eghhlj < lower] = 0
        return [Ebnhlj, Edhhlj, Eghhlj]

