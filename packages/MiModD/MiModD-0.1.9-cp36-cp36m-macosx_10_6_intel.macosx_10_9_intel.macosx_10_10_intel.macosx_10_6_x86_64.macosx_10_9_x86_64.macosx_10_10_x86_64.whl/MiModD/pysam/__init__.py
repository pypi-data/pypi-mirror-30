import sys
import os

from .exceptions import *
from .csamtools import *
from . import csamtools
from . import Pileup
from .version import __version__, __samtools_version__


#
# samtools command line options to export in python
#
# import is a python reserved word.
SAMTOOLS_DISPATCH = { 
    # samtools 'documented' commands
    "view" : ( "view", None ),
    "sort" : ( "sort", None),
    "mpileup" : ( "mpileup", None),
    "depth" : ("depth", None),
    "faidx" : ("faidx", None),
    "tview" : ("tview", None),
    "index" : ("index", None),
    "idxstats" : ("idxstats", None),
    "fixmate" : ("fixmate", None),
    "flagstat" : ("flagstat", None),
    "calmd" : ("calmd", None),
    "merge" : ("merge", None),  
    "rmdup" : ("rmdup", None),
    "reheader" : ("reheader", None),
    "cat" : ("cat", None),
    "targetcut" : ("targetcut", None),
    "phase" : ("phase", None),
    # others
    "samimport": ( "import", None),
    "bam2fq" : ("bam2fq", None),
    "pad2unpad" : ("pad2unpad", None),
    "depad" : ("pad2unpad", None),
    "bedcov" : ("bedcov", None),
    "bamshuf" : ("bamshuf", None),
    # obsolete
    # "pileup" : ( "pileup", ( (("-c",), Pileup.iterate ), ), ),

 }

# instantiate samtools commands as python functions
for key, options in SAMTOOLS_DISPATCH.items():
    cmd, parser = options
    globals()[key] = SamtoolsDispatcher(cmd, parser)

# hack to export all the symbols from csamtools
__all__ = \
    csamtools.__all__ + \
    [ "SamtoolsError", "SamtoolsDispatcher" ] + list(SAMTOOLS_DISPATCH) +\
    ["Pileup" ] 


###########################################################
# Utility functions for compilation
def get_include():
    '''return a list of include directories.'''
    dirname = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    return [ dirname,
             os.path.join(dirname, 'include', 'samtools') ]

def get_defines():
    '''return a list of defined compilation parameters.'''
    return [('_FILE_OFFSET_BITS','64'), ('_USE_KNETFILE','')]
