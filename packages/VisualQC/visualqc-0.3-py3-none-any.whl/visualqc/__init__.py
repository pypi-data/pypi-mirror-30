# -*- coding: utf-8 -*-

"""Top-level package for visualqc."""

__all__ = ['vqc', 'run_workflow', 'review_and_rate', 'outlier_advisory']

__author__ = """Pradeep Reddy Raamana"""
__email__ = 'raamana@gmail.com'
__version__ = '0.1.0'

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


from visualqc import vqc
from visualqc.vqc import run_workflow
from visualqc.viz import review_and_rate
from visualqc.readers import gather_freesurfer_data, read_aparc_stats_in_hemi, read_aseg_stats, read_aparc_stats_wholebrain
from visualqc.outliers import outlier_advisory
