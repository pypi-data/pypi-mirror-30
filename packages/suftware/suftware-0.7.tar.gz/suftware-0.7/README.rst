SUFTware (Statistics Using Field Theory) provides fast and lightweight Python implementations of Bayesian Field Theory algorithms for low-dimensional statistical inference. SUFTware currently supports the one-dimenstional density estimation algorithm DEFT, described in [1], [2], and [3]. The image on the right shows DEFT applied to alcohol consumption data from the World Health Organization. This computation takes about 0.25 seconds on a standard laptop computer. Code for this and other examples can be found on the Examples page. See the Documentation page for details on the SUFTware API.

Currently, SUFTware supports a one-dimensional density estimation called DEFT. DEFT has substantial advantages over standard density estimation methods, including, including kernel density estimation and Dirichlet process mixture modeling. See [Chen et al., 2018; Kinney 2015; Kinney 2014].

Installation
pip install suftware
Requirements

Python >= 3.6.2
or Python = 2.7.10
numpy >= 1.13.3
scipy >= 1.0.0
matplotlib >= 2.1.0

Documentation: "http://suftware.readthedocs.org"
Github: "https://github.com/jbkinney/suftware"