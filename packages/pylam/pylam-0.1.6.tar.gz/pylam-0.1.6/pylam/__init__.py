# -*- coding: utf-8 -*-
"""
This package contains object classes and functions to work with LAMMPS files within Python.

"""

__license__   = "MIT"
__docformat__ = 'reStructuredText'
from .version import __version__


from ._block import (DataBlock, ThermoBlock, FixBlock)
from ._datafile import (SimpleDataFile, FixBlockFile, LogFile)
from ._lmpdatafile import (LammpsDataFile, LammpsDataHeader, LammpsDataMasses, LammpsDataCoeffs, LammpsDataAtoms,
                           LammpsDataVelocities, LammpsDataAtomTemplate, LammpsDataCoeffsSection, LammpsDataAtomAtomic)


__all__ = ( 'SimpleDataFile', 'FixBlockFile', 'LogFile',
            'ThermoBlock','DataBlock', 'FixBlock',
            'LammpsDataFile', 'LammpsDataHeader', 'LammpsDataMasses', 'LammpsDataCoeffs', 'LammpsDataAtoms',
            'LammpsDataVelocities', 'LammpsDataAtomTemplate', 'LammpsDataCoeffsSection', 'LammpsDataAtomAtomic')
