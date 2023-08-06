

class ClientResponse(object):

    def __init__(self, data=None, success=False, error=None):

        self.data = data
        self.error = error
        self.success = success
