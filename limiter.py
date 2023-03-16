from slowapi import Limiter
from slowapi.util import get_remote_address

req_limiter = Limiter(key_func=get_remote_address)
random_limit = "120/minute"
custom_limit = "150/minute"
delete_limit = "100/minute"
register_limit = "85/minute"
