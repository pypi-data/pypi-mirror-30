#!/usr/bin/env python
"""
Functional Tests for Suftware
"""

# Standard modules
import numpy as np
import sys

# Import suftware 
sys.path.append('../')
import suftware as sw

# Generate data
np.random.seed(0)
data = np.random.randn(100)

# simple test
sw.DensityEstimator(data)
global_mistake = False
global_test_success_counter = 0
global_test_fail_counter = 0


# helper method for functional test
def run_one_functional_test(**kw):
    functional_test = sw.DensityEstimator(data, **kw)
    global global_mistake
    global_mistake = functional_test.mistake
    if global_mistake is True:
        global global_test_fail_counter
        global_test_fail_counter += 1
    else:
        global global_test_success_counter
        global_test_success_counter += 1


# helper method for displaying pass/fail status
def display_local_status():
    print("Tests: passed: ", global_test_success_counter, ", tests failed: ", global_test_fail_counter,"\n")


def display_global_status():
    print('\033[1m' + "Total tests: passed: ", global_test_success_counter, " Total tests failed: ",
          global_test_fail_counter)


def run_grid_tests():
    print("Running Functional Test for parameter 'grid' \n")
    # grid Tests:
    # values to be tested that are expected to fail
    grid_fail_list = [5, 'x', set(np.linspace(-3, 3, 100)), np.linspace(-3, 3, 5),
                      np.linspace(-3, 3, 1001), np.linspace(-1E-6, 1E-6, 100),
                      np.linspace(-1E6, 1E6, 100)]

    # values to be tested that are expected to pass
    grid_success_list = [None, np.linspace(-3, 3, 100), np.linspace(-3, 3, 100).T, np.matrix(np.linspace(-3, 3, 100)),
                         np.matrix(np.linspace(-3, 3, 100).T), list(np.linspace(-3, 3, 100)), np.linspace(-3, 3, 6),
                         np.linspace(-3, 3, 100), np.linspace(-3, 3, 100), np.linspace(-3, 3, 1000)]

    # should fail
    [run_one_functional_test(grid=grid_fail_list[i], should_fail=True) for i in range(len(grid_fail_list))]
    # should pass
    [run_one_functional_test(grid=grid_success_list[i], should_fail=False) for i in range(len(grid_success_list))]

    display_local_status()


def run_grid_spacing_tests():
    print("Running Functional Test for parameter 'grid_spacing' \n")
    # values to be tested
    grid_spacing_fail_list = [0, 0.0, -0.1, '0.1', [0.1], 0.0001, 1000.0]
    grid_spacing_success_list = [None, 0.05, 0.1, 0.5]

    # should fail
    [run_one_functional_test(grid_spacing=grid_spacing_fail_list[i], should_fail=True) for i in
     range(len(grid_spacing_fail_list))]
    # should pass
    [run_one_functional_test(grid_spacing=grid_spacing_success_list[i], should_fail=False) for i in
     range(len(grid_spacing_success_list))]

    display_local_status()


def run_bound_box_tests():
    # bounding_box
    print("Running Functional Test for parameter 'bounding_box' \n")

    # values to be tested
    bbox_fail_list = [{-6, 6}, 6, [6], [-6, 0, 6], ['-6', '6'], [6, 6], [-1E-6, 1E-6], [-1E6, 1E6], [10, 20]]
    bbox_success_list = [[-6, 6], (-6, 6), np.array([-6, 6]), [-.1, .1], [-10, 10]]

    # should fail
    [run_one_functional_test(bounding_box=bbox_fail_list[i], should_fail=True) for i in range(len(bbox_fail_list))]
    # should pass
    [run_one_functional_test(bounding_box=bbox_success_list[i], should_fail=False) for i in
     range(len(bbox_success_list))]

    display_local_status()


def run_num_grid_points_tests():
    # num_grid_points
    print("Running Functional Test for parameter 'num_grid_points' \n")

    num_grid_points_fail_list = [-10, -1, 0, 1, 2, 3, 4, 5, 1001]
    num_grid_points_success_list = [6, 100, 1000]

    # should fail
    [run_one_functional_test(num_grid_points=num_grid_points_fail_list[i], should_fail=True) for i in
     range(len(num_grid_points_fail_list))]
    # should pass
    [run_one_functional_test(num_grid_points=num_grid_points_success_list[i], should_fail=False) for i in
     range(len(num_grid_points_success_list))]

    display_local_status()


