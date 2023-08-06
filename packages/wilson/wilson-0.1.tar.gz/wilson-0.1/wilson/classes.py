import wilson
from wilson.run.smeft import SMEFT
from wilson.run.wet import WETrunner
import numpy as np
from math import log, e
import wcxf


class Wilson(object):
    """Wilson."""
    def __init__(self, wcdict, scale, eft, basis):
        self.wc = wcxf.WC(eft=eft, basis=basis, scale=scale,
                          values=wcxf.WC.dict2values(wcdict))
        self.wc.validate()
        self._cache = {}

    @classmethod
    def from_wc(cls, wc):
        return cls(wcdict=wc.dict, scale=wc.scale, eft=wc.eft, basis=wc.basis)

    @classmethod
    def load_wc(cls, stream):
        wc = wcxf.WC.load(stream)
        return cls.from_wc(wc)

    def _repr_html_(self):
        r_wcxf = self.wc._repr_html_()
        r_wcxf = '\n'.join(r_wcxf.splitlines()[2:])  # remove WCxf heading
        html = "<h3>Wilson coefficients</h3>\n\n"
        html += r_wcxf
        return html

    def match_run(self, eft, basis, scale, sectors='all'):
        """Run the Wilson coefficients to a different scale
        (and possibly different EFT)
        and return them as `wcxf.WC` instance."""
        cached = self._get_from_cache(sector=sectors, scale=scale, eft=eft, basis=basis)
        if cached is not None:
            return cached
        scale_ew = 91.1876
        mb = 4.2
        mc = 1.3
        if self.wc.basis == basis and self.wc.eft == eft and scale == self.wc.scale:
            return self.wc  # nothing to do
        if self.wc.eft == 'SMEFT':
            if eft == 'SMEFT':
                smeft = SMEFT(self.wc)
                # if input and output EFT ist SMEFT, just run.
                wc_out = smeft.run(scale)
                self._set_cache('all', scale, 'SMEFT', wc_out.basis, wc_out)
                return wc_out
            else:
                # if SMEFT -> WET-x: match to WET at the EW scale
                wc_ew = self._get_from_cache(sector='all', scale=scale_ew, eft='WET', basis='JMS')
                if wc_ew is None:
                    smeft = SMEFT(self.wc)
                    wc_ew = smeft.run(scale_ew).match('WET', 'JMS')
                self._set_cache('all', scale_ew, wc_ew.eft, wc_ew.basis, wc_ew)
                wet = WETrunner(wc_ew)
        elif self.wc.eft in ['WET', 'WET-4', 'WET-3']:
            wet = WETrunner(self.wc.translate('JMS'))
        else:
            raise ValueError("Input EFT {} unknown or not supported".format(self.wc.eft))
        if eft == wet.eft:  # just run
            wc_out = wet.run(scale, sectors=sectors).translate(basis)
            self._set_cache(sectors, scale, eft, basis, wc_out)
            return wc_out
        elif eft == 'WET-4' and wet.eft == 'WET':  # match at mb
            wc_mb = wet.run(mb, sectors=sectors).match('WET-4', 'JMS')
            wet4 = WETrunner(wc_mb)
            wc_out = wet4.run(scale, sectors=sectors).translate(basis)
            self._set_cache(sectors, scale, 'WET-4', basis, wc_out)
            return wc_out
        elif eft == 'WET-3' and wet.eft == 'WET-4':  # match at mc
            wc_mc = wet.run(mc, sectors=sectors).match('WET-3', 'JMS')
            wet3 = WETrunner(wc_mc)
            wc_out = wet3.run(scale, sectors=sectors).translate(basis)
            return wc_out
            self._set_cache(sectors, scale, 'WET-3', basis, wc_out)
        elif eft == 'WET-3' and wet.eft == 'WET':  # match at mb and mc
            wc_mb = wet.run(mb, sectors=sectors).match('WET-4', 'JMS')
            wet4 = WETrunner(wc_mb)
            wc_mc = wet4.run(mc, sectors=sectors).match('WET-3', 'JMS')
            wet3 = WETrunner(wc_mc)
            wc_out = wet3.run(scale, sectors=sectors).translate(basis)
            self._set_cache(sectors, scale, 'WET-3', basis, wc_out)
            return wc_out
        else:
            raise ValueError("Running from {} to {} not implemented".format(wet.eft, eft))

    def get_smpar(self, scale_sm=91.1876):
        if self.wc.eft != 'SMEFT':
            raise ValueError("get_smpar only works if the initial EFT is SMEFT.")
        smeft = SMEFT(self.wc)
        C_out = smeft._rgevolve(scale_sm)
        return wilson.run.smeft.smpar.smpar(C_out)

    def _get_from_cache(self, sector, scale, eft, basis):
        """Try to load a set of Wilson coefficients from the cache, else return
        None."""
        try:
            return self._cache[eft][scale][basis][sector]
        except KeyError:
            return None

    def _set_cache(self, sector, scale, eft, basis, wc_out):
        if eft not in self._cache:
            self._cache[eft] = {scale: {basis: {sector: wc_out}}}
        elif scale not in self._cache[eft]:
            self._cache[eft][scale] = {basis: {sector: wc_out}}
        elif basis not in self._cache[eft][scale]:
            self._cache[eft][scale][basis] = {sector: wc_out}
        else:
            self._cache[eft][scale][basis][sector] = wc_out


class RGsolution(object):
    """Class representing a continuous (interpolated) solution to the
    SMEFT RGEs to be used for plotting."""

    def __init__(self, fun, scale_min, scale_max):
        """Initialize.

        Parameters:
        - fun: function of the scale that is expected to return a
        dictionary with the RGE solution and to accept vectorized input.
        - scale_min, scale_max: lower and upper boundaries of the scale
        """
        self.fun = fun
        self.scale_min = scale_min
        self.scale_max = scale_max

    def plotdata(self, key, part='re', scale='log', steps=50):
        """Return a tuple of arrays x, y that can be fed to plt.plot,
        where x is the scale in GeV and y is the parameter of interest.

        Parameters:
        - key: dicionary key of the parameter to be plotted (e.g. a WCxf
          coefficient name or a SM parameter like 'g')
        - part: plot the real part 're' (default) or the imaginary part 'im'
        - scale: 'log'; make the x steps logarithmically distributed; for
          'linear', linearly distributed
        - steps: steps in x to take (default: 50)
        """
        if scale == 'log':
            x = np.logspace(log(self.scale_min),
                            log(self.scale_max),
                            steps,
                            base=e)
        elif scale == 'linear':
            x = np.linspace(self.scale_min,
                            self.scale_max,
                            steps)
        y = self.fun(x)
        y = np.array([d[key] for d in y])
        if part == 're':
            return x, y.real
        elif part == 'im':
            return x, y.imag

    def plot(self, key, part='re', scale='log', steps=50, legend=True, plotargs={}):
        """Plot the RG evolution of parameter `key`.

        Parameters:
        - part, scale, steps: see `plotdata`
        - legend: boolean, show the legend (default: True)
        - plotargs: dictionary of arguments to be passed to plt.plot
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError("Please install matplotlib if you want to use the plot method")
        pdat = self.plotdata(key, part=part, scale=scale, steps=steps)
        plt.plot(*pdat, label=key, **plotargs)
        if scale == 'log':
            plt.xscale('log')
        if legend:
            plt.legend()
