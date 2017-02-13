from __future__ import print_function
import sys,os,argparse
from maestro.aws import s3
from maestro.tools import path
from snapp.execute import ModuleExecuter 

version="0.6.0"

###
# Internal Modules
###
from umpire import fetch, unpack, deploy

# Default Config
from umpire import config

# Actions
from umpire import action

# Helpers
from umpire import get_umpire_cache_root

###
# Command line args
#    Add actions under action.py
###
parser = argparse.ArgumentParser(description="""
Umpire reads a properly formatted JSON deployment file to deploy files.
Examples can be found on GitHub: https://github.com/Signiant/umpire
""")

parser.add_argument("-c", "--clear-cache", action=action.ClearCache,
        nargs=0,
        help="Clears the default cache. Set UMPIRE_CACHE_LOCATION to override."
        )

parser.add_argument("-r", "--repair-cache", action=action.RepairLockFiles,
        nargs=0,
        help="Clears the default cache of lockfiles. Set UMPIRE_CACHE_LOCATION to override.")

parser.add_argument("--debug",
        nargs=0,
        action="store_true",
        default=False)
        help="Enables debug mode, which will print tracebacks for most errors.")

parser.add_argument("--version", action="version", version=version)

parser.add_argument("deployment_file")

#Entry point for Umpire
def entry():
    exit_code = Umpire().exit_code
    sys.exit(exit_code)

class Umpire(ModuleExecuter):

    def run(self, context):
        kwargs = parser.parse_args()
        #Get the instance of our first module
        deployer = deploy.DeployModule()

        deployer.cache_root = get_umpire_cache_root()
        deployer.deployment_file = kwargs.deployment_file 
        deployer.DEBUG = kwargs.debug

        print str(kwargs)
        sys.exit(0)
        self.exit_code = deployer.run(context)

