from flask_login import UserMixin
from flask import current_app as app
#import jwt
from jose import jwt, JWTError
from .initialise import pk, pk_swap
from flask_adfs.initialise import  get_access


class User(UserMixin):  # pragma: no cover
    roles = []
    authenticated = False
    roles_str = ''
    pk_swapped = False


    def __init__(self, access_token=None):
        # encode certificate as bytes
        try:
            token_data = self.decode_token(access_token)
            # 10 second leeway to ignore the timing error due to out of sync clocks with adfs servers
        
        except JWTError as e:
        #except jwt.exceptions.DecodeError as e:
            app.logger.error("failed to initiate user. error: " + repr(e))
            try:
                self.pk_swapped = pk_swap()
                if self.pk_swapped: 
                    app.logger.info("swapped to new ADFS certificate")               
                    token_data = self.decode_token(access_token)
                else:    
                    raise e
            except Exception as e:
                app.logger.error("failed to initiate userwith alternative cert error: " + repr(e))
                self.authenticated = False 
                return                        
        except Exception as e:
                app.logger.error("failed to initiate user. error: " + repr(e))
                self.authenticated = False
                return
        self.access_token = access_token

        tempRoles = []
        roles = []
        try:
            self.racf_id = token_data["UserName"].upper()
            # token_data["group"] is the following:
            # ['CN=GUIDE_DEV_Editor,OU=Guide,OU=Central Groups,DC=diti,DC=lr,DC=net',
            #  'CN=GUIDE_DEV_Author,OU=Guide,OU=Central Groups,DC=diti,DC=lr,DC=net'],
            # the section 'CN=GUIDE_DEV_' will need to be split off, as well as the extra data
            roleData = token_data.get("group", [])
            # ADFS will only return a list if user is in more than one group
            if isinstance(roleData, list):
                for i in range(0, len(roleData)):
                    tempData = roleData[i].split(',')
                    tempRoles.append(tempData[0])
            else:
                tempData = roleData.split(',')
                tempRoles.append(tempData[0])

            roles.append("Viewer") # everyone gets this just by being authenticated
            for i in tempRoles:
                tempData = i.split('_')
                roles.append(tempData[len(tempData)-1])

            self.roles = set(roles)
            roles = list(self.roles)
            roles.sort()
            self.roles_str = 'Roles\n=====\n{0}'.format('\n'.join(roles))
            self.token_data = token_data
            self.authenticated = True
        except:
            app.logger.error("failed to parse user token id={0}".format(id))
            self.authenticated = False

    def decode_token(self, access_token):
        return jwt.decode(access_token, 
                        pk(self.pk_swapped), 
                        algorithms='RS256',
                        audience=app.config.get('ADFS_LOGIN_URL'), 
                        options={'leeway':10}
                        )



    @property
    def is_authenticated(self):
        return self.authenticated

    @property
    def is_active(self):
        return self.authenticated

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        # return self.access_token
        return self.racf_id

    def get_racf_id(self):
        return self.racf_id

    def get_token_data(self):
        return self.token_data

    def get_roles(self):
        return self.roles

    def get_permissions(self,channel):
        perms = get_access().setdefault(channel,{})
        permissions = []
        for perm, roles in perms.items():
            if not roles.isdisjoint(self.roles):
                permissions.append(perm)
        return permissions 
