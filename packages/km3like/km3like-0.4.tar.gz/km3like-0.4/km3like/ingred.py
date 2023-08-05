#!/usr/bin/env python
# coding=utf-8
# pylint: disable=C0103,R0903
# vim:set ts=4 sts=4 sw=4 et:

from __future__ import division, absolute_import, print_function

from six import string_types
import logging
import re

import h5py
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib.pyplot as plt

from astropy.convolution import CustomKernel, convolve
from sklearn.neighbors import KernelDensity

from km3astro.random import random_azimuth, random_date
from km3astro.coord import local_event, sun_local
from km3astro.sources import GALACTIC_CENTER

from km3like.data import gc_morph
from km3pipe.math import mad


def sigma_lognorm(v):
    loc, scale, sigma = stats.lognorm.fit(v)
    return sigma


def get_lognorm(sigma):
    return stats.lognorm(s=sigma)


def sigma_norm(v):
    loc, scale = stats.norm.fit(v)
    return scale


def sigma_halfnorm(v):
    loc, scale = stats.halfnorm.fit(v)
    return scale


def width_halfcauchy(v):
    loc, scale = stats.halfcauchy.fit(v)
    return scale


def width_cauchy(v):
    loc, scale = stats.cauchy.fit(v)
    return scale


def mean_abs_err(v):
    return np.mean(np.abs(v))


def mean_squared_err(v):
    return np.mean(np.square(v))


class NotFittedError(ValueError, AttributeError):
    """Exception class to raise if estimator is used before fitting.
    """


