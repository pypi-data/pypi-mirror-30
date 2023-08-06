#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
import numpy as np
from numpy.testing import assert_almost_equal

from lmfit.models import LorentzianModel, GaussianModel
from qef.operators.convolve import Convolve


cases = ((LorentzianModel,
          0.004,
          lambda s1, s2: s1 + s2),
         (GaussianModel,
          0.0004,
          lambda s1, s2: np.sqrt(s1 * s1 + s2 * s2)))


@pytest.mark.parametrize('ComponentModel, de, sigma', cases)
def test_simplecases(ComponentModel, de, sigma):
    r"""Convolution of two Lorentzians is one Lorentzian, and convolution
     of two gaussians is one gaussian"""

    # Convolve two Lorentzians or convolve two Gaussians. Store the result
    # in dataset 'y'
    s1 = 0.011  # narrow component
    s2 = 0.163  # broad component
    c1 = ComponentModel(prefix='c1_')
    p = c1.make_params(amplitude=1.0, center=0.0, sigma=s1)
    c2 = ComponentModel(prefix='c2_')
    p.update(c2.make_params(amplitude=1.0, center=0.0, sigma=s2))
    e = de * np.arange(-250, 1500)  # energies in meV
    y = Convolve(c1, c2).eval(params=p, x=e)

    # Fit a Lorentzian to dataset 'y' or a Gaussian to dataset 'y'
    m = ComponentModel()
    params = m.guess(y, x=e)
    params['amplitude'].set(value=42.0)  # astray from correct value
    params['sigma'].set(value=4.2*sigma(s1, s2))  # astray from correct value
    r = m.fit(y, params, x=e)

    # The assertions will be carried out using not the dataset 'y' but
    # the fit we did to the dataset 'y'.
    # 1. Assert the convolution preserves the normalization
    assert_almost_equal(r.params['amplitude'], 1.0, decimal=3)

    # 1. Assert the convolution results in the appropriate combination for
    # their components' sigma values
    assert_almost_equal(r.params['sigma'], sigma(s1, s2), decimal=3)


if __name__ == '__main__':
    pytest.main([os.path.abspath(__file__)])
