#!/usr/bin/python
import numpy as np
import math
import scipy as sp
import scipy.stats as stats
import sys
from suftware.utils import ControlledError

# List of supported distributions by name
VALID_DISTRIBUTIONS = '''
gaussian
narrow
wide
foothills
accordian
goalposts
towers
uniform
beta_convex
beta_concave
exponential
gamma
triangular
laplace
vonmises
'''.split()

# Maximum number of samples this algorithm will simulate
MAX_DATASET_SIZE = 1E6

class Results(): pass;

def gaussian_mixture(N,weights,mus,sigmas,bbox):
    assert bbox[1] > bbox[0]
    assert len(weights)==len(mus)==len(sigmas)

    # Get xs to sample
    xs = np.linspace(bbox[0],bbox[1],1E4)

    # Build pdf strings
    pdf_py = '0'
    pdf_js = '0'
    for m, s, w in zip(mus,sigmas,weights):
        pdf_py +='+(%f/%f)*np.exp(-0.5*np.power((x-(%f))/%f,2))'%(w,s,m,s)
        pdf_js +='+(%f/%f)*Math.exp(-0.5*Math.pow((x-(%f))/%f,2))'%(w,s,m,s)

    # Evaluate pdf at xs
    ps = np.zeros(len(xs))
    for i,x in enumerate(xs):
        ps[i] = eval(pdf_py)
    ps /= sum(ps)

    # Sample datapoints
    data = np.random.choice(xs, size=N, replace=True, p=ps)

    # Return valuables
    return data, pdf_py, pdf_js