class BinnedResolution(object):
    """Fit an resolutioni (e.g. angular), binned in ene, cosz.

    Resolutions are approximated as contant in each (ene ,cosz) bin.

    Methods
    -------
    fit(residual, energy, coszen)
        Measure residuals in each (ene, cosz) bin.
    estimate(ene, cosz)
        Estimate the errors of individual events, depending
        on the (ene, cosz) bin they fall into. Needs to be fitted first.
    plot()
        Show a 2D heatmap of the resolution. Needs to be fitted first.
    save(filename)
        Dump the fitted resolution map to a hdf5 file.
    load(filename)
        Load a fitted resolution from a hdf5 file.

    Example
    -------
    >>> r = BinnedResolution(ebins, cosz_bins, metric='median')
    >>> r.fit(residuals, reco_energy, reco_coszen)
    >>> r.plot()
    >>> r.estimate(some_ene, some_cosz)
    >>> r.save('test.h5', mode='w')
    >>> rr = BinnedResolution.load('test.h5')
    >>> rr.estimate(some_ene, some_cosz)
    >>> rr.plot()
    """
    metrics_avail = {
        'median': np.median,
        'lognorm': sigma_lognorm,
        'norm': sigma_norm,
        'mad': mad,
        'mean_squared_error': mean_squared_err,
        'mean_absolute_error': mean_abs_err,
        'halfnorm': sigma_halfnorm,
        'halfcauchy': width_halfcauchy,
        'cauchy': width_cauchy,
    }
    metrics_sample = {
        'norm': stats.norm,
        'lognorm': get_lognorm,
        'halfnorm': stats.halfnorm,
        'cauchy': stats.cauchy,
        'halfcauchy': stats.halfcauchy,
    }

    def __init__(self, ene_bins, cosz_bins, metric='median'):
        self.ene_bins = ene_bins
        self.cosz_bins = cosz_bins
        self._is_fitted = False
        self._hist_fitted = False
        self.log = logging.getLogger(self.__class__.__name__)
        self._set_metric(metric)
        self._hists = {}

    def _set_metric(self, metric):
        if isinstance(metric, string_types):
            try:
                self.metric = self.metrics_avail[metric]
                self.metric_name = metric
            except KeyError:
                raise KeyError(
                    "Unknown metric '{}'. Available metrics are: {}".format(
                        metric, list(self.metrics_avail.keys())))
        else:
            self.metric = metric
            self.metric_name = metric.__name__

    def _assert_shapes(self):
        self.nbins_ene = len(self.ene_bins) - 1
        self.nbins_cosz = len(self.cosz_bins) - 1
        assert self._resol.shape[0] >= self.nbins_ene
        assert self._resol.shape[1] >= self.nbins_cosz

    def fit(self, residuals, energy, cosz, use_histogram=True):
        residuals = np.atleast_1d(residuals)
        cosz = np.atleast_1d(cosz)
        energy = np.atleast_1d(energy)

        df = pd.DataFrame({
            'energy': energy,
            'cosz': cosz,
            'residuals': residuals,
        })
        df['ene_bins'] = pd.cut(df.energy, self.ene_bins, labels=None)
        df['cosz_bins'] = pd.cut(df.cosz, self.cosz_bins, labels=None)
        grp = df.groupby(['ene_bins', 'cosz_bins'])
        meas = grp['residuals'].agg(self.metric)
        if use_histogram:
            for (ebin, czbin), subdf in grp:
                e_i, c_i = self._get_bins(subdf.energy, subdf.cosz)
                # we are in groupby(bin), so all should go into same bin
                # still, be sure -- else there is no point in continuing!
                assert np.std(e_i) < 0.01
                assert np.std(c_i) < 0.01
                e = int(e_i[0])
                c = int(c_i[0])
                self._hists[(e, c)] = self._fit_histogram(
                    subdf['residuals'])
            self._hist_fitted = True
        else:
            self._hist_fitted = False
        self._resol = meas.unstack().values.copy()
        self._assert_shapes()
        self._is_fitted = True

    def _fit_histogram(self, arr, **histargs):
        if 'bins' not in histargs:
            histargs['bins'] = 'auto'
        hist = np.histogram(arr, **histargs)
        return hist

    def _named_df(self):
        eb_ = pd.IntervalIndex.from_breaks(self.ene_bins, name='Energy Bins')
        cb_ = pd.IntervalIndex.from_breaks(self.cosz_bins, name='Cos Zen Bins')
        df_named = pd.DataFrame(self._resol, index=eb_, columns=cb_)
        return df_named

    def _assert_fitted(self):
        if not self._is_fitted:
            raise NotFittedError(
                "Not fitted! Either call fit or load a prefitted model!")

    def _assert_hist_fitted(self):
        if not self._hist_fitted:
            raise NotFittedError(
                "Histograms Not fitted!")

    def plot(self, annot=True, **kwargs):
        self._assert_fitted()
        data = self._named_df()
        return sns.heatmap(data, annot=True, **kwargs)

    def plot_hists(self, showmedian=True, logx=False, logy=False,
                   xmax=np.pi, xmin=0.01, nx=100):
        self._assert_hist_fitted()
        nrows, ncols = self._resol.shape
        fig, axes = plt.subplots(ncols=ncols, nrows=nrows,
                                 figsize=(3 * ncols, 2 * nrows))
        for ri in range(nrows):
            for ci in range(ncols):
                ax = axes[ri, ci]
                h = self._get_hist_rv(ri, ci)
                if logx:
                    x = np.geomspace(xmin, xmax, nx)
                else:
                    x = np.linspace(xmin, xmax, nx)
                if showmedian:
                    ax.axvline(h.median(), color='r', linewidth=3)
                if logx:
                    ax.set_xscale('log')
                if logy:
                    ax.set_yscale('log')
                ax.fill_between(x, h.pdf(x), step='pre', alpha=.66)

    def _get_bins(self, energy, cosz, clip_bins=True):
        # self._assert_fitted()
        cosz = np.atleast_1d(cosz)
        energy = np.atleast_1d(energy)
        e_i = np.digitize(energy, self.ene_bins) - 1
        c_i = np.digitize(cosz, self.cosz_bins) - 1
        max_ei = len(self.ene_bins)
        max_ci = len(self.cosz_bins)
        if clip_bins:
            e_i = np.clip(e_i, a_min=0, a_max=max_ei)
            c_i = np.clip(c_i, a_min=0, a_max=max_ei)
        assert np.all(e_i <= max_ei)
        assert np.all(c_i <= max_ci)
        return e_i, c_i

    def estimate(self, energy, cosz, clip_bins=True):
        self._assert_fitted()
        e_i, c_i = self._get_bins(energy, cosz, clip_bins)
        return self._resol[e_i, c_i]

    def _get_hist_rv(self, e, c):
        return stats.rv_histogram(self._hists[(e, c)])

    def sample(self, energy, cosz, clip_bins=True, use_histogram=False):
        e_i, c_i = self._get_bins(energy, cosz, clip_bins)
        n_samp = len(energy)
        if use_histogram:
            self._assert_hist_fitted()
        else:
            if self.metric_name not in self.metrics_sample:
                raise NotImplementedError(
                    "Metric '{} does not support resampling! "
                    "Supported metrics are: {}".format(
                        self.metric_name,
                        list(self.metrics_sample.keys())))
            rv = self.metrics_sample[self.metric_name]
        out = np.zeros(n_samp)
        tups = np.column_stack((e_i, c_i))
        for e, c in np.unique(tups, axis=0):
            spread = self._resol[e, c]
            if use_histogram:
                dist = self._get_hist_rv(e, c)
            # SHOULD work on edge cases like lognorm
            else:
                dist = rv(spread)
            mask = ((e_i == e) & (c_i == c))
            n_samp = np.sum(mask)
            if n_samp == 0:
                continue
            offsets = dist.rvs(size=n_samp)
            out[mask] = offsets
        return out

    @classmethod
    def _from_arrays(cls, matrix, ene_bins, cosz_bins, metric='median'):
        r = cls(ene_bins, cosz_bins, metric=metric)
        r._resol = matrix
        r._is_fitted = True
        return r

    def save(self, filename, mode='w'):
        # dump matrix, bins, binlimx to h5
        filt_kws = {
            'fletcher32': True,
            'shuffle': True,
            'compression': 'gzip',
            'compression_opts': 5,
        }
        with h5py.File(filename, mode) as h5:
            h5.create_dataset('/binned_res/ene_bins', data=self.ene_bins,
                              **filt_kws)
            h5.create_dataset('/binned_res/cosz_bins', data=self.cosz_bins,
                              **filt_kws)
            h5.create_dataset('/binned_res/matrix', data=self._resol,
                              **filt_kws)
            h5['/binned_res'].attrs['metric'] = self.metric_name
            if self._hist_fitted:
                for idx, h in self._hists.items():
                    ei, ci = idx
                    hcounts, hlims = h
                    grpname = '/binned_res/hists/ebin{}_czbin{}'.format(
                        ei, ci)
                    h5.create_dataset(grpname + '/' + 'counts',
                                      data=hcounts, **filt_kws)
                    h5.create_dataset(grpname + '/' + 'binlims',
                                      data=hlims, **filt_kws)

    @classmethod
    def load(cls, filename, **kwargs):
        # load matrix, bin, binlims from h5 -> init + "fit"
        with h5py.File(filename, 'r') as h5:
            ene_bins = h5['/binned_res/ene_bins'][:]
            cosz_bins = h5['/binned_res/cosz_bins'][:]
            matrix = h5['/binned_res/matrix'][:]
            metric_name = h5['/binned_res'].attrs['metric']
            if '/binned_res/hists' in h5:
                use_hists = True
                hists = {}
                expr = 'ebin(\d+)_czbin(\d+)'
                for grpname, gr in h5['/binned_res/hists'].items():
                    ei, ci = (int(k) for k in re.findall(expr, grpname)[0])
                    counts = gr['counts'][:]
                    binlims = gr['binlims'][:]
                    hists[(ei, ci)] = (counts, binlims)

        resol = cls._from_arrays(matrix, ene_bins, cosz_bins,
                                 metric=metric_name, **kwargs)
        if use_hists:
            resol._hists = hists
            resol._hist_fitted = True
        return resol

    def __mul__(self, x):
        self._resol *= x
        return self

    def __truediv__(self, x):
        self._resol /= x
        return self


