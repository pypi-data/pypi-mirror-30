#!/usr/bin/env python
"""
Total Radiance = atmosphere rad. or boundary rad. + atm. scat. or boundary refl.

Lowtran outputs W cm^-2 ster^-1 micron^-1
we want photons cm^-2 s^-1 ster^-1 micron^-1
1 W cm^-2 = 10000 W m^-2

h = 6.62607004e-34 m^2 kg s^-1
I: irradiance
Np: numer of photons
Np = (Ilowtran*10000)*lambda_m/(h*c)
"""
from pathlib import Path
from matplotlib.pyplot import show
try:
    import seaborn as sns
    sns.set_context('talk',font_scale=1.5)
except ImportError:
    pass
#
import lowtran
from lowtran.plots import plotscatter


if __name__=='__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description='Lowtran 7 interface')
    p.add_argument('-z','--obsalt',help='altitude of observer [km]',type=float,default=0.)
    p.add_argument('-a','--zenang',help='Observer zenith angle [deg] ',nargs='+',type=float,default=[0.,60,80])
    p.add_argument('-w','--wavelen',help='wavelength range nm (start,stop)',type=float,nargs=2,default=(300,1000))
    p.add_argument('-o','--outfn',help='NetCDF4 file to write')
    p.add_argument('--model',help='0-6, see Card1 "model" reference. 5=subarctic winter',type=int,default=5)

    p=p.parse_args()

    c1={'model':p.model,
        'h1': p.obsalt, # of observer
        'angle': p.zenang, # of observer
        'wlnmlim': p.wavelen,
        }
# %%
    TR = lowtran.scatter(c1)
# %%
    if p.outfn:
        outfn = Path(p.outfn).expanduser()
        print('writing', outfn)
        TR.to_netcdf(outfn)
# %%
    plotscatter(TR, c1)

    show()
