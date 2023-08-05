Change Log
==========

Unreleased Changes
------------------

0.4 (2018-03-19)
------------------
* add PseudoExperiment routines ``km3like.sim``
* Changed name: ``AngularResolution`` -> ``BinnedResolution``. Note:
  saved [as h5] resolutions are not compatible and have to be regenerated!
* ``BinnedResolution.{save,load}()`` now also use the histograms.
* add simple llh definitions (numpy functions for ``scipy.optimise.minimize``)

0.3 (2018-03-08)
----------------
* add pdf sampler
* namechange ``km3like.pseudo`` -> ``km3like.sample``
* Angular Resolution -> fits a parametric dist/nonparam histo in each 
  coszen, energy bin -> estimate uncertainty of an event, -> get random samples
  from the PSF to smear an event.

0.2.1 (2017-07-20)
------------------
* add BaseLLHNoExog and derive other pointsource classes from it
* add ScrambledBootstrap sampler (bootstrapped events + random azimuth/time)
