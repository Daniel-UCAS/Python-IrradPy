### 50-Badescu 2008

###References:
# Badescu, V. (2008). Use of sunshine number for solar irradiance time series generation. In Modeling Solar Radiation at the Earth’s Surface (pp. 327-355). Springer, Berlin, Heidelberg.
# Badescu, V., Gueymard, C. A., Cheval, S., Oprea, C., Baciu, M., Dumitrescu, A., ... & Rada, C. (2013). Accuracy analysis for fifty-four clear-sky solar radiation models using routine hourly global irradiance measurements in Romania. Renewable Energy, 55, 85-103.

###Inputs:
#  Esc=1366.1   [Wm-2]      (Solar constant)
#  sza          [radians]   (zenith_angle)
#  press        [mb]        (local barometric)
#  wv           [atm.cm]    (total columnar amount of water vapour)
#  ozone        [atm.cm]    (total columnar amount of ozone)

###Outputs:
#  Ebn  [Wm-2]     (Direct normal irradiance)
#  Edh  [Wm-2]     (Diffuse horizontal irradiance)
#  Egh  [Wm-2]     (Global horizontal irradiance)

###Notes:
#  Dayth is the day number ranging from 1 to 365.

###Codes:
import numpy as np
from numpy import sin, cos, log, log10, power, pi
from .solarGeometry import time2dayth, time2yearth

class ClearSkyBadescu:
    def __init__(self, time, press):
        self.dayth = time2dayth(time)
        self.yearth = time2yearth(time)
        self.press = press

    def Badescu(self, sza, wv, ozone):
        # Extraterrestrial irradiance
        Esc = 1366.1
        totaldayofyear = 366 - np.ceil(self.yearth / 4 - np.trunc(self.yearth / 4))
        B = (self.dayth - 1) * 2 * np.pi / totaldayofyear
        Eext = Esc * (1.00011 + 0.034221 * np.cos(B) + 0.00128 * np.sin(B) + 0.000719 * np.cos(2 * B) + 0.000077 * np.sin(2 * B))

        # Air mass corrected for elevation
        am = 1 / (cos(sza) + 0.15 * power((pi / 2 - sza) / pi * 180 + 3.885, -1.253))
        ama = am * self.press / 1013.25

        # the transimissivity of the atmosphere due to Rayleigh scattering by molecules
        Tr = 0.9768 - 0.0874 * ama + 0.010607552 * power(ama, 2) - 8.46205e-4 * power(ama, 3) + 3.57246e-5 * power(ama, 4) - 6.0176e-7 * power(ama, 5)

        # the transmissivity of the ozone layer  (Badescu 2013)
        XO = ama * (ozone * 10)  # our ozone unit here is atm.cm

        AO = ((0.1082 * XO) / (power(1 + 13.86 * XO, 0.805))) + ((0.00658 * XO) / (1 + power(10.36 * XO, 3))) + (
                    0.002118 * XO / (1 + 0.0042 * XO + 3.23e-6 * XO * XO))
        TO = 1 - AO

        # the transmissivity of aerosols depends on the air mass
        Ta = power(0.84, ama)

        # the absorptivity by water vapour (Badescu 2013)
        XW = ama * wv * 10  ##our wv unit here is atm.cm


        AW = 0.29 * XW / ((power(1 + 14.15 * XW, 0.635)) + 0.5925 * XW)

        # direct normal radiation
        M = Tr * TO - AW
        M[M < 0] = 0
        EbnBadescu = Eext * M * Ta
        # diffuse horizontal radiation
        EdhBadescu = Eext * cos(sza) * (0.5 * TO * (1 - Tr) + 0.75 * (0.93 - 0.21 * log(ama)) * (TO * Tr - AW) * (1 - Ta))
        # global radiation
        EghBadescu = EbnBadescu * cos(sza) + EdhBadescu

        # Quality control
        lower = 0
        EbnBadescu[EbnBadescu < lower] = 0
        EdhBadescu[EdhBadescu < lower] = 0
        EghBadescu[EghBadescu < lower] = 0
        return [EbnBadescu, EdhBadescu, EghBadescu]
