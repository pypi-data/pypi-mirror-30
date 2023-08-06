from st_library.utils.api_client import resource
from st_library.utils.api_client import request


class ApiClient(object):
    def __init__(self):
        raise TypeError('This class should not be initialized')

    res = resource
    get = request.get
    post = request.post
    delete = request.delete
