"""
repo.py contains code to control the local cache for umpire. It is not a module.
"""

import os, shutil, time
import ConfigParser
import maestro.tools.path
import maestro.internal.module
from urlparse import urlparse
from unpack import UnpackModule

CONFIG_FILENAME = ".umpire"
CONFIG_REPO_SECTION_NAME = "umpire"
CONFIG_ENTRY_SECTION_NAME = "entry"

CURRENT_ENTRY_CONFIG_VERSION = "0.1"
CURRENT_REPO_CONFIG_VERSION = "0.1"

def create_local_cache(local_path, remote_url):
    """
    Creates a cache and returns a LocalCache object. NOT THREAD-SAFE.
    """
    cache_config = os.path.join(local_path, CONFIG_FILENAME)
    if os.path.exists(cache_config):
        raise CacheError("A cache already exists in the specified location: " + local_path)

    try:
        os.makedirs(local_path)
    except OSError as e:
        pass #Directories exist

    ## Start creating config
    config = ConfigParser.SafeConfigParser()
    config.add_section(CONFIG_REPO_SECTION_NAME)

    config.set(CONFIG_REPO_SECTION_NAME, "remote_url", remote_url)
    config.set(CONFIG_REPO_SECTION_NAME, "config_version", CURRENT_REPO_CONFIG_VERSION)

    with open(cache_config, "w+") as f:
        config.write(f)

    return LocalCache(local_path)
 
def read_entry(file_location):
    if not os.path.exists(file_location):
        raise EntryError("Unable to find entry file under: " + file_location)

    #Get parser
    parser = ConfigParser.SafeConfigParser()
    try:#Read
        config = parser.read(file_location)
    except ConfigParser.ParsingError:
        raise EntryError("Error parsing the entry configuration file: " + file_location + " Please contact an administrator for help fixing this problem.")

    #Verify the config has been read 
    if config is None:
        raise EntryError("The config file: " + file_location + " appears to be empty. Please verify this is the location of a valid umpire cache entry.")

    #Verify the section we're looking for is there 
    if CONFIG_ENTRY_SECTION_NAME not in parser.sections():
        raise EntryError("The config file " + file_location + " appears to be missing the [umpire] section. Please verify this is the location of a valid umpire cache entry, or delete the containing folder and try again.")

    entry = EntryInfo()

    #Set file location
    entry.path = os.path.split(file_location)[0]

    #Attempt to parse the md5
    try:
        entry.md5 = parser.get(CONFIG_ENTRY_SECTION_NAME, "md5")
    except ConfigParser.Error:
        pass #TODO: Future
    if not entry.md5:
        pass #TODO: Future
    
    #Attempt to parse the entry product name
    try:
        entry.name = parser.get(CONFIG_ENTRY_SECTION_NAME, "name")
    except ConfigParser.Error:
        raise EntryError("Unable to parse name from entry file: " + file_location)
    if not entry.name:
        raise EntryError("Unable to parse name from entry file: " + file_location)
    
    #Attempt to parse the entry platform name
    try:
        entry.platform = parser.get(CONFIG_ENTRY_SECTION_NAME, "platform")
    except ConfigParser.Error:
        raise EntryError("Unable to parse platform from entry file: " + file_location)
    if not entry.name:
        raise EntryError("Unable to parse platform from entry file: " + file_location)

    #Attempt to parse the entry version 
    try:
        entry.version = parser.get(CONFIG_ENTRY_SECTION_NAME, "version")
    except ConfigParser.Error:
        raise EntryError("Unable to parse version from entry file: " + file_location)
    if not entry.name:
        raise EntryError("Unable to parse version from entry file: " + file_location)
    
    #Attempt to parse the entry config version 
    try:
        entry.config_version = parser.get(CONFIG_ENTRY_SECTION_NAME, "config_version")
    except ConfigParser.Error:
        raise EntryError("Unable to parse config_version from entry file: " + file_location)
    if not entry.config_version:
        raise EntryError("Unable to parse config_version from entry file: " + file_location)

    return entry

def write_entry(entry):

        ## Start creating config
        config = ConfigParser.SafeConfigParser()
        config_path = os.path.join(entry.path, CONFIG_FILENAME)
        config.add_section(CONFIG_ENTRY_SECTION_NAME)

        config.set(CONFIG_ENTRY_SECTION_NAME, "name", entry.name)
        config.set(CONFIG_ENTRY_SECTION_NAME, "platform", entry.platform)
        config.set(CONFIG_ENTRY_SECTION_NAME, "version", entry.version)
        config.set(CONFIG_ENTRY_SECTION_NAME, "config_version", CURRENT_ENTRY_CONFIG_VERSION)

        with open(os.path.join(entry.path, CONFIG_FILENAME), "w+") as f:
            return config.write(f)