class Morph(stats.rv_histogram):
    """Wrapper class for DM Halo Profiles.

    Basically a subclass for scipy.stats.rv_histogram.

    Parameters
    ==========
    morphname: string, optional (default='nfw_new')
        Name of the halo model.
    normed: bool, optional (default=True)
        Return a normalized distribution?
    """
    def __init__(self, morphname='nfw_new', normed=True):
        counts, binlims = gc_morph(morphname, full_lims=True)
        norm = np.sum(np.diff(binlims) * counts)
        if normed:
            counts /= norm
        super(Morph, self).__init__((counts, binlims),
                                    name="morph_{}".format(morphname))
        self.integrated_morph = norm


def ConvKernelGen(rv, grid=None):
    """Build a astropy-compatible convolution kernel out of a scipy pdf.

    Parameters
    ==========
    rv: instanve of scipy.stats.rv_continuous
        The input pdf. should be zero-centered.
    grid: array-like, optional (default=None)
        Grid on whic to evaluate the convolution.
        If None, default is 500 points between -10 and 10.
    """
    if grid is None:
        grid = np.linspace(-10, 10, 501)
    pdf = rv.pdf(grid)
    kern = CustomKernel(pdf)
    kern.normalize()
    return kern


class BackgroundSky(object):
    """Generate random uniform background from a DF with zenith+azimuth.
    """
    def __init__(self, mc_dataframe, bkg=None):
        self.df = mc_dataframe

    def uniform_detector(self, n_evts, wgt=None):
        samp = self.df.sample(n_evts, replace=True, weights=wgt)
        samp['time'] = random_date(n_evts, astropy_time=False)
        samp['azimuth'] = random_azimuth(n_evts)
        return samp

    def background_astro(self, n_evts, wgt=None):
        evts = self.uniform_detector(n_evts, wgt)
        astro_evts = local_event(azimuth=evts.azimuth, zenith=evts.zenith,
                                 time=evts.time)
        return astro_evts.icrs