def run_alpha_tests():
    # alpha
    print("Running Functional Test for parameter 'alpha' \n")

    # values to be tested
    alpha_fail_list = [None, 'x', -1, 0.0, 0, 0.1, 10]
    alpha_success_list = [1, 2, 3, 4]

    # should fail
    [run_one_functional_test(alpha=alpha_fail_list[i], should_fail=True) for i in range(len(alpha_fail_list))]
    # should pass
    [run_one_functional_test(alpha=alpha_success_list[i], should_fail=False) for i in range(len(alpha_success_list))]

    display_local_status()


def run_periodic_tests():
    # periodic
    print("Running Functional Test for parameter 'periodic' \n")

    # values to be tested
    periodic_fail_list = [0, -1, 'True', 'x', 1]
    perdiodic_success_list = [False, True]

    # should fail
    [run_one_functional_test(periodic=periodic_fail_list[i], should_fail=True) for i in range(len(periodic_fail_list))]
    # should pass
    [run_one_functional_test(periodic=perdiodic_success_list[i], should_fail=False) for i in
     range(len(perdiodic_success_list))]

    display_local_status()


def run_evaluation_method_for_Z_tests():
    # evaluation_method_for_Z
    print("Running Functional Test for parameter 'evaluation_method_for_Z' \n")

    # values to be tested
    Z_eval_fail_list = [0, 'x', 'Einstein', False]
    Z_eval_success_list = ['Lap', 'Lap+Fey', 'Lap+Imp']

    # should fail
    [run_one_functional_test(evaluation_method_for_Z=Z_eval_fail_list[i], should_fail=True) for i in
     range(len(Z_eval_fail_list))]
    # should pass
    [run_one_functional_test(evaluation_method_for_Z=Z_eval_success_list[i], should_fail=False) for i in
     range(len(Z_eval_success_list))]

    display_local_status()


def run_num_samples_for_Z_test():
    # num_samples_for_Z
    print("Running Functional Test for parameter 'num_samples_for_Z' \n")
    # Question: should a value of None pass or fail?

    # values to be tested
    num_samples_for_Z_fail_list = [None, -1, 'x', 0.1, 1001]
    num_samples_for_Z_success_list = [0, 1, 10, 1000]

    # should fail
    [run_one_functional_test(num_samples_for_Z=num_samples_for_Z_fail_list[i], should_fail=True) for i in
     range(len(num_samples_for_Z_fail_list))]
    # should pass
    [run_one_functional_test(num_samples_for_Z=num_samples_for_Z_success_list[i], should_fail=False) for i in
     range(len(num_samples_for_Z_success_list))]

    display_local_status()


def run_tolerance_tests():
    # tolerance
    print("Running Functional Test for parameter 'tolerance' \n")
    # values to be tested
    tolerance_fail_list = ['x', -1,0,0.0]
    tolerance_success_list = [1e-6, 1e-4, 1e-2, 1e-1, 1]

    # should fail
    [run_one_functional_test(tolerance=tolerance_fail_list[i], should_fail=True) for i in
     range(len(tolerance_fail_list))]
    # should pass
    [run_one_functional_test(tolerance=tolerance_success_list[i], should_fail=False) for i in
     range(len(tolerance_success_list))]

    display_local_status()


def run_resolution_tests():
    # resolution
    print("Running Functional Test for parameter 'resolution' \n")
    # values to be tested
    resolution_fail_list = ['x', -1,0,0.0, None]
    resolution_success_list = [1e-4, 1e-2, 1e-1, 1]

    # should fail
    [run_one_functional_test(resolution=resolution_fail_list[i], should_fail=True) for i in
     range(len(resolution_fail_list))]
    # should pass
    [run_one_functional_test(resolution=resolution_success_list[i], should_fail=False) for i in
     range(len(resolution_success_list))]

    display_local_status()


