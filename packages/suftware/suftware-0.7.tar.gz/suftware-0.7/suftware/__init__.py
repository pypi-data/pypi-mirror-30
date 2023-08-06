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

import utils
import maxent
import supplements
import deft_core

# Enable plotting
#from utils import enable_graphics

from suftware.utils import enable_graphics

# Make classes local
#from utils import ControlledError as ControlledError
from suftware.utils import ControlledError as ControlledError

from DensityEstimator import DensityEstimator
from SimulatedDataset import SimulatedDataset
from ExampleDataset import ExampleDataset
from DensityEvaluator import DensityEvaluator


# Classes that have yet to be written
class Density2DEstimator:
    """
    Future class for density estimation in a two dimensional area.
    """
    pass

class JointDensityEstimator:
    """
    Future class for estimating the joint distribution between two
    univariate quantities.
    """
    pass

class SurvivalCurveEstimator:
    """
    Future class for computing simple survival curves
    """
    pass

class ProportionalHazardsEstimator:
    """
    Future class for computing proportional hazards models
    """
    pass

class GeneralizedHazardsEstimator:
    """
    Future class for computing generalized hazards models
    """
    pass

class IntervalCensoredSurvivalEstimator:
    """
    Future class for computing interval-censored survival curves
    """

