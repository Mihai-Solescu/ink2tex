"""
Runtime hook to fix NumPy CPU dispatcher conflicts in PyInstaller
This prevents the "CPU dispatcher tracer already initialized" error
"""

import os

# Set environment variables to prevent NumPy CPU dispatcher conflicts
# This must be done before numpy is imported anywhere
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1' 
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

# Additional environment variables to prevent CPU dispatcher conflicts
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['NPY_NUM_BUILD_JOBS'] = '1'