class KDERV(stats.rv_continuous):
    """Create a `scipy.stats.rv_continuous` instance from a (gaussian) KDE.

    Uses the KDE implementation from sklearn.
    """
    def __init__(self, data, bw=None, **fitargs):
        data = np.atleast_1d(data)
        if bw is None:
            bw = self._bandwidth(data, **fitargs)
        data = data.reshape(-1, 1)
        self.kde = KernelDensity(bandwidth=bw).fit(data)
        super(KDERV, self).__init__(name='KDE')

    def _bandwidth(cls, sample, **fitargs):
        gkde = stats.gaussian_kde(sample, **fitargs)
        f = gkde.covariance_factor()
        bw = f * sample.std()
        return bw

    def _pdf(self, x):
        x = np.atleast_1d(x).reshape(-1, 1)
        log_pdf = self.kde.score_samples(x)
        pdf = np.exp(log_pdf)
        return pdf

    def _rvs(self, *args, **kwargs):
        # don't ask me why it uses `self._size`
        return self.kde.sample(n_samples=self._size)


def SmoothDist(dist, grid, *args, **kwargs):
    """Create a `rv_continuous subclass from a given pdf.

    Approximates distribution as stepfunction/histogram.
    Treats the given input as bincenters + bin heights.
    """
    def bincenters_to_bins(x):
        bw = (x[1] - x[0]) / 2
        cen = (x[1:] + x[:-1]) / 2
        cen = np.insert(cen, 0, x[0] - bw)
        cen = np.append(cen, x[-1] + bw)
        return cen
    lims = bincenters_to_bins(grid)
    return stats.rv_histogram((dist, lims), *args, **kwargs)


def cauchy_1d_kernel(gam=2, sup_range=10, nsup=501):
    """Build a cauchy (lorentz) convolution kernel."""
    sup = np.linspace(-sup_range, sup_range, nsup)
    c = stats.cauchy(0, gam)      # gamma = fwhm/2
    cc = ConvKernelGen(c, grid=sup)
    # lorentz = Lorentz1D(fwhm=2*gam)
    cc.normalize()
    return cc


def bkg_sun(samp, time, kernel, x=None):
    if x is None:
        x = np.linspace(-10, 200, 5000)
    sun_pos = sun_local(samp.time)
    sep_sun_deg = sun_pos.separation(samp).deg
    sep_sun = KDERV(sep_sun_deg)
    dist = SmoothDist(
        convolve(sep_sun.pdf(x), kernel),
        x,
        name='Sun'
    )
    return dist


def sig_sun(gam=2):
    return stats.cauchy(0, gam)


def bkg_gc(samp, kernel, x=None):
    if x is None:
        x = np.linspace(-10, 200, 5000)
    samp = samp.icrs
    gc = GALACTIC_CENTER.icrs
    sep_gc_deg = samp.separation(gc).deg
    sep_gc = KDERV(sep_gc_deg)
    dist = SmoothDist(
        convolve(sep_gc.pdf(x), kernel),
        x,
        name='Atmo'
    )
    return dist


def sig_gc(kernel, morph='einasto', x=None):
    if x is None:
        x = np.linspace(-10, 200, 5000)
    halo = Morph(morph)
    dist = SmoothDist(
        convolve(halo.pdf(x), kernel),
        x,
        name=morph,
    )
    return dist
