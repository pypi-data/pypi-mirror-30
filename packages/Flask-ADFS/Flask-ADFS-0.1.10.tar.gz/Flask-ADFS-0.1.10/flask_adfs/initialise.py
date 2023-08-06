import textwrap
import requests
import xmltodict
# from cryptography.x509 import load_pem_x509_certificate
# from cryptography.hazmat.backends import default_backend
from flask_login import LoginManager
from flask import  g

_public_key = None
_public_key_x = None
login_mgr = LoginManager()
adfs_access = {}


def pk(swapped=False):
    if swapped:
        return _public_key_x
    else:
        return _public_key

def pk_swap():
    if _public_key_x:
        return True
    return False

def adfs_init(app):
    global _public_key
    global _public_key_x
    global login_mgr
    login_mgr.init_app(app)
    login_mgr.session_protection = "strong"
    with app.app_context():
        _get_certs_from_adfs(app)

    # try:
    #     with open('{0}'.format(app.config.get('ADFS_CERT_LOCATION'))) as cert:
    #         cert_str = cert.read()
    #         cert_str = cert_str.encode()
    #     # extract public key
    #     cert_obj = load_pem_x509_certificate(cert_str, default_backend())
    #     _public_key_x = cert_obj.public_key()
    #     app.logger.debug('ADFS second public key cached')
    # except:
    #     app.logger.error('Could not get second ADFS public key')



def set_access(access):
    global adfs_access
    adfs_access = access


def get_access():
    global adfs_access
    return adfs_access

def _get_certs_from_adfs(app, retry=False):
    global _public_key
    global _public_key_x
    """Used by verify_token to connect to adfs metadata and retrieve new certificates"""
    g.trace_id = "johnp"
    app.logger.info('getting certificates from adfs')

    # clear old certs for ease of debugging
    _public_key = None
    _public_key_x = None
    try:
        res = requests.get('{}/federationMetadata/2007-06/federationmetadata.xml'.format(app.config.get("ADFS_URL")))
    except Exception:
        if not retry:
            app.logger.warning('failed to connect to adfs, retrying')
            _get_certs_from_adfs(app, retry=True)
            return
        else:
            app.logger.warning('failed to connect to adfs, no certificates available')
            return # TODO should do something better here
    adfs_meta_dict = xmltodict.parse(res.text)
    certs = adfs_meta_dict['EntityDescriptor']['RoleDescriptor'][1]['KeyDescriptor']
    # if there is only one cert then the cert variable will be a dict
    if isinstance(certs,dict):
        _public_key = _reformat_adfs_cert(certs['KeyInfo']['X509Data']['X509Certificate'])
    # if there are 2 certs then the cert variable will be a list
    elif isinstance(certs,list):
        _public_key_x = _reformat_adfs_cert(certs[0]['KeyInfo']['X509Data']['X509Certificate'])
        _public_key = _reformat_adfs_cert(certs[1]['KeyInfo']['X509Data']['X509Certificate'])

    
    if _public_key:
        app.logger.info('adfs primary cert retrieved from adfs')
        # app.logger.info(_public_key)
    else:
        app.logger.info('unable to retrieve primary cert from adfs')

    app.logger.info('adfs additional cert:')
    if _public_key_x:
        app.logger.info('adfs additional cert retrieved from adfs')
        # app.logger.info(_public_key_x)
    else:
        app.logger.info('no additional cert available from adfs')

def _reformat_adfs_cert(cert_string):
    """Used by verify_token to convert x509 certificates from adfs metadata into a usable format"""
    split = textwrap.fill(cert_string, 64)
    cert_str = "-----BEGIN CERTIFICATE-----\n{}\n-----END CERTIFICATE-----".format(split)
    return cert_str
    # cert_obj = load_pem_x509_certificate(cert_str.encode(), default_backend())
    # return cert_obj.public_key()

