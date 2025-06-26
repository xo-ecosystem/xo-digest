import warnings

from urllib3.exceptions import NotOpenSSLWarning


def patch_urllib3_warning():
    warnings.filterwarnings("ignore", category=NotOpenSSLWarning)
