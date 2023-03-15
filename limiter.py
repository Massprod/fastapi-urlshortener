from slowapi import Limiter
from slowapi.util import get_remote_address

req_limiter = Limiter(key_func=get_remote_address)
random_limit = "15/minute"
custom_limit = "15/minute"
delete_limit = "10/minute"
register_limit = "10/minute"
