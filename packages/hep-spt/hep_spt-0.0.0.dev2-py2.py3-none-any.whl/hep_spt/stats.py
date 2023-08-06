'''
Function and classes representing statistical tools.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']


# Python
import os, warnings
import numpy as np
from math import exp, log, sqrt
from scipy.interpolate import interp1d
from scipy.optimize import fsolve
from scipy.special import gamma
from scipy.stats import beta, chi2, kstwobign, poisson
from scipy.stats import ks_2samp as scipy_ks_2samp

# Local
from hep_spt import __project_path__
from hep_spt.core import decorate

# Define confidence intervals.
__chi2_one_dof__ = chi2(1)
__one_sigma__    = __chi2_one_dof__.cdf(1)

# Number after which the poisson uncertainty is considered to
# be the same as that of a gaussian with "std = sqrt(lambda)".
__poisson_to_gauss__ = 200


__all__ = ['calc_poisson_fu',
           'calc_poisson_llu',
           'cp_fu',
           'FlatDistTransform',
           'ks_2samp',
           'gauss_u',
           'poisson_fu',
           'poisson_llu',
           'rv_random_sample',
           'sw2_u'
          ]


def _access_db( name ):
    '''
    Access a database table under 'data/'.

    :param name: name of the file holding the data.
    :type name: str
    :returns: array holding the data.
    :rtype: numpy.ndarray
    '''
    ifile = os.path.join(__project_path__, 'data', name)

    table = np.loadtxt(ifile)

    return table


@decorate(np.vectorize)
def calc_poisson_fu( m, cl = __one_sigma__ ):
    '''
    Return the lower and upper frequentist uncertainties for
    a poisson distribution with mean "m".

    :param m: mean of the Poisson distribution.
    :type m: float
    :param cl: confidence level (between 0 and 1).
    :type cl: float
    :returns: lower and upper uncertainties.
    :rtype: float, float

    .. note:: This function might turn very time consuming. Consider using :func:`poisson_fu` instead.
    '''
    sm = sqrt(m)

    alpha = (1. - cl)/2.

    il, ir = _poisson_initials(m)

    if m < 1:
        # In this case there is only an upper uncertainty, so
        # the coverage is reset so it covers the whole "cl"
        lw = m
        alpha *= 2.
    else:
        fleft = lambda l: 1. - (poisson.cdf(m, l) - poisson.pmf(m, l)) - alpha

        lw = fsolve(fleft, il)[0]

    fright = lambda l: poisson.cdf(m, l) - alpha

    up = fsolve(fright, ir)[0]

    return _process_poisson_u(m, lw, up)


@decorate(np.vectorize)
def calc_poisson_llu( m, cl = __one_sigma__ ):
    '''
    Calculate poisson uncertainties based on the logarithm of likelihood.

    :param m: mean of the Poisson distribution.
    :type m: float
    :param cl: confidence level (between 0 and 1).
    :type cl: float
    :returns: lower and upper uncertainties.
    :rtype: float, float

    .. note:: This function might turn very time consuming. Consider using :func:`poisson_llu` instead.
    '''
    ns = np.sqrt(__chi2_one_dof__.ppf(cl))

    nll = lambda x: -2.*np.log(poisson.pmf(m, x))

    ref = nll(m)

    func = lambda x: nll(x) - ref - ns

    il, ir = _poisson_initials(m)

    if m < 1:
        lw = m
    else:
        lw = fsolve(func, il)[0]

    up = fsolve(func, ir)[0]

    return _process_poisson_u(m, lw, up)


@decorate(np.vectorize)
def cp_fu( k, N, cl = __one_sigma__ ):
    '''
    Return the frequentist Clopper-Pearson uncertainties of having
    "k" events in "N".

    :param k: passed events.
    :type k: int
    :param N: total number of events.
    :type N: int
    :param cl: confidence level.
    :type cl: float
    :returns: lower and upper uncertainties on the efficiency.
    :rtype: float
    '''
    p = float(k)/N

    pcl = 0.5*(1. - cl)

    # Lower uncertainty
    if k != 0:
        lw = beta(k, N - k + 1).ppf(pcl)
    else:
        lw = p

    # Upper uncertainty
    if k != N:
        up = beta(k + 1, N - k).ppf(1. - pcl)
    else:
        up = p

    return p - lw, up - p


class FlatDistTransform:
    '''
    Instance to transform values following an unknown distribution :math:`f(x)`
    into a flat distribution. This class takes into account the inverse
    transform sampling theorem, which states that, given a distribution
    :math:`f(x)` where :math:`x\\in[a, b]` then, given a random variable
    following a flat distribution *r*,

    .. math::
       F(x) - F(x_0) = \int_{x_0}^x f(x) dx = \int_0^r r dr = r

    where :math:`F(x)` is the primitive of :math:`f(x)`. This allows us to
    generate values following the distribution :math:`f(x)` given values from
    a flat distribution

    .. math::
       x = F^{-1}(r + F(x_0))

    In this class, the inverse process is performed. From a given set of values
    of a certain distribution, we build a method to generate numbers following
    a flat distribution.

    The class performs an interpolation to get the transformated values from
    an array holding the cumulative of the distribution. The function
    :func:`scipy.interpolate.interp1d` is used for this purpose.
    '''
    def __init__( self, points, values=None, kind='cubic' ):
        '''
        Build the class from a given set of values following a certain
        distribution (the use of weights is allowed), or x and y values of
        a PDF. This last method is not recommended, since the precision
        relies on the dispersion of the values, sometimes concentrated around
        peaking regions which might not be well described by an interpolation.

        :param points: x-values of the distribution (PDF).
        :type points: numpy.ndarray
        :param values: weights or PDF values to use.
        :type values: numpy.ndarray
        :param kind: kind of interpolation to use. For more details see \
        :func:`scipy.interpolate.interp1d`.
        :type kind: str or int
        '''
        srt = points.argsort()

        points = points[srt]
        if values is None:
            c = np.linspace(1./len(points), 1., len(points))
        else:
            c  = np.cumsum(values[srt])
            c *= 1./c[-1]

        self._trans = interp1d(points, c,
                               copy=False,
                               kind=kind,
                               bounds_error=False,
                               fill_value=(0, 1)
        )

    def transform( self, values ):
        '''
        Return the value of the transformation of the given values.

        :param values: values to transform.
        :type values: array-like
        '''
        return self._trans(values)


def gauss_u( s, cl = __one_sigma__ ):
    '''
    Calculate the gaussian uncertainty for a given confidence level.

    :param s: standard deviation of the gaussian.
    :type s: float or collection(float)
    :param cl: confidence level.
    :type cl: float
    :returns: gaussian uncertainty.
    :rtype: float or collection(float)
    '''
    n = np.sqrt(__chi2_one_dof__.ppf(cl))

    return n*s


def _ks_2samp_values( arr, weights = None ):
    '''
    Calculate the values needed to perform the Kolmogorov-Smirnov test.

    :param arr: input sample.
    :type arr: array-like
    :param weights: possible weights.
    :type weights: array-like
    :returns: sorted sample, stack with the cumulative distribution and
    sum of weights.
    :rtype: array-like, array-like, float
    '''
    weights = weights if weights is not None else np.ones(len(arr), dtype=float)

    ix  = np.argsort(arr)
    arr = arr[ix]
    weights = weights[ix]

    cs = np.cumsum(weights)

    sw = cs[-1]

    hs = np.hstack((0, cs/sw))

    return arr, hs, sw


def ks_2samp( a, b, wa = None, wb = None ):
    '''
    Compute the Kolmogorov-Smirnov statistic on 2 samples. This is a two-sided
    test for the null hypothesis that 2 independent samples are drawn from the
    same continuous distribution. Weights for each sample are accepted. If no
    weights are provided, then the function scipy.stats.ks_2samp is called
    instead.

    :param a: first sample.
    :type a: array-like
    :param b: second sample.
    :type b: array-like
    :param wa: set of weights for "a". Same length as "a".
    :type wa: array-like or None.
    :param wb: set of weights for "b". Same length as "b".
    :type wb: array-like or None.
    :returns: test statistic and two-tailed p-value.
    :rtype: float, float
    '''
    if wa is None and wb is None:
        return scipy_ks_2samp(a, b)

    a, cwa, na = _ks_2samp_values(a, wa)
    b, cwb, nb = _ks_2samp_values(b, wb)

    m = np.concatenate([a, b])

    cdfa = cwa[np.searchsorted(a, m, side='right')]
    cdfb = cwb[np.searchsorted(b, m, side='right')]

    d = np.max(np.abs(cdfa - cdfb))

    en = np.sqrt(na*nb/float(na + nb))
    try:
        prob = kstwobign.sf((en + 0.12 + 0.11/en)*d)
    except:
        prob = 1.

    return d, prob


def poisson_fu( m ):
    '''
    Return the poisson frequentist uncertainty at one standard
    deviation of confidence level.

    :param m: measured value(s).
    :type m: array-like
    :returns: lower and upper frequentist uncertainties.
    :rtype: array-like(float, float)
    '''
    return _poisson_u_from_db(m, 'poisson_fu.dat')


def poisson_llu( m ):
    '''
    Return the poisson uncertainty at one standard deviation of
    confidence level. The lower and upper uncertainties are defined
    by those two points with a variation of one in the value of the
    negative logarithm of the likelihood multiplied by two:

    .. math::
       \sigma_\\text{low} = n_\\text{obs} - \lambda_\\text{low}

    .. math::
       \\alpha - 2\log P(n_\\text{obs}|\lambda_\\text{low}) = 1

    .. math::
       \sigma_\\text{up} = \lambda_\\text{up} - n_\\text{obs}

    .. math::
       \\alpha - 2\log P(n_\\text{obs}|\lambda_\\text{up}) = 1

    where :math:`\\alpha = 2\log P(n_\\text{obs}|n_\\text{obs})`.

    :param m: measured value(s).
    :type m: array-like
    :returns: lower and upper frequentist uncertainties.
    :rtype: array-like(float, float)
    '''
    return _poisson_u_from_db(m, 'poisson_llu.dat')


def _poisson_initials( m ):
    '''
    Return the boundaries to use as initial values in
    scipy.optimize.fsolve when calculating poissonian
    uncertainties.

    :param m: mean of the Poisson distribution.
    :type m: float
    :returns: upper and lower boundaries.
    :rtype: float, float
    '''
    sm = np.sqrt(m)

    il = m - sm
    if il <= 0:
        # Needed by "calc_poisson_llu"
        il = 0.1
    ir = m + sm

    return il, ir


def _poisson_u_from_db( m, database ):
    '''
    Decorator for functions to calculate poissonian uncertainties,
    which are partially stored on databases. If "m" is above the
    maximum number stored in the database, the gaussian approximation
    is taken instead.

    :param database: name of the database.
    :type database: str
    :returns: lower and upper frequentist uncertainties.
    :rtype: array-like(float, float)
    :raises TypeError: if the input array has non-integer values.
    '''
    m = np.array(m)
    if not np.issubdtype(m.dtype, np.integer):
        raise TypeError('Calling function with a non-integer value')

    scalar_input = False
    if m.ndim == 0:
        m = m[None]
        scalar_input = True

    no_app = (m < __poisson_to_gauss__)

    if np.count_nonzero(no_app) == 0:
        # We can use the gaussian approximation in all
        out = np.array(2*[np.sqrt(m)]).T
    else:
        # Non-approximated uncertainties
        table = _access_db(database)

        out = np.zeros((len(m), 2), dtype = np.float64)

        out[no_app] = table[m[no_app]]

        mk_app = np.logical_not(no_app)

        if mk_app.any():
            # Use the gaussian approximation for the rest
            out[mk_app] = np.array(2*[np.sqrt(m[mk_app])]).T

    if scalar_input:
        return np.squeeze(out)
    return out


def _process_poisson_u( m, lw, up ):
    '''
    Calculate the uncertainties and display an error if they
    have been incorrectly calculated.

    :param m: mean value.
    :type m: float
    :param lw: lower bound.
    :type lw: float
    :param up: upper bound.
    :type up: float
    :returns: lower and upper uncertainties.
    :type: array-like(float, float)
    '''
    s_lw = m - lw
    s_up = up - m

    if any(s < 0 for s in (s_lw, s_up)):
        warnings.warn('Poisson uncertainties have been '\
                      'incorrectly calculated')

    # numpy.vectorize needs to know the exact type of the output
    return float(s_lw), float(s_up)


def rv_random_sample( func, size = 10000, **kwargs ):
    '''
    Create a random sample from the given rv_frozen object. This is typically
    created after building a scipy.stats.rv_discrete or
    scipy.stats.rv_continuous functions.

    :param func: function to use for the generation.
    :type func: scipy.stats.rv_frozen
    :param size: size of the sample.
    :type size: int
    :param kwargs: any other argument to scipy.stats.rv_frozen.rvs.
    :type kwargs: dict
    :returns: generated sample.
    :rtype: array-like
    '''
    args = np.array(func.args)

    if len(args.shape) == 1:
        size = (size,)
    else:
        size = (size, args.shape[1])

    return func.rvs(size=size, **kwargs)


def sw2_u( arr, bins = 20, range = None, weights = None ):
    '''
    Calculate the errors of a weighted sample. This uncertainty is
    calculated as follows:

    .. math::

       \sigma_i = \sqrt{\sum_{j = 0}^n \omega_{i,j}^2}

    where *i* refers to the i-th bin and :math:`j \in [0, n]` refers to
    each entry in that bin with weight :math:`\omega_{i,j}`. If "weights" is
    None, then this coincides with the square root of the number of entries
    in each bin.

    :param arr: input array of data to process.
    :param bins: see :func:`numpy.histogram`.
    :type bins: int, sequence of scalars or str
    :param range: range to process in the input array.
    :type range: tuple(float, float)
    :param weights: possible weights for the histogram.
    :type weights: collection(value-type)
    :returns: symmetric uncertainty.
    :rtype: array-like
    '''
    if weights is not None:
        values = np.histogram(arr, bins, range, weights = weights*weights)[0]
    else:
        values = np.histogram(arr, bins, range)[0]

    return np.sqrt(values)


if __name__ == '__main__':
    '''
    Generate the tables to store the pre-calculated values of
    some uncertainties.
    '''
    m = np.arange(__poisson_to_gauss__)

    print('Creating databases:')
    for func in (calc_poisson_fu, calc_poisson_llu):

        ucts = np.array(func(m, __one_sigma__)).T

        name = func.__name__.replace('calc_', '') + '.dat'

        fpath = os.path.join('data', name)

        print('- {}'.format(fpath))

        np.savetxt(fpath, ucts)