def run_seed_tests():
    # seed
    print("Running Functional Test for parameter 'seed' \n")
    # values to be tested
    seed_fail_list = ['x', 1e-5,1.0,-1]
    seed_success_list = [None,1,10,100,1000]

    # should fail
    [run_one_functional_test(seed=seed_fail_list[i], should_fail=True) for i in
     range(len(seed_fail_list))]
    # should pass
    [run_one_functional_test(seed=seed_success_list[i], should_fail=False) for i in
     range(len(seed_success_list))]

    display_local_status()


def run_print_t_tests():
    # print_t
    print("Running Functional Test for parameter 'print_t' \n")
    # values to be tested
    print_t_fail_list = ['x',1.0,-1,0,None]
    print_t_success_list = [False, True]

    # should fail
    [run_one_functional_test(print_t=print_t_fail_list[i], should_fail=True) for i in
     range(len(print_t_fail_list))]
    # should pass
    [run_one_functional_test(print_t=print_t_success_list[i], should_fail=False) for i in
     range(len(print_t_success_list))]

    display_local_status()


def run_num_posterior_samples_tests():
    # num_posterior_samples
    print("Running Functional Test for parameter 'num_posterior_samples' \n")
    # values to be tested
    num_posterior_samples_fail_list = ['x',-1,0.0,1001]
    num_posterior_samples_success_list = [0,1,2,3,10,100,1000]

    # should fail
    [run_one_functional_test(num_posterior_samples=num_posterior_samples_fail_list[i], should_fail=True) for i in
     range(len(num_posterior_samples_fail_list))]
    # should pass
    [run_one_functional_test(num_posterior_samples=num_posterior_samples_success_list[i], should_fail=False) for i in
     range(len(num_posterior_samples_success_list))]

    display_local_status()


def run_sample_only_at_l_star_tests():
    # sample_only_at_l_star
    print("Running Functional Test for parameter 'sample_only_at_l_star' \n")
    # values to be tested
    sample_only_at_l_star_fail_list = ['x',1.0,-1,0,None]
    sample_only_at_l_star_success_list = [False, True]

    # should fail
    [run_one_functional_test(sample_only_at_l_star=sample_only_at_l_star_fail_list[i], should_fail=True) for i in
     range(len(sample_only_at_l_star_fail_list))]
    # should pass
    [run_one_functional_test(sample_only_at_l_star=sample_only_at_l_star_success_list[i], should_fail=False) for i in
     range(len(sample_only_at_l_star_success_list))]

    display_local_status()


def run_max_log_evidence_ratio_drop_tests():

    # max_log_evidence_ratio_drop
    print("Running Functional Test for parameter 'max_log_evidence_ratio_drop' \n")
    # values to be tested
    max_log_evidence_ratio_drop_fail_list = ['x',-1,0,None,0]
    max_log_evidence_ratio_drop_success_list = [0.1, 1,2,3,10,100,100.0,1000]

    # should fail
    [run_one_functional_test(max_log_evidence_ratio_drop=max_log_evidence_ratio_drop_fail_list[i], should_fail=True)
     for i in range(len(max_log_evidence_ratio_drop_fail_list))]
    # should pass
    [run_one_functional_test(max_log_evidence_ratio_drop=max_log_evidence_ratio_drop_success_list[i], should_fail=False)
     for i in range(len(max_log_evidence_ratio_drop_success_list))]

    display_local_status()


def run_all_functional_tests():
    # 1
    run_grid_tests()
    # 2
    run_grid_spacing_tests()
    # 3
    run_bound_box_tests()
    # 4
    run_num_grid_points_tests()
    # 5
    run_alpha_tests()
    # 6
    run_periodic_tests()
    # 7
    run_evaluation_method_for_Z_tests()
    # 8
    run_num_samples_for_Z_test()
    # 9
    run_tolerance_tests()
    # 10
    run_resolution_tests()
    # 11
    run_seed_tests()
    # 12
    run_print_t_tests()
    # 13
    run_num_posterior_samples_tests()
    # 14
    run_sample_only_at_l_star_tests()
    # 15
    run_max_log_evidence_ratio_drop_tests()

    display_global_status()

run_all_functional_tests()
