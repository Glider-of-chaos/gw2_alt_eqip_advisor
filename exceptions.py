class Error(Exception):
    """Base class for local exceptions"""
    pass

class ApiConnectionError(Error):
    """Exceptions raised in case connection to api did not work out

    Attributes:
        request_url -- request url that did not get proper resopnse
        response_code -- response code
    """

    def __init__(self, request_url, response_code):
        self.request_url = request_url
        self.response_code = response_code

class NoSuchItemError(Error):
    """Raised when API returned no such item response
    
    Attributes:
        item_id -- id of an item that was not recognized by API
    """

    def __init__(self):
        pass
        
