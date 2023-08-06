#!/usr/local/bin/python -W ignore
import scipy as sp
import numpy as np
import sys
import time
import pdb
import numbers

SMALL_NUM = 1E-6
MAX_NUM_GRID_POINTS = 1000
DEFAULT_NUM_GRID_POINTS = 100
MAX_NUM_POSTERIOR_SAMPLES = 1000
MAX_NUM_SAMPLES_FOR_Z = 1000

# Import deft-related code
import deft_core
import utils
import laplacian

from utils import DeftError
from interpolated_density import InterpolatedDensity
from interpolated_field import InterpolatedField

class Density:
    """This class will serve as the interface for running
    deft1d

    parameters
    ----------
    data: (np.array)
        User input data for which Deft1D will estimate the density.
    num_grid_points: (int)
        Number of grid points.
    grid: (np.array)
        Locations of grid points. Grid points must be evenly spaced in
        ascending order.
    alpha: (int)
        Smoothness parameter. Represents the order of the
        derivative in the action.
    bounding_box: ([float,float])
        Bounding box for density estimation.
    periodic: (boolean)
        Enforce periodic boundary conditions via True or False.
    evaluation_method_for_Z: (string)
        Method of evaluation of partition function. Possible values:
        'Lap'      : Laplace approximation (default).
        'Lap+Imp'  : Laplace approximation + importance sampling.
        'Lap+Fey'  : Laplace approximation + Feynman diagrams.
    num_samples_for_Z: (int)
        *** Note *** This parameter works only when evaluation_method_for_Z is 'Lap+Imp'.
        Number of samples for the evaluation of the partition function.
        More samples will help to evaluate a better density. More samples
        will also make calculation slower. num_samples_for_Z = 0 means the Laplace
        approximation for the evaluation of the partition function is used.
    resolution: (float > 0)
        Specifies max distance between neighboring points on the MAP curve.
    seed: (int)
        Specify random seed for evaluation of the partition function
        and for the posterior sampling.
    max_t_step: (float > 0)
        Maximum t step size on the MAP curve.
    max_log_evidence_ratio_drop: (float > 0)
        Stop criterion for traversing the MAP curve; deft stops when:
        max_log_evidence - current_log_evidence >  max_log_evidence_ratio_drop
    tolerance: (float > 0)
        Value which species convergence of phi.
    num_posterior_samples: (int >= 0)
        Number of posterior samples.
    sample_only_at_l_star: (boolean)
        If True : posterior samples drawn at l_star.
        If False: posterior sampling done among l near l_star.

    attributes
    ----------
    *** Note ***: all parameters are attributes except for results.
    results: (dict)
        Contains the results of deft.

    methods
    -------
    run():
        Runs the DEFT 1D algorithm.
    get_results_dict():
        Transforms the results object passed by run() into a dictionary, or
        returns a single specified attribute of the results object.
    get_Q_samples():
        Returns a list of sampled Qs in functionalized form.
    eval_samples():
        Evaluates sampled Qs on specified x values.
    """

    def __init__(self,
                 data,
                 grid=None,
                 grid_spacing=None,
                 num_grid_points=None,
                 bounding_box=None,
                 alpha=3,
                 periodic=False,
                 max_t_step=1.0,
                 tolerance=1E-6,
                 resolution=0.1,
                 num_posterior_samples=100,
                 sample_only_at_l_star=False,
                 max_log_evidence_ratio_drop=20,
                 evaluation_method_for_Z='Lap',
                 num_samples_for_Z=1000,
                 seed=None,
                 print_t=False,
                 should_fail=None):

        # Record other inputs as class attributes
        self.alpha = alpha
        self.grid = grid
        self.grid_spacing = grid_spacing
        self.num_grid_points = num_grid_points
        self.bounding_box = bounding_box
        self.periodic = periodic
        self.Z_evaluation_method = evaluation_method_for_Z
        self.num_samples_for_Z = num_samples_for_Z
        self.max_t_step = max_t_step
        self.print_t = print_t
        self.tolerance = tolerance
        self.seed = seed
        self.resolution = resolution
        self.num_posterior_samples = num_posterior_samples
        self.sample_only_at_l_star = sample_only_at_l_star
        self.max_log_evidence_ratio_drop = max_log_evidence_ratio_drop
        self.data = data
        self.results = None

        # Validate inputs
        try:
            self.inputs_check()

            # clean input data
            self.clean_data()

            # Choose grid
            self.set_grid()

            # Fit to data
            self.run()

            # Save some results
            self.results_dict = self.get_results_dict()
            self.histogram = self.results_dict['R']
            self.phi_star = InterpolatedField(self.results_dict['phi_star'],
                                              self.grid,
                                              self.bounding_box)
            self.Q_star = InterpolatedDensity(self.phi_star)
            self.evaluate = self.Q_star.evaluate
            self.values = self.evaluate(self.grid)
            self.sample_values = self.eval_samples(self.grid)

            if should_fail is True:
                print('MISTAKE: Succeeded but should have failed.')
                self.mistake = True
                #sys.exit(1)
            elif should_fail is False:
                print('Success, as expected.')
                self.mistake = False
            else:
                self.mistake = None


        except DeftError as e:
            if should_fail is True:
                print('Error, as expected:', e)
                self.mistake = False

            elif should_fail is False:
                print('MISTAKE: Failed but should have succeeded: ', e)
                self.mistake = True
                #sys.exit(1)

            else:
                print('Error: ', e)
                self.mistake = None
                #sys.exit(1)


    def set_grid(self):
        """
        Sets the grid based on user input
        :param: self
        :return: None
        """

        data = self.data
        grid = self.grid
        grid_spacing = self.grid_spacing
        num_grid_points = self.num_grid_points
        bounding_box = self.bounding_box
        alpha = self.alpha

        # If grid is specified
        if grid is not None:

            # Check and set number of grid points
            num_grid_points = len(grid)
            assert(num_grid_points >= 2*alpha)

            # Check and set grid spacing
            diffs = np.diff(grid)
            grid_spacing = diffs.mean()
            assert (grid_spacing > 0)
            assert (all(np.isclose(diffs, grid_spacing)))

            # Check and set grid bounds
            grid_padding = grid_spacing / 2
            lower_bound = grid[0] - grid_padding
            upper_bound = grid[-1] + grid_padding
            bounding_box = np.array([lower_bound, upper_bound])
            box_size = upper_bound - lower_bound

        # If grid is not specified
        if grid is None:

            ### First, set bounding box ###

            # If bounding box is specified, use that.
            if bounding_box is not None:
                assert bounding_box[0] < bounding_box[1]
                lower_bound = bounding_box[0]
                upper_bound = bounding_box[1]
                box_size = upper_bound - lower_bound


            # Otherwise set bounding box based on data
            else:
                assert isinstance(data, np.ndarray)
                assert all(np.isfinite(data))
                assert min(data) < max(data)

                # Choose bounding box to encapsulate all data, with extra room
                data_max = max(data)
                data_min = min(data)
                data_span = data_max - data_min
                lower_bound = data_min - .2 * data_span
                upper_bound = data_max + .2 * data_span

                # Autoadjust lower bound
                if data_min >= 0 and lower_bound < 0:
                    lower_bound = 0

                # Autoadjust upper bound
                if data_max <= 0 and upper_bound > 0:
                    upper_bound = 0
                if data_max <= 1 and upper_bound > 1:
                    upper_bound = 1
                if data_max <= 100 and upper_bound > 100:
                    upper_bound = 100

                # Extend bounding box outward a little for numerical safety
                lower_bound -= SMALL_NUM*data_span
                upper_bound += SMALL_NUM*data_span
                box_size = upper_bound - lower_bound

                # Set bounding box
                bounding_box = np.array([lower_bound, upper_bound])

            ### Next, define grid based on bounding box ###

            # If grid_spacing is specified
            if (grid_spacing is not None):
                assert isinstance(grid_spacing, float)
                assert np.isfinite(grid_spacing)
                assert grid_spacing > 0

                # Set number of grid points
                num_grid_points = np.floor(box_size/grid_spacing).astype(int)

                # Check num_grid_points isn't too small
                check(2*self.alpha <= num_grid_points,
                      'Using grid_spacing = %f ' % grid_spacing +
                      'produces num_grid_points = %d, ' % num_grid_points +
                      'which is too small. Reduce grid_spacing or do not set.')

                # Check num_grid_points isn't too large
                check(num_grid_points <= MAX_NUM_GRID_POINTS,
                      'Using grid_spacing = %f ' % grid_spacing +
                      'produces num_grid_points = %d, ' % num_grid_points +
                      'which is too big. Increase grid_spacing or do not set.')

                # Define grid padding
                # Note: grid_spacing/2 <= grid_padding < grid_spacing
                grid_padding = (box_size - (num_grid_points-1)*grid_spacing)/2
                assert (grid_spacing/2 <= grid_padding < grid_spacing)

                # Define grid to be centered in bounding box
                grid_start = lower_bound + grid_padding
                grid_stop = upper_bound - grid_padding
                grid = np.linspace(grid_start,
                                   grid_stop * (1 + SMALL_NUM), # For safety
                                   num_grid_points)

            # Otherwise, if num_grid_points is specified
            elif (num_grid_points is not None):
                assert isinstance(num_grid_points, int)
                assert 2*alpha <= num_grid_points <= MAX_NUM_GRID_POINTS

                # Set grid spacing
                grid_spacing = box_size / num_grid_points

                # Define grid padding
                grid_padding = grid_spacing/2

                # Define grid to be centered in bounding box
                grid_start = lower_bound + grid_padding
                grid_stop = upper_bound - grid_padding
                grid = np.linspace(grid_start,
                                   grid_stop * (1 + SMALL_NUM), # For safety
                                   num_grid_points)

            # Otherwise, set grid_spacing and num_grid_points based on data
            else:
                assert isinstance(data, np.ndarray)
                assert all(np.isfinite(data))
                assert min(data) < max(data)

                # Compute default grid spacing
                default_grid_spacing = box_size/DEFAULT_NUM_GRID_POINTS

                # Set minimum number of grid points
                min_num_grid_points = 2 * alpha

                # Set minimum grid spacing
                data.sort()
                diffs = np.diff(data)
                min_grid_spacing = min(diffs[diffs > 0])
                min_grid_spacing = min(min_grid_spacing,
                                       box_size/min_num_grid_points)

                # Set grid_spacing
                grid_spacing = max(min_grid_spacing, default_grid_spacing)

                # Set number of grid points
                num_grid_points = np.floor(box_size/grid_spacing).astype(int)

                # Set grid padding
                grid_padding = grid_spacing/2

                # Define grid to be centered in bounding box
                grid_start = lower_bound + grid_padding
                grid_stop = upper_bound - grid_padding
                grid = np.linspace(grid_start,
                                   grid_stop * (1 + SMALL_NUM),  # For safety
                                   num_grid_points)

        # Set final grid
        self.grid = grid
        self.grid_spacing = grid_spacing
        self.grid_padding = grid_padding
        self.num_grid_points = num_grid_points
        self.bounding_box = bounding_box
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.box_size = box_size

        # Make sure that the final number of gridpoints is ok.
        check(2 * self.alpha <= self.num_grid_points <= MAX_NUM_GRID_POINTS,
              'After setting grid, we find that num_grid_points = %d; must have %d <= len(grid) <= %d. ' %
              (self.num_grid_points, 2*self.alpha, MAX_NUM_GRID_POINTS) +
              'Something is wrong with input values of grid, grid_spacing, num_grid_points, or bounding_box.')

        # Set bin edges
        self.bin_edges = np.concatenate(([lower_bound],
                                         grid[:-1]+grid_spacing/2,
                                         [upper_bound]))


    def get_results_dict(self, key=None):
        """
        Returns a dictionary whose keys access the attributes of the
        results object returned by deft_1d.run()

        [DOCUMENT]
        """
        if self.results is not None and key is None:
            # return the dictionary containing results if no key provided
            return self.results.__dict__
        elif self.results is not None and key is not None:
            try:
                return self.results.__dict__.get(key)
                #return self.results.__getattribute__(key)
            except AttributeError as e:
                print("Get results:",e)
        else:
            print("Get Results: Deft results are none. Please run fit first.")


    def get_Q_samples(self, importance_resampling=True):
        """
        Produces a set of sampled Q distributions. By default these are chosen
        using importance resampling.

        [DOCUMENT]
        """

        # ensure parameters are legal
        if self.results is not None and self.num_posterior_samples is not 0:
            try:
                if not isinstance(importance_resampling,bool):
                    raise DeftError('Q_samples syntax error. Please ensure importance_resampling is of type bool')
            except DeftError as e:
                print(e)
                sys.exit(1)

            # return all samples here
            Q_Samples = []
            sample_weights = []
            for sampleIndex in range(self.num_posterior_samples):
                Q_Samples.append(
                    InterpolatedDensity(InterpolatedField(self.results_dict['phi_samples'][:, sampleIndex], self.grid, self.bounding_box)))

                sample_weights.append(self.results_dict['phi_weights'][sampleIndex])

            if importance_resampling:

                indices = range(self.num_posterior_samples)
                index_probs = sample_weights / sum(sample_weights)
                weighted_sample_indices = np.random.choice(indices, size=self.num_posterior_samples, p=index_probs)

                Q_samples_weighted = []
                for weight_index in weighted_sample_indices:
                    Q_samples_weighted.append(Q_Samples[weight_index])

                #print("Warning, returning list of Density objects; use index while using evaluate")
                # return weight samples as default
                return Q_samples_weighted

            #print("Warning, returning list of Density objects; use index while using evaluate")
            # we have samples Q_samples in a list

            return Q_Samples

        else:
            print("Q_Samples: Please ensure fit is run and posterior sampling method is not None")

    # returns Q_samples evaluated on the x-values provided
    def eval_samples(self, xs=None):
        """
        Evaluate sampled Qs at specified locations

        parameters:
            xs (np.array): Data points at which samples are evaluated
        return:
            values (np.array): Value of sampled Qs at provided x values. Returns
                None if no samples were taken
        """

        # If xs are not provided use grid
        if xs is None:
            xs = self.get_grid()

        # Evaluate Q_samples on grid and return
        if self.num_posterior_samples > 0:
            Q_samples = self.get_Q_samples()
            values = np.array([Q.evaluate(xs) for Q in Q_samples]).T
        else:
            values = None
        return values

    #
    # The main DEFT algorithm in 1D.
    #

    def run(self):
        """
        Runs DEFT 1D on data. Requires that all relevant input already be set
        as attributes of class instance.

        return:
            results (class instance): A container class whose attributes contain
            the results of the DEFT 1D algorithm.
        """

        # Extract information from Deft1D object
        data = self.data
        G = self.num_grid_points
        h = self.grid_spacing
        alpha = self.alpha
        periodic = self.periodic
        Z_eval = self.Z_evaluation_method
        num_Z_samples = self.num_samples_for_Z
        DT_MAX = self.max_t_step
        print_t = self.print_t
        tollerance = self.tolerance
        resolution = self.resolution
        deft_seed = self.seed
        num_pt_samples = self.num_posterior_samples
        fix_t_at_t_star = self.sample_only_at_l_star
        max_log_evidence_ratio_drop = self.max_log_evidence_ratio_drop

        # Start clock
        start_time = time.clock()

        # If deft_seed is specified, set it
        if not (deft_seed is None):
            np.random.seed(deft_seed)
        else:
            np.random.seed(None)

        # Create Laplacian
        laplacian_start_time = time.clock()
        if periodic:
            op_type = '1d_periodic'
        else:
            op_type = '1d_bilateral'
        Delta = laplacian.Laplacian(op_type, alpha, G)
        laplacian_compute_time = time.clock() - laplacian_start_time
        if print_t:
            print('Laplacian computed de novo in %f sec.'%laplacian_compute_time)

        # Get histogram counts and grid centers

        # Histogram based on bin centers
        counts, _ = np.histogram(data, self.bin_edges)
        N = sum(counts)

        # Make sure a sufficient number of bins are nonzero
        num_nonempty_bins = sum(counts > 0)
        check(num_nonempty_bins > self.alpha,
              'Histogram has %d nonempty bins; must be > %d.' %
              (num_nonempty_bins, self.alpha))

        # Compute initial t
        t_start = min(0.0, sp.log(N)-2.0*alpha*sp.log(alpha/h))
        if t_start < -10.0:
            t_start /= 2
        #print('t_start = %.2f' % t_start)
        if print_t:
            print('t_start = %0.2f' % t_start)

        # Do DEFT density estimation
        core_results = deft_core.run(counts, Delta, Z_eval, num_Z_samples, t_start, DT_MAX, print_t,
                                     tollerance, resolution, num_pt_samples, fix_t_at_t_star,max_log_evidence_ratio_drop)

        # Fill in results
        #copy_start_time = time.clock()
        results = core_results # Get all results from deft_core

        # Normalize densities properly
        results.h = h
        results.L = G*h
        results.R /= h
        results.Q_star /= h
        results.l_star = h*(sp.exp(-results.t_star)*N)**(1/(2.*alpha))
        for p in results.map_curve.points:
            p.Q /= h
        if not (num_pt_samples == 0):
            results.Q_samples /= h
        results.Delta = Delta

        # Store results
        self.results = results

    # Check inputs
    def inputs_check(self):
        """
        Check all inputs NOT having to do with the choice of grid
        :param self:
        :return: None
        """

        if self.grid_spacing is not None:

            # max_t_step is a number
            check(isinstance(self.grid_spacing, numbers.Real),
                  'type(grid_spacing) = %s; must be a number' %
                  type(self.grid_spacing))

            # grid_spacing is positive
            check(self.grid_spacing > 0,
                  'grid_spacing = %f; must be > 0.' % self.grid_spacing)

        if self.grid is not None:

            # grid is a list or np.array
            types = (list, np.ndarray, np.matrix)
            check(isinstance(self.grid, types),
                  'type(grid) = %s; must be a list or np.ndarray' %
                  type(self.grid))

            # cast grid as np.array as ints
            try:
                self.grid = np.array(self.grid).ravel().astype(float)
            except: # SHOULD BE MORE SPECIFIC
                raise DeftError('Cannot cast grid as 1D np.array of floats.')

            # grid has appropriate number of points
            check(2*self.alpha <= len(self.grid) <= MAX_NUM_GRID_POINTS,
                  'len(grid) = %d; must have %d <= len(grid) <= %d.' %
                  (len(self.grid), 2*self.alpha, MAX_NUM_GRID_POINTS))

            # grid is ordered
            diffs = np.diff(self.grid)
            check(all(diffs > 0),
                  'grid is not monotonically increasing.')

            # grid is evenly spaced
            check(all(np.isclose(diffs, diffs.mean())),
                  'grid is not evenly spaced; grid spacing = %f +- %f' %
                  (diffs.mean(), diffs.std()))

        # alpha is int
        check(isinstance(self.alpha, int),
              'type(alpha) = %s; must be int.' % type(self.alpha))

        # alpha in range
        check(1 <= self.alpha <= 4,
              'alpha = %d; must have 1 <= alpha <= 4' % self.alpha)

        if self.num_grid_points is not None:

            # num_grid_points is an integer
            check(isinstance(self.num_grid_points, int),
                  'type(num_grid_points) = %s; must be int.' %
                  type(self.num_grid_points))

            # num_grid_points is in the right range
            check(2*self.alpha <= self.num_grid_points <= MAX_NUM_GRID_POINTS,
              'num_grid_points = %d; must have %d <= num_grid_poitns <= %d.' %
              (self.num_grid_points, 2*self.alpha, MAX_NUM_GRID_POINTS))

        # bounding_box
        if self.bounding_box is not None:

            # bounding_box is right type
            box_types = (list, tuple, np.ndarray)
            check(isinstance(self.bounding_box, box_types),
                  'type(bounding_box) = %s; must be one of %s' %
                  (type(self.bounding_box), box_types))

            # bounding_box has right length
            check(len(self.bounding_box)==2,
                  'len(bounding_box) = %d; must be %d' %
                  (len(self.bounding_box), 2))

            # bounding_box entries must be numbers
            check(isinstance(self.bounding_box[0], numbers.Real) and
                  isinstance(self.bounding_box[1], numbers.Real),
                  'bounding_box = %s; entries must be numbers' %
                  repr(self.bounding_box))

            # bounding_box entries must be sorted
            check(self.bounding_box[0] < self.bounding_box[1],
                  'bounding_box = %s; entries must be sorted' %
                  repr(self.bounding_box))

            # reset bounding_box as tuple
            self.bounding_box = (float(self.bounding_box[0]),
                                 float(self.bounding_box[1]))

        # periodic is bool
        check(isinstance(self.periodic, bool),
              'type(periodic) = %s; must be bool' % type(self.periodic))

        # evaluation_method_for_Z is valid
        Z_evals = ['Lap', 'Lap+Imp', 'Lap+Fey']
        check(self.Z_evaluation_method in Z_evals,
              'Z_eval = %s; must be in %s' %
              (self.Z_evaluation_method, Z_evals))

        # num_samples_for_Z is an integer
        check(isinstance(self.num_samples_for_Z, numbers.Integral),
              'type(self.num_samples_for_Z) = %s; ' %
              type(self.num_samples_for_Z) +
              'must be integer.')
        self.num_samples_for_Z = int(self.num_samples_for_Z)

        # num_samples_for_Z is in range
        check(0 <= self.num_samples_for_Z <= MAX_NUM_SAMPLES_FOR_Z,
              'self.num_samples_for_Z = %d; ' % self.num_samples_for_Z +
              ' must satisfy 0 <= num_samples_for_Z <= %d.' %
               MAX_NUM_SAMPLES_FOR_Z)

        # max_t_step is a number
        check(isinstance(self.max_t_step, numbers.Real),
              'type(max_t_step) = %s; must be a number' %
              type(self.max_t_step))

        # max_t_step is positive
        check(self.max_t_step > 0,
              'maxt_t_step = %f; must be > 0.' % self.max_t_step)

        # print_t is bool
        check(isinstance(self.print_t,bool),
              'type(print_t) = %s; must be bool.' % type(self.print_t))

        # tolerance is float
        check(isinstance(self.tolerance, numbers.Real),
              'type(tolerance) = %s; must be number' % type(self.tolerance))

        # tolerance is positive
        check(self.tolerance > 0,
              'tolerance = %f; must be > 0' % self.tolerance)

        # resolution is number
        check(isinstance(self.resolution, numbers.Real),
              'type(resolution) = %s; must be number' % type(self.resolution))

        # resolution is positive
        check(self.resolution > 0,
              'resolution = %f; must be > 0' % self.resolution)

        if self.seed is not None:

            # seed is int
            check(isinstance(self.seed, int),
                  'type(seed) = %s; must be int' % type(self.seed))

            # seed is in range
            check(0 <= self.seed <= 2**32 - 1,
                  'seed = %d; must have 0 <= seed <= 2**32 - 1' % self.seed)

        # sample_only_at_l_star is bool
        check(isinstance(self.sample_only_at_l_star, bool),
              'type(sample_only_at_l_star) = %s; must be bool.' %
              type(self.sample_only_at_l_star))

        # num_posterior_samples is int
        check(isinstance(self.num_posterior_samples, numbers.Integral),
              'type(num_posterior_samples) = %s; must be integer' %
              type(self.num_posterior_samples))
        self.num_posterior_samples = int(self.num_posterior_samples)


        # num_posterior_samples is nonnegative
        check(0 <= self.num_posterior_samples <= MAX_NUM_POSTERIOR_SAMPLES,
              'num_posterior_samples = %f; need '%self.num_posterior_samples +
              '0 <= num_posterior_samples <= %d.' %MAX_NUM_POSTERIOR_SAMPLES)

        # max_log_evidence_ratio_drop is number
        check(isinstance(self.max_log_evidence_ratio_drop, numbers.Real),
              'type(max_log_evidence_ratio_drop) = %s; must be number' %
              type(self.max_log_evidence_ratio_drop))

        # max_log_evidence_ratio_drop is positive
        check(self.max_log_evidence_ratio_drop > 0,
              'max_log_evidence_ratio_drop = %f; must be > 0' %
              self.max_log_evidence_ratio_drop)

    # This method will be used to clean user input data; it's for use with the API.
    def clean_data(self):
        """
        Sanitize the assigned data
        :param: self
        :return: None
        """
        data = self.data

        try:
            # if data is a list or set, cast into numpy array
            if type(data) == list or type(data) == set:
                data = np.array(data)
            # if data already np array, do nothing
            elif type(data) == np.ndarray:
                pass
            # think about whether the following is a good idea
            elif type(data) != np.ndarray:
                data = np.array(data)
            else:
                raise DeftError("Error: could not cast data into an np.array")
        except DeftError as e:
            print(e)
            sys.exit(1)

        # remove nan's from the np data array
        data = data[~np.isnan(data)]
        # remove positive or negative infinite values from the np data array
        data = data[~np.isinf(data)]
        # remove complex numbers from data
        data = data[~np.iscomplex(data)]
        # make data floats
        data = data.astype(float)

        try:
            if not (len(data) > 0):
                raise DeftError(
                    'Input check failed, data must have length > 0: data = %s' % data)
        except DeftError as e:
            print(e)
            sys.exit(1)

        try:
            data_spread = max(data) - min(data)
            if not np.isfinite(data_spread):
                raise DeftError(
                    'Input check failed. Data[max]-Data[min] is not finite: Data spread = %s' % data_spread)
        except DeftError as e:
            print(e)
            sys.exit(1)

        try:
            if not (data_spread > 0):
                raise DeftError(
                    'Input check failed. Data[max]-Data[min] must be > 0: data_spread = %s' % data_spread)
        except DeftError as e:
            print(e)
            sys.exit(1)

        # Set cleaned data
        self.data = data

    def plot(self,
             ax=None,
             save_as=None,
             figsize=[4,4],
             fontsize=12,
             title='',
             xlabel='',
             tight_layout=False,
             show_now=True,
             num_posterior_samples=None,
             histogram_color='orange',
             histogram_alpha=1,
             posterior_color='dodgerblue',
             posterior_line_width=1,
             posterior_alpha=.2,
             color='blue',
             linewidth=2,
             alpha=1,
             backend='TkAgg'):
        """
        Visualize the estimated density
        :return: None
        """

        # check if matplotlib.pyplot is loaded. If not, load it carefully
        if 'matplotlib.pyplot' not in sys.modules:
            enable_graphics(backend=backend)

        ### Plot results ###
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
            tight_layout = True

        # Plot histogram
        ax.bar(self.grid,
               self.histogram,
               width=self.grid_spacing,
               color=histogram_color,
               alpha=histogram_alpha)

        # Set number of posterior samples to plot
        if num_posterior_samples is None:
            num_posterior_samples = self.num_posterior_samples

        # Plot posterior samples
        ax.plot(self.grid,
                self.sample_values[:, :num_posterior_samples],
                color=posterior_color,
                linewidth=posterior_line_width,
                alpha=posterior_alpha)

        # Plot best fit density
        ax.plot(self.grid,
                self.values,
                color=color,
                linewidth=linewidth,
                alpha=alpha)

        # Style plot
        ax.set_xlim(self.bounding_box)
        ax.set_title(title, fontsize=fontsize)
        ax.set_xlabel(xlabel, fontsize=fontsize)
        ax.set_yticks([])
        #ax.tick_params('x', rotation=45, labelsize=fontsize)
        ax.tick_params('x', labelsize=fontsize)

        # Do tight_layout if requested
        if tight_layout:
            plt.tight_layout()

        # Save figure if save_as is specified
        if save_as is not None:
            plt.draw()
            plt.savefig(save_as)

        # Show figure if show_now is True
        if show_now:
            plt.show()

def check(condition, message):
    '''
    Checks a condition; raises a DeftError with message if condition fails.
    :param condition:
    :param message:
    :return: None
    '''
    if not condition:
        raise DeftError(message)

def enable_graphics(backend='TkAgg'):
    """
    Must be called before any plotting routines will function

    :param backend: Graphical backend to use
    :return: None
    """
    try:
        global mpl
        import matplotlib as mpl
        mpl.use(backend)
        global plt
        import matplotlib.pyplot as plt
    except:
        raise DeftError('Could not import matplotlib.')