class SimulatedDataset:
    """
    Simulates data from a variety of distributions.

    Parameters
    ----------

    distribution: (str)
        The distribution from which to draw data. Run sw.SimulatedDataset.list()
        to which distributions are available.

    num_data_points: (int > 0)
        The number of data points to simulate. Must satisfy
        0 <= N <= MAX_DATASET_SIZE.

    seed: (int)
        Seed passed to random number generator.
    """

    def __init__(self,
                 distribution='gaussian',
                 num_data_points=100,
                 seed=None):

        periodic = False

        # If seed is specified, set it
        if not (seed is None):
            np.random.seed(seed)
        else:
            np.random.seed(None)

        # If gaussian distribution
        if distribution == 'gaussian':
            description = 'Gaussian distribution'
            mus = [0.]
            sigmas = [1.]
            weights = [1.]
            bounding_box = [-5,5]
            data, pdf_py, pdf_js = gaussian_mixture(num_data_points, weights, mus, sigmas, bounding_box)

        # If mixture of two gaussian distributions
        elif distribution == 'narrow':
            description = 'Gaussian mixture, narrow separation'
            mus = [-1.25, 1.25]
            sigmas = [1., 1.]
            weights = [1., 1.]
            bounding_box = [-6, 6]
            data, pdf_py, pdf_js = gaussian_mixture(num_data_points, weights, mus, sigmas, bounding_box)

        # If mixture of two gaussian distributions
        elif distribution == 'wide':
            description = 'Gaussian mixture, wide separation'
            mus = [-2.0, 2.0]
            sigmas = [1.0, 1.0]
            weights = [1.0, 0.5]
            bounding_box = [-6.0, 6.0]
            data, pdf_py, pdf_js = gaussian_mixture(num_data_points, weights, mus, sigmas, bounding_box)

        elif distribution == 'foothills':
            description = 'Foothills (Gaussian mixture)'
            mus = [0., 5., 8., 10, 11]
            sigmas = [2., 1., 0.5, 0.25, 0.125]
            weights = [1., 1., 1., 1., 1.]
            bounding_box = [-5,12]
            data, pdf_py, pdf_js = gaussian_mixture(num_data_points, weights, mus, sigmas, bounding_box)

        elif distribution == 'accordian':
            description = 'Accordian (Gaussian mixture)'
            mus = [0., 5., 8., 10, 11, 11.5]
            sigmas = [2., 1., 0.5, 0.25, 0.125, 0.0625]
            weights = [16., 8., 4., 2., 1., 0.5]
            bounding_box = [-5,13]
            data, pdf_py, pdf_js = gaussian_mixture(num_data_points, weights, mus, sigmas, bounding_box)

        elif distribution == 'goalposts':
            description = 'Goalposts (Gaussian mixture)'
            mus = [-20, 20]
            sigmas = [1., 1.]
            weights = [1., 1.]
            bounding_box = [-25,25]
            data, pdf_py, pdf_js = gaussian_mixture(num_data_points, weights, mus, sigmas, bounding_box)

        elif distribution == 'towers':
            description = 'Towers (Gaussian mixture)'
            mus = [-20, -15, -10, -5, 0, 5, 10, 15, 20]
            sigmas = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
            weights = [1., 1., 1., 1., 1., 1., 1., 1., 1.]
            bounding_box = [-25,25]
            data, pdf_py, pdf_js = gaussian_mixture(num_data_points, weights, mus, sigmas, bounding_box)

        # If uniform distribution
        elif distribution == 'uniform':
            data = stats.uniform.rvs(size=num_data_points)
            bounding_box = [0,1]
            description = 'Uniform distribution'
            pdf_js = "1.0"
            pdf_py = "1.0"

        # Convex beta distribution
        elif distribution == 'beta_convex':
            data = stats.beta.rvs(a=0.5, b=0.5, size=num_data_points)
            bounding_box = [0,1]
            description = 'Convex beta distribtuion'
            pdf_js = "Math.pow(x,-0.5)*Math.pow(1-x,-0.5)*math.gamma(1)/(math.gamma(0.5)*math.gamma(0.5))"
            pdf_py = "np.power(x,-0.5)*np.power(1-x,-0.5)*math.gamma(1)/(math.gamma(0.5)*math.gamma(0.5))"

        # Concave beta distribution
        elif distribution == 'beta_concave':
            data = stats.beta.rvs(a=2, b=2, size=num_data_points)
            bounding_box = [0,1]
            description = 'Concave beta distribution'
            pdf_js = "Math.pow(x,1)*Math.pow(1-x,1)*math.gamma(4)/(math.gamma(2)*math.gamma(2))"
            pdf_py = "np.power(x,1)*np.power(1-x,1)*math.gamma(4)/(math.gamma(2)*math.gamma(2))"

        # Exponential distribution
        elif distribution == 'exponential':
            data = stats.expon.rvs(size=num_data_points)
            bounding_box = [0,5]
            description = 'Exponential distribution'
            pdf_js = "Math.exp(-x)"
            pdf_py = "np.exp(-x)"

        # Gamma distribution
        elif distribution == 'gamma':
            data = stats.gamma.rvs(a=3, size=num_data_points)
            bounding_box = [0,10]
            description = 'Gamma distribution'
            pdf_js = "Math.pow(x,2)*Math.exp(-x)/math.gamma(3)"
            pdf_py = "np.power(x,2)*np.exp(-x)/math.gamma(3)"

        # Triangular distribution
        elif distribution == 'triangular':
            data = stats.triang.rvs(c=0.5, size=num_data_points)
            bounding_box = [0,1]
            description = 'Triangular distribution'
            pdf_js = "2-4*Math.abs(x - 0.5)"
            pdf_py = "2-4*np.abs(x - 0.5)"

        # Laplace distribution
        elif distribution == 'laplace':
            data = stats.laplace.rvs(size=num_data_points)
            bounding_box = [-5,5]
            description = "Laplace distribution"
            pdf_js = "0.5*Math.exp(- Math.abs(x))"
            pdf_py = "0.5*np.exp(- np.abs(x))"

        # von Misses distribution
        elif distribution == 'vonmises':
            data = stats.vonmises.rvs(1, size=num_data_points)
            bounding_box = [-3.14159,3.14159]
            periodic = True
            description = 'von Mises distribution'
            pdf_js = "Math.exp(Math.cos(x))/7.95493"
            pdf_py = "np.exp(np.cos(x))/7.95493"

        else:
            raise ControlledError('Distribution type "%s" not recognized.' % distribution)

        # Set these
        attributes = {
            'data': data,
            'bounding_box': bounding_box,
            'distribution': distribution,
            'pdf_js': pdf_js,
            'pdf_py': pdf_py,
            'periodic': periodic
        }
        for key, value in attributes.items():
            setattr(self, key, value)

    @staticmethod
    def list():
        """
        Return list of valid distributions.
        """