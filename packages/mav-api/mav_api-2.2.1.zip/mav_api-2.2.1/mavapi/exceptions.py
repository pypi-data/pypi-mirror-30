class MAVAPIExceptions(Exception):
    pass

class MAVAPIError(MAVAPIExceptions):

    WRONG_ACCESSTOKEN = {'status': 'error', 'error_code': 4, 'error_msg': 'Wrong access_token.'}
    NO_ACCESSTOKEN = {'status': 'error', 'error_code': 3, 'error_msg': "Token isn't specified."}
    AUTH_IP_DENIED = {'status': 'error', 'error_code': 47, 'error_msg': "You cannot use this access_token from this IP address."}
    DATE_WRONG_FORMAT = {'status': 'error', 'error_code': 12, 'error_msg': 'Date in wrong format.'}

    error_list = {3:NO_ACCESSTOKEN,4:WRONG_ACCESSTOKEN,12:DATE_WRONG_FORMAT,47:AUTH_IP_DENIED}