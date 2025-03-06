import re
from pydub import utils

# Fix invalid escape sequences in regex patterns
def patch_pydub():
    # Fix the regex patterns
    utils._fd_or_path_or_tempfile = re.compile(r'([su]([0-9]{1,2})p?) \(([0-9]{1,2}) bit\)$')
    utils._fd_or_path_or_tempfile2 = re.compile(r'([su]([0-9]{1,2})p?)( \(default\))?$')
    utils._flt_pattern = re.compile(r'(flt)p?( \(default\))?$')
    utils._dbl_pattern = re.compile(r'(dbl)p?( \(default\))?$')

# Apply the patch when imported
patch_pydub() 