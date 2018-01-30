

class DeploymentItem(object):
    
    # Required fields
    name = None
    version = None
    platform = None
    destination = None

    # Optional fields
    link = True
    unpack = True
    keep_updated = False

class DeploymentParser(object):
    def parse(uri):
        raise TypeError("Not implemented")
