"""Common Likelihoods.

All the heavy lifting is done by ``statsmodels`` + ``scipy.optimize``.
"""
import numpy as np
from statsmodels.base.model import GenericLikelihoodModel

# n_sig: param to be fitted
# variables which span llh space: alpha, energy
# additional params: n_bkg, signal_pdf, background_pdf


class BaseLLHNoExog(GenericLikelihoodModel):
    """Likelihood base class.

    The signal and background distributions need to be specified yet.

    Parameters:
        endog: list[arrays]
            collection of your data vectors on which the
            likelihood is evaluated (i.e. energy, distance to source),
        signal: callable
            Signal distribution
        background: callable
            Background distribution
    """
    def __init__(self, endog, exog=None, signal=None,
                 background=None, **kwds):
        """Don't care about exogenous variables, don't have them.

        ``endog`` is a collection of your data vectors on which the
        likelihood is evaluated (i.e. energy, distance to source),
        but not the parameter we would like to fit! (e.g. number of
        signal events).
        """
        if signal is not None:
            self.signal = signal
        if background is not None:
            self.background = background
        exog = np.zeros_like(endog)
        super(BaseLLHNoExog, self).__init__(endog=endog, exog=exog, **kwds)

    @classmethod
    def signal(cls, *args):
        """Signal distribution"""
        raise NotImplementedError

    @classmethod
    def background(cls, *args):
        """Background distribution"""
        raise NotImplementedError

    def nloglikeobs(self, params):
        endog = self.endog
        ll = self.nlnlike(params, endog)
        return ll

    def nlnlike(self, params, endog):
        """The actual likelihood, with parameter + data vectors.

        Implement this in your subclass.
        """
        raise NotImplementedError


class PointSourceStandardLLH(BaseLLHNoExog):
    """Point Source Standard Likelihood.

    The signal and background distributions need to be specified yet.

    Parameters:
        endog: list[arrays]
            collection of your data vectors on which the
            likelihood is evaluated (i.e. energy, distance to source),
        signal: callable
            Signal distribution
        background: callable
            Background distribution
    """
    start_params = [42.0]
    param_names = ['n_signal']

    def nlnlike(self, params, endog):
        """The standard Negative Log Likelihood."""
        n_sig = params[0]
        alpha, energy = endog

        n_tot = alpha.shape[0]

        sig = self.signal.pdf(alpha, energy)
        bkg = self.background.pdf(alpha, energy)
        sumlogl = -np.ma.sum(
            np.ma.log(
                (n_sig / n_tot) * sig + ((n_tot - n_sig) / n_tot) * bkg
            )
        )
        return -sumlogl


class PointSourceExtendedLLH(BaseLLHNoExog):
    """Point Source Extended Likelihood.

    The signal and background distributions need to be specified yet.

    Parameters:
        endog: list[arrays]
            collection of your data vectors on which the
            likelihood is evaluated (i.e. energy, distance to source),
        n_bkg: integer, optional [default: 10000]
            Number of expected background events in sample.
        signal: callable
            Signal distribution
        background: callable
            Background distribution
    """
    start_params = [42.0]
    param_names = ['n_signal']

    def __init__(self, endog, n_bkg=10000, **kwds):
        """We need 1 additional parameter, the number of background events.
        """
        self.n_bkg = n_bkg
        super(PointSourceExtendedLLH, self).__init__(endog=endog, **kwds)

    def nlnlike(self, params, endog):
        """The extended Negative Log Likelihood."""
        n_sig = params[0]
        alpha, energy = endog
        sig = self.signal.pdf(alpha, energy)
        bkg = self.background.pdf(alpha, energy)
        sumlogl = -np.ma.sum(
            np.ma.log(
                n_sig * sig + self.n_bkg * bkg
            )
        ) - self.n_bkg - n_sig
        return -sumlogl


def std_nlnlike1d(params, endog, n_bkg_exp, signal_1d, background_1d):
    """Standard Negative Log Likelihood, 1D.

    Fit 1 parameter ``n_signal``,
    in 1 dimension ``alpha``
    (i.e. separation to source).
    """
    n_sig = params[0]
    alpha = np.atleast_1d(endog)
    n_tot = n_bkg_exp
    s = signal_1d.pdf(alpha)
    b = background_1d.pdf(alpha)
    sumlogl = np.ma.sum(
        np.ma.log(
            (n_sig / n_tot) * s + ((n_tot - n_sig) / n_tot) * b
        )
    )
    return -sumlogl


def std_nlnlike2d(params, endog, n_bkg_exp, signal_2d, background_2d):
    """Standard Negative Log Likelihood.

    Fit 1 parameter ``n_signal``,
    in 2 dimensions ``alpha, energy``
    (``alpha`` is separation to source).
    """
    n_sig = params[0]
    alpha, energy = endog
    alpha = np.atleast_1d(alpha)
    energy = np.atleast_1d(energy)
    n_tot = n_bkg_exp
    s = signal_2d.pdf(alpha, energy)
    b = background_2d.pdf(alpha, energy)
    sumlogl = np.ma.sum(
        np.ma.log(
            (n_sig / n_tot) * s + ((n_tot - n_sig) / n_tot) * b
        )
    )
    return -sumlogl


def ext_nlnlike1d(params, endog, signal_1d, background_1d):
    """Extended Negative Log Likelihood, 1D.

    Fit 2 parameters ``n_signal`` and ``n_background``,
    in 1 dimension ``alpha``
    (i.e. separation to source).
    """
    n_sig = params[0]
    n_bkg = params[1]
    n_tot = n_bkg + n_sig
    alpha = np.atleast_1d(endog)
    n_sky = len(alpha)
    s = signal_1d.pdf(alpha)
    b = background_1d.pdf(alpha)
    sumlogl = np.sum(
        np.log(
            (n_sig * s) + (n_bkg * b)
        )
    )
    # barlow, "ext ML", eqn (9)
    sumlogl -= n_tot
    sumlogl -= np.sum(np.log(np.arange(1, n_sky + 1)))
    return -sumlogl


def ext_nlnlike2d(params, endog, signal_2d, background_2d):
    """Extended Negative Log Likelihood.

    Fit 2 parameters ``n_signal`` and ``n_background``,
    in 2 dimensions ``alpha, energy``
    (``alpha`` is separation to source).
    """
    n_sig = params[0]
    n_bkg = params[1]
    n_tot = n_sig + n_bkg
    alpha, energy = endog
    alpha = np.atleast_1d(alpha)
    energy = np.atleast_1d(energy)
    n_sky = len(alpha)
    assert len(alpha) == len(energy)
    s = signal_2d.pdf(alpha, energy)
    b = background_2d.pdf(alpha, energy)
    sumlogl = np.sum(
        np.log(
            (n_sig * s) + (n_bkg * b)
        )
    )
    # barlow, "ext ML", eqn (9)
    sumlogl -= n_tot
    sumlogl -= np.sum(np.log(np.arange(1, n_sky + 1)))
    return -sumlogl
