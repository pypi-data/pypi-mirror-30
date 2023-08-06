""" File utils base class for Linux servers. """

import types
import socket
import logging
import stat as libstat

from urllib.parse import urlparse
from ... import FileUtils as FileUtilsBase

logger = logging.getLogger(__name__)

__all__ = ['FileUtils',]


class FileUtils(FileUtilsBase):
    DEFAULT_TIMEOUT_SECONDS = 60
    DEFAULT_COPY_TIMEOUT_SECONDS = 1200

    def close(self):
        """ Deallocate any resources being held.  """
        for child_name, child_obj in self.children.items():
            child_obj.close()


    def validate_and_parse_url(self, url, calling_method):
        """
        Returns
        -------
        server name, server port, resource path
        """
        parsed_url = urlparse(url)
        if parsed_url.username:
            logger.warning("The fileutils module {} is ignoring username {} "
                "passed as part of the url {} for method {}.  "
                "This must be passed in via testbed object.".\
                format(self.__module__, parsed_url.username,
                url, calling_method))

        if parsed_url.password:
            logger.warning("The fileutils module {} is ignoring password {} "
                "passed as part of the url {} for method {}.  "
                "This must be passed in via testbed object.".\
                format(self.__module__, parsed_url.password,
                url, calling_method))

        return parsed_url.hostname, parsed_url.port, parsed_url.path


    def get_child(self, abstraction_scheme, **kwargs):
        """ Attempt to load a protocol implementation.

        First, attempt to load a native Python implementation.
        If none is available, then attempt to load a curl-based
        implementation.

        Raises
        ------
        `Exception`
            if the requested protocol is not supported, this
            occurs when no plugin can be found.
        """

        try:
            child = super().get_child(abstraction_scheme)
        except Exception:
            curl_abstraction_key = 'curl.'+abstraction_scheme
            logger.debug("The fileutils module {} does not implement "
                "submodule {}.  Attempting to load submodule {}.".\
                format(self.__module__, abstraction_scheme,
                curl_abstraction_key))
            try:
                child = super().get_child(curl_abstraction_key)
            except Exception as exc:
                logger.debug("The fileutils module {} does not support "
                    "protocol {}.".format(self.__module__, abstraction_scheme))
                raise Exception("The protocol {} is not supported.".\
                    format(abstraction_scheme)) from exc

        return child


    def copyfile(self, from_file_url, to_file_url,
            timeout_seconds = DEFAULT_COPY_TIMEOUT_SECONDS,
            *args, **kwargs):

        logger.info("Copying file from {} to {} ...".\
            format(from_file_url, to_file_url))

        parsed_from_file_url = urlparse(from_file_url)
        parsed_to_file_url = urlparse(to_file_url)
        from_scheme = parsed_from_file_url.scheme
        to_scheme = parsed_to_file_url.scheme

        from_scheme_is_local = self.is_local(from_file_url)
        to_scheme_is_local = self.is_local(to_file_url)

        if from_scheme_is_local and to_scheme_is_local:
            raise Exception("fileutils module {} does not allow "
                "copying between two local files.".format(self.__module__))

        if not from_scheme_is_local and not to_scheme_is_local:
            raise Exception("fileutils module {} does not allow "
                "copying between two remote files.".format(self.__module__))


        abstraction_scheme = to_scheme if from_scheme_is_local else from_scheme

        # Get implementation
        child = self.get_child(abstraction_scheme, **kwargs)

        # Execute copy
        return child.copyfile(from_file_url, to_file_url, timeout_seconds,
            *args, upload=from_scheme_is_local, **kwargs)



    def dir(self, from_directory_url,
             timeout_seconds=DEFAULT_TIMEOUT_SECONDS, *args, **kwargs):

        logger.info("Retrieving directory listing for {} ...".\
            format(from_directory_url))

        parsed_url = urlparse(from_directory_url)
        scheme = parsed_url.scheme
        if self.is_local(from_directory_url):
            # Contents requested for local directory
            raise Exception("The fileutils module {} does not implement dir "
                "on a local directory.".format(self.__module__))
        else:
            # Dir requested for remote directory

            # Get implementation
            child = self.get_child(scheme, **kwargs)

            # Execute dir
            return child.dir(from_directory_url, timeout_seconds,
                *args, **kwargs)


    def stat(self, file_url,
             timeout_seconds=DEFAULT_TIMEOUT_SECONDS, *args, **kwargs):

        logger.info("Retrieving details for file {} ...".format(file_url))

        parsed_url = urlparse(file_url)
        scheme = parsed_url.scheme
        if self.is_local(file_url):
            # Contents requested for local directory
            raise Exception("The fileutils module {} does not implement stat "
                "on a local directory.".format(self.__module__))
        else:
            # Stat requested for remote directory

            # Get implementation
            child = self.get_child(scheme, **kwargs)

            # Execute stat
            return child.stat(file_url, timeout_seconds, *args, **kwargs)


    def chmod(self, file_url, mode,
             timeout_seconds=DEFAULT_TIMEOUT_SECONDS, *args, **kwargs):

        logger.info("Setting permissions of file {} to {} ...".\
            format(file_url, libstat.filemode(mode)))

        parsed_url = urlparse(file_url)
        scheme = parsed_url.scheme
        if self.is_local(file_url):
            # Contents requested for local directory
            raise Exception("The fileutils module {} does not implement chmod "
                "on a local directory.".format(self.__module__))
        else:
            # Chmod requested for remote directory

            # Get implementation
            child = self.get_child(scheme, **kwargs)

            # Execute chmod
            return child.chmod(file_url, mode, timeout_seconds,
                *args, **kwargs)


    def deletefile(self, file_url,
             timeout_seconds=DEFAULT_TIMEOUT_SECONDS, *args, **kwargs):

        logger.info("Deleting file {} ...".format(file_url))

        parsed_url = urlparse(file_url)
        scheme = parsed_url.scheme
        if self.is_local(file_url):
            # Contents requested for local directory
            raise Exception("The fileutils module {} does not implement "
                "deletefile on a local directory.".format(self.__module__))
        else:
            # Delete requested for remote directory

            # Get implementation
            child = self.get_child(scheme, **kwargs)

            # Execute chmod
            return child.deletefile(file_url, timeout_seconds, *args, **kwargs)


    def renamefile(self, from_file_url, to_file_url,
            timeout_seconds=DEFAULT_TIMEOUT_SECONDS, *args, **kwargs):

        logger.info("Renaming file {} to {} ...".\
            format(from_file_url, to_file_url))

        parsed_from_file_url = urlparse(from_file_url)
        parsed_to_file_url = urlparse(to_file_url)
        from_scheme = parsed_from_file_url.scheme
        to_scheme = parsed_to_file_url.scheme

        from_scheme_is_local = self.is_local(from_file_url)
        to_scheme_is_local = self.is_local(to_file_url)

        if from_scheme_is_local and to_scheme_is_local:
            raise Exception("fileutils module {} does not allow "
                "renaming local files.".format(self.__module__))

        if from_scheme_is_local != to_scheme_is_local:
            raise Exception("fileutils module {} requires from/to files to be "
                "renamed to both be remote.  Local files are not supported".\
                format(self.__module__))

        if from_scheme != to_scheme:
            raise Exception("fileutils module {} requires from/to files to be "
                "renamed to have the same protocol.".format(self.__module__))

        scheme = from_scheme

        # Rename requested for remote directory

        # Get implementation
        child = self.get_child(scheme, **kwargs)

        # Execute chmod
        return child.renamefile(from_file_url, to_file_url, timeout_seconds,
            *args, **kwargs)
