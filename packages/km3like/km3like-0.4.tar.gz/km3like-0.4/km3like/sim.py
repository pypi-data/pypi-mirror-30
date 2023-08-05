#!/usr/bin/env python
# coding=utf-8
# pylint: disable=C0103,R0903
# vim:set ts=4 sts=4 sw=4 et:

from __future__ import division, absolute_import, print_function

import numpy as np
import pandas as pd
from scipy import stats

from km3astro.random import random_azimuth, random_date
from km3astro.coord import orca_sun_dist, sun_local


def sim_background(df, return_df=True, n=None,
                   smear_background=False, resol=None):
    if n is not None:
        n_evts_samp = n
    else:
        n_evts = df.wgt_honda.sum()
        p = stats.poisson(n_evts)
        n_evts_samp = int(p.rvs(size=1))
    resamp = df.sample(
        n=n_evts_samp,
        replace=True,
        weights=df.wgt_honda
    )
    azi = random_azimuth(n=n_evts_samp)
    dat = random_date(n=n_evts_samp)
    alpha = orca_sun_dist(azi, dat, resamp.gandalf_zenith)
    if smear_background:
        if resol is None:
            raise ValueError("Pass a fitted BinnedResolution instance!")
        alpha_smear_bkg_len = resol.sample(
            resamp.gandalf_energy_corrected,
            resamp.gandalf_cos_zenith,
            use_histogram=True)
        alpha_smear_bkg = alpha_smear_bkg_len
        # smear the great-circle distance, in a random direction
        # (might be smeared towards or away from source)
        alpha_smear_bkg = np.abs(alpha_smear_bkg_len * np.cos(
            np.random.uniform(
                high=2 * np.pi,
                size=len(alpha_smear_bkg_len)
            )
        ))
        alpha += alpha_smear_bkg
    energy = np.array(resamp.gandalf_energy_corrected)
    if return_df:
        return pd.DataFrame({'energy': energy, 'alpha': alpha})
    return alpha, energy


def sim_signal(df, resol, n_sig=42, mass=1000.0, channel='W+ W-',
               oversample=5, return_df=True, poisson_sig=True):
    wsc = "wimpsim_{}_{}".format(channel, mass)
    if poisson_sig:
        p = stats.poisson(n_sig)
        n_sig_samp = int(p.rvs(size=1))
    else:
        n_sig_samp = n_sig
    # oversample here, since it might be above horizon
    sun_time = random_date(n=oversample * n_sig_samp)
    sun_zen = np.pi - sun_local(sun_time).alt.rad
    mask = np.cos(sun_zen) <= 0
    sun_zen = sun_zen[mask][:n_sig_samp]
    sun_time = sun_time[mask][:n_sig_samp]
    sun_ene = df.gandalf_energy_corrected.sample(
        n=n_sig_samp,
        replace=True,
        weights=df.wgt * df[wsc]
    )
    energy = np.array(sun_ene)
    alpha_smear_sig = resol.sample(
        sun_ene,
        np.cos(sun_zen),
        use_histogram=True
    )
    if return_df:
        return pd.DataFrame({'energy': energy, 'alpha': alpha_smear_sig})
    return alpha_smear_sig, sun_ene


def sim_sky(data, n_sig=42, *args, **kwargs):
    bkg = sim_background(data, return_df=True)
    sig = sim_signal(data, return_df=True, n_sig=n_sig, *args, **kwargs)
    sky = pd.concat([sig, bkg])
    return sky
