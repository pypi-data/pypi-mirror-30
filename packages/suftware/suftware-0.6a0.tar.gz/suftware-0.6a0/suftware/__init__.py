"""
Head module. Contains classes for user interfacing.
"""

# choose correct path for module if python version is 3
import sys
if sys.version_info[0]==3:

	sys.path.insert(0,sys.path[len(sys.path)-1]+"/suftware")
	sys.path.insert(1,"./suftware")
	
	import pip
	for package in pip.get_installed_distributions():
		if 'suftware' in str(package):
				#print(package.location)
				sys.path.insert(2,package.location+"/suftware")

# Data simulation
from simulate_density_data import run as simulate_density_data
from simulate_density_data import VALID_DISTRIBUTIONS \
    as simulate_density_data__distribution_types

# Data examples
from example_density_data import run as example_density_data
from example_density_data import VALID_DATASETS \
    as example_density_data__datasets


import utils
import maxent
import supplements
import deft_core

# Density estimation
from density import Density
from interpolated_density import InterpolatedDensity
from interpolated_field import InterpolatedField

from utils import DeftError as ControlledError

# Enable plotting
from density import enable_graphics

# Classes that have yet to be written
class Density2D:
    """
    Future class for density estimation in a two dimensional area.
    """
    pass

class DensityJoint:
    """
    Future class for estimating the joint distribution between two
    univariate quantities.
    """
    pass

class Survival:
    """
    Future class for computing simple survival curves
    """
    pass

class ProportionalHazards:
    """
    Future class for computing proportional hazards models
    """
    pass

class GeneralizedHazards:
    """
    Future class for computing generalized hazards models
    """
    pass

class IntervalCensoredSurvival:
    """
    Future class for computing interval-censored survival curves
    """

