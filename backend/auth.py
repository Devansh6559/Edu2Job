# from flask import request, jsonify, current_app
# import requests
# from models import User, db
# import jwt
# from functools import wraps
# from google.oauth2 import id_token
# from google.auth.transport import requests as google_requests

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
        
#         if 'Authorization' in request.headers:
#             auth_header = request.headers['Authorization']
#             try:
#                 token = auth_header.split(' ')[1]
#             except IndexError:
#                 return jsonify({'message': 'Token is missing!'}), 401
        
#         if not token:
#             return jsonify({'message': 'Token is missing!'}), 401
        
#         try:
#             data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
#             current_user = User.query.get(data['user_id'])
#         except:
#             return jsonify({'message': 'Token is invalid!'}), 401
        
#         return f(current_user, *args, **kwargs)
    
#     return decorated

# from google.oauth2 import id_token
# from google.auth.transport import requests

# GOOGLE_CLIENT_ID = "1019789869790-24jf1rlv594hm407c1lgfjdrr8o9m5g8.apps.googleusercontent.com"

# def verify_google_token(token):
#     try:
#         idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

#         # idinfo contains:
#         # email, name, picture, sub (Google user ID)
#         return {
#             "email": idinfo["email"],
#             "name": idinfo.get("name", "Google User"),
#             "picture": idinfo.get("picture")
#         }

#     except Exception as e:
#         print("Google token verification error:", e)
#         return None
from flask import request, jsonify, current_app
import requests
from models import User, db
import jwt
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'message': 'Token is missing!'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

from google.oauth2 import id_token
from google.auth.transport import requests

GOOGLE_CLIENT_ID = "1019789869790-24jf1rlv594hm407c1lgfjdrr8o9m5g8.apps.googleusercontent.com"

def verify_google_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        return {
            "email": idinfo["email"],
            "name": idinfo.get("name", "Google User"),
            "picture": idinfo.get("picture")
        }
    except Exception as e:
        print("Google token verification error:", e)
        return None
