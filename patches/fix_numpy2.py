import numpy as np

# Patch removed types in numpy 2.0
if not hasattr(np, "float_"):
    np.float_ = np.float64

if not hasattr(np, "int_"):
    np.int_ = np.int64

if not hasattr(np, "uint"):
    np.uint = np.uint64
