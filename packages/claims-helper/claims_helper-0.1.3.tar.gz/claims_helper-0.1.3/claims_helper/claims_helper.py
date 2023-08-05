import base64
import json
from flask import Blueprint, jsonify, request

def base64_decode(encoded_str):
    # Add paddings manually if necessary.
    num_missed_paddings = 4 - len(encoded_str) % 4
    if num_missed_paddings != 4:
        encoded_str += b'=' * num_missed_paddings
    return base64.b64decode(encoded_str).decode('utf-8')

def base64_encode(plain_str):
    return base64.b64encode(plain_str.encode('utf-8'))

class ClaimsHelper:
    def __init__(self, request):
        """User info is the complete header parameter value as generated by the ESP endpoint"""
        claims = request.headers.get('Claims', None)

        if claims:
            self.claims = json.loads(base64_decode(claims))
            print 'Recevied claims: ', self.claims
        else:
            self.claims = None
            
    def get_user_id(self):
        if self.claims is not None and 'user_id' in self.claims:
            return self.claims['user_id']
        else:
            return None

    def is_admin(self, scheme_id=None):
        """Returns true if the claims contain an admin role for the specified scheme"""
        if self.claims is None or 'roles' not in self.claims:
            return False

        for role in self.claims['roles']:
            if role['role'] == 'admin':
                # Checks if user has a global admin role (ie, scheme_id is None or not specified)
                if 'scheme_id' not in role or role['scheme_id'] is None:
                    return True

                if role['scheme_id'] == scheme_id:
                    return True
        
        return False

def create_claims_header(user_id, roles):
    """ Creates a header with custom claims - useful to simulate what will come from FB calls 
        roles is an array of dictionaries with the following values:
        role: string - name of the role. Requried
        scheme_id: integer - scheme_id. Can be missing, or None
    """
    if user_id is None:
        raise Exception('user_id cannot be None!')

    if type(roles) is not list:
        raise Exception('Expecting roles to be a list of roles. Hint: the type is actually {}'.format(type(roles)) )

    claims = {'user_id': user_id}

    if roles is not None:
        claims['roles'] = list(roles)

    header = {'Claims': base64_encode(json.dumps(claims))}

    return header