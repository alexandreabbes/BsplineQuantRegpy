# Quantile Regression with Constrained Splines

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/BsplineQuantRegpy.svg)](https://badge.fury.io/py/BsplineQuantRegpy)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17427913.svg)](https://doi.org/10.5281/zenodo.17427913)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Documentation](https://img.shields.io/badge/docs-fr-blue.svg)](https://bsplinequantregpy.readthedocs.io/fr/latest/)
[![Documentation EN](https://img.shields.io/badge/docs-en-blue.svg)](https://bsplinequantregpy.readthedocs.io/en/latest/)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![R](https://img.shields.io/badge/R-4.0+-blue.svg)](https://www.r-project.org/)


Python implementation of quantile regression with constrained splines (degrees 1-4). Degrees 1-3 are based on the article **"Quantile regression with cubic splines under shape constraints"** by Alexandre Abbes, while degree 4 is a natural consequence of the cited references.



## Associated packages

| Package | Langage | Description | Lien |
|---------|---------|-------------|------|
| **BsplineQuantReg** | R | Splines cubiques contraintes, self-contained | [CRAN](https://cran.r-project.org/package=BsplineQuantReg) |
| **cobs** | R | Constrained B-Splines (linéaires et quadratiques) | [CRAN](https://cran.r-project.org/package=cobs) |
| **quantreg** | R | Quantile Regression | [CRAN](https://cran.r-project.org/package=quantreg) |
| **quantreg** | Python | Quantile Regression | [statmodels](https://www.statsmodels.org) or [PyPI](https://pypi.org/project/statsmodels) |
| **Ce package** | Python | Splines de degrés 1 à 4 contraintes | [GitHub](https://github.com/alexandreabbes/BsplineQuantRegpy) |

### Comparison of packages

| Fonctionnality| cobs (R) | BsplineQuantReg (R) | BsplineQuantRegpy (Python) |
|---------------|----------|---------------------|---------------------|
| Linear Splines  | ✅ | ❌ | ✅ |
| Quadratic Splines | ✅ | ❌ | ✅ |
| Cubic Splines | ❌ | ✅ | ✅ |
| Quartic Splines | ❌ | ❌ | ✅ |
| Contraints at knots | ✅ | ✅ | ✅ |
| Over the whole interval | ❌ | ✅ | ✅ |
| Region constraints | ❌ | ✅ | ✅ |
| Third derivative| ❌ | ❌ | ✅ |
| Gui | ❌ | ❌ | ✅ |
| Self-contained for Bsplines| ❌ | ✅ | ❌ (utilise SciPy) |



```

## Features

-  Quantile regression with splines of degree 1 to 4
-  Constraints on derivatives (monotonicity, convexity, third derivative)
-  Constraints valid over the entire interval or selected regions
-  Graphical interface for interactive testing (Tkinter)
-  Multiple solvers support (CLARABEL, ECOS, SCS, MOSEK)

##  Installation

### Python

```bash
# From PyPI
pip install BsplineQuantRegpy

# Or from source
git clone https://github.com/alexandreabbes/BsplineQuantRegpy.git
cd BsplineQuantRegpy
pip install -e .
```

### R

```r
# From CRAN
install.packages("BsplineQuantReg")
```

## Links

- **Python Repository**: [https://github.com/alexandreabbes/BsplineQuantRegpy](https://github.com/alexandreabbes/BsplineQuantRegpy)
- **R Repository**: [https://github.com/alexandreabbes/BsplineQuantReg](https://github.com/alexandreabbes/BsplineQuantReg)
- **R CRAN Package**: [https://cran.r-project.org/package=BsplineQuantReg](https://cran.r-project.org/package=BsplineQuantReg)
- **DOI**: [10.5281/zenodo.17427913](https://doi.org/10.5281/zenodo.17427913)

## File Structure

### Graphical Interface
- `Quant_reg_tk.py` - Tkinter GUI for interactive parameter testing (spline degree, knots, derivative constraints)

### Main Algorithms

| File | Description |
|------|-------------|
| `SplineCubicQuant.py` | Cubic splines with constraints on 1st, 2nd, and 3rd derivatives |
| `SplineQuarticQuant.py` | Quartic splines with exact constraints over the entire interval |
| `SplineQuadraticQuant.py` | Quadratic splines with constraints on 1st and 2nd derivatives |
| `SplineLinearQuant.py` | Linear splines with constraints on 1st derivative '
| `quantile_spline.py` | Unified function for regresion with any degree 1-4 and constraints|

### Examples and Data
- `example_temerature.py` - Replication of the test on global warming (temperatures , data in `temp.xls`)
- `examples/` - Additional usage examples

## Quick Start

```python
from BsplineQuanRegpy import SplineCubicQuantile
import numpy as np
Quickstart
Quickstart2

Or launch the GUI:

```python
from splinequantreg import run_gui
run_gui()
```


## Prerequisites

### Python
```bash
pip install numpy scipy pandas matplotlib cvxpy
```
``


## Citation

If you use this code in your research, please cite:

```bibtex
@article{abbes2025quantile,
  title={Quantile regression with cubic polynomial splines under shape constraints with applications},
  author={Abbes, Alexandre},
  year={2025},
  doi={10.5281/zenodo.17427913}
}


## Contributions

Contributions are welcome! Feel free to:

- Open an [issue](https://github.com/alexandreabbes/BsplineQuantRegpy/issues)
- Submit a [pull request](https://github.com/alexandreabbes/BsplineQuantRegpy/pulls)
- Suggest improvements

## License

This project is licensed under the GPL-v3 License - see the [LICENSE](LICENSE) file for details.

## AI Assistance

This project was carried out with the assistance of **DeepSeek** ([https://deepseek.com/](https://deepseek.com/)), which helped the developer with:
- Implementing constrained spline algorithms from MATLAB to Python
- Translating mathematical concepts into Python code
- Structuring programs and documentation

DeepSeek is a language model developed by 深度求索 [1].

[1] DeepSeek-AI. (2024). DeepSeek-V3 Technical Report. arXiv:2412.19437.

## References

- Abbes, A. (2025). Quantile regression with cubic polynomial splines
under shape constraints with applications. doi:10.5281/zenodo.17427913
- He, X., & Shi, P. (1998). Monotone B-spline smoothing. *Journal of the American Statistical Association*, 93(442), 643-650.
- Karlin, S., & Studden, W.J. (1966). *Tchebycheff Systems: With Applications in Analysis and Statistics*. Interscience Publishers.
- Papp, D., & Alizadeh, F. (2014). Shape-Constrained Estimation Using Nonnegative Splines. *Journal of Computational and Graphical Statistics*, 23(1), 211-231.


## Contact

**Author**: Alexandre Abbes
**Email**: alexandre.abbes@proton.me
**GitHub**: [alexandreabbes](https://github.com/alexandreabbes)
