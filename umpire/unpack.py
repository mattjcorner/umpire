"""unpack.py"""

HELPTEXT = """
                  ----- Unpack Module -----

The unpack module unpacks a tar gz file.

Usage: Currently N/A

"""

import sys, os
from maestro.core import module

HELP_KEYS = ["h", "help"]

class UnpackModule(module.AsyncModule):
    # Required ID of this module
    id = "unpack"
    file_path = None
    destination_path = None
    delete_archive = False

    def help(self):
        print self.help_text
        exit(0)

    def run(self,kwargs):
        import tarfile
        with tarfile.open(self.file_path, "r:gz") as f:
            f.extractall(self.destination_path)
        if self.delete_archive is True:
            os.remove(self.file_path)