class EntryInfo(object):
    config_version = None
    md5 = None
    name = None
    path = None
    platform = None
    version = None

    def lock(self):
        pass
    def unlock(self):
        pass

class EntryError(Exception):
    pass

class EntryLockError(Exception):
    pass

class CacheError(Exception):
    pass

class LocalCache(object):
    local_path = None
    settings_file = None
    remote_url = None
    config_version = None

    #Verifies local existance
    def __init__(self, cache_root):
        if not os.path.exists(cache_root):
            raise CacheError("The path '" + str(cache_root) + "' does not contain a valid umpire cache.")
        
        self.local_path = cache_root

        self.settings_file = os.path.join(cache_root,CONFIG_FILENAME)

        if not os.path.exists(self.settings_file):
            raise CacheError("The specified path does not appear to be a valid umpire cache")
        config = None
        
        #Get parser
        parser = ConfigParser.SafeConfigParser()
        try:#Read
            config = parser.read(self.settings_file)
        except ConfigParser.ParsingError:
            raise CacheError("Error parsing the cache configuration file. Please contact an administrator for help fixing this problem.")

        #Verify the config has been read 
        if config is None:
            raise CacheError("The config file appears to be empty. Please verify this is the location of a valid umpire cache.")

        #Verify the section we're looking for is there 
        if CONFIG_REPO_SECTION_NAME not in parser.sections():
            raise CacheError("The config file appears to be missing the [umpire] section. Please verify this is the location of a valid umpire cache.")
        
        #Attempt to parse the data
        try:
            self.remote_url = parser.get(CONFIG_REPO_SECTION_NAME, "remote_url")
        except ConfigParser.Error:
            raise CacheError("Unable to determine the remote URL of this cache" + self.local_path)

        if not self.remote_url:
            raise CacheError("Unable to determine the remote URL of this cache:" + self.local_path)

        try:
            self.config_version = parser.get(CONFIG_REPO_SECTION_NAME, "config_version")
        except ConfigParser.Error:
            raise CacheError("Unable to determine the version of this cache: " + self.local_path)

        if not self.config_version:
            raise CacheError("Unable to determine the version of this cache: " + self.local_path)

    #Gets EntryInfo object, returns None if it doesn't exist.
    def get(self, platform, name, version):
        cs_entry_file = os.path.join(self.local_path, platform, name, version)
        entry_file = maestro.tools.path.get_case_insensitive_path(cs_entry_file)

        if entry_file is None:
            return None
        else:
            return read_entry(entry_file)
    
    #Locks a local entry
    def lock(self, entry):
        pass #TODO: Future

    def unlock(self, entry):
        pass #TODO: Future
        
    #Puts an archive of files into the cache 
    def put(self,archive_path, platform, name, version, unpack=True, force=False, keep_archive = False, keep_original = False):
        full_path = os.path.join(self.local_path, platform, name, version)
        case_insensitive_path = maestro.tools.path.get_case_insensitive_path(full_path)

        #If file exists, and we're not force deleting it throw an error
        if case_insensitive_path is not None and force is False:
            raise EntryError("Entry already exists under: " + case_insensitive_path + ". Please delete this entry, or enable force overwriting.")
        #Otherwise delete it
        elif case_insensitive_path is not None and force is True:
            shutil.rmtree(case_insensitive_path)

        try:
            os.makedirs(full_path)
        except OSError as e:
            raise CacheError("Unknown error in creating cache entry: " + str(e))
        
        #Copy archive to cache location
        shutil.copy(archive_path, full_path)

        #Remove original if we want
        if keep_original is False:
            os.remove(archive_path)

        unpacker = UnpackModule(None)
       
       #Unpack if necessary 
        if unpack is True:
            unpacker.destination_path = full_path
            unpacker.file_path = os.path.join(full_path, os.path.split(archive_path)[1])
            unpacker.delete_archive = not keep_archive
            unpacker.start()
            print "Unpacking " + os.path.split(archive_path)[1] + "..."

        entry = EntryInfo()
        entry.name = name
        entry.version = version
        entry.platform = platform
        entry.path = full_path

        #Write the entry
        write_entry(entry)

        #Lock the newly written entry
        self.lock(entry)

        if unpack is True:
            while unpacker.status == maestro.internal.module.RUNNING:
                time.sleep(0.2)
                if unpacker.exception is not None:
                    raise unpacker.exception


        
    #Set the repositories remote URL (updates local .umpire_repo file)
    def set_remote(url):
        pass #TODO: Future


if __name__ == "__main__":
    try:
        cache = create_local_cache("./test", "s3://bucketname")
        cache.put("../../poco-1.4.6p2-win64.tar.gz", "win64","poco","1.4.6p2", keep_original = True)
        cache.get("win64","poco","1.4.6p2")
    finally:
        #pass
        shutil.rmtree("./test")
