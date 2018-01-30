import json
from umpire.parser import DeploymentParser, DeploymentItem

class JSONDeploymentParser(DeploymentParser):
    def parse(uri):
        try:
            with open(uri):
                data = json.load
        except TypeError:
            pass
        except IOError as e:
            if not self.DEBUG:
                print("Unable to locate file: " + str(self.uri))
            else:
                raise e
            sys.exit(1)

        # Attempt to parse into Deployment Item here
        pass
