from __future__ import print_function, absolute_import
# module contains all authorisation related functions

from pydrive.auth import GoogleAuth
import sys
import os

# set directory for relativistic import
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import file_add
except ImportError:
    from . import file_add

    
def drive_auth(reset):
    """
    asks for authentication to generate access token or uses existing access token
    Args:
        reset (bool): True for resetting linked account, bypasses existing access token.
    Returns:
        Google_Auth with permissions
    """
    g_auth = GoogleAuth()

    # setting Google Auth for custom parameters
    g_auth.DEFAULT_SETTINGS['client_config_file'] = file_add.client_secrets
    g_auth.DEFAULT_SETTINGS['client_config_backend'] = 'file'
    g_auth.DEFAULT_SETTINGS['oauth_scope'] = ['https://www.googleapis.com/auth/drive']
    g_auth.DEFAULT_SETTINGS['get_refresh_token'] = True
    g_auth.DEFAULT_SETTINGS['save_credentials'] = True
    g_auth.DEFAULT_SETTINGS['save_credentials_backend'] = 'file'
    g_auth.DEFAULT_SETTINGS['save_credentials_file'] = file_add.cred_file()
    g_auth.DEFAULT_SETTINGS['client_id'] = '442675981331-9sq75sq0731sc0pef1rsg2jksmqfov2f.apps.googleusercontent.com'
    g_auth.DEFAULT_SETTINGS['client_secret'] = 'bmPz_4djxl_NZsA4Cvvaz2XT'

    # if already authenticated, load file
    g_auth.LoadCredentialsFile(file_add.cred_file())

    if g_auth.credentials is None or reset:
        if reset:
            if g_auth.credentials is not None:
                print("Error: Couldn't reset account. Please report at thealphadollar@iitkgp.ac.in")
                sys.exit(1)
        g_auth.LocalWebserverAuth()

    elif g_auth.access_token_expired:
        # refresh authorisation if expired
        g_auth.Refresh()

    else:
        # initialise the saved data
        g_auth.Authorize()

    return g_auth


def reset_account():
    """
    change linked account
    Args:
        None
    Returns:
        None
    """
    if os.path.isfile(file_add.cred_file()):
        os.remove(file_add.cred_file())

    drive_auth(True)
    
 
if __name__ == '__main__':
    pass
