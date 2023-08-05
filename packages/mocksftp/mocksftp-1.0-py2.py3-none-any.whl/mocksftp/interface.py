import logging
import os
import shutil

import errno
import paramiko
import sys
from paramiko import SFTPAttributes

from mocksftp.decorators import returns_sftp_error

__all__ = [
    'SFTPServerInterface',
]


class SFTPHandle(paramiko.SFTPHandle):

    log = logging.getLogger(__name__)

    def __init__(self, file_obj, flags=0):
        super(SFTPHandle, self).__init__(flags)
        self.file_obj = file_obj

    @property
    def readfile(self):
        return self.file_obj

    @property
    def writefile(self):
        return self.file_obj


class SFTPServerInterface(paramiko.SFTPServerInterface):

    log = logging.getLogger(__name__)

    def __init__(self, server, *largs, **kwargs):
        self._root = kwargs.pop('root', None)
        super(SFTPServerInterface, self).__init__(server, *largs, **kwargs)

    def _path_join(self, path, follow_symlinks=True):
        path = os.path.normpath(os.path.join(self._root, path))
        if not path.startswith(self._root):
            raise OSError(errno.EACCES, "No access outside root", path)

        if follow_symlinks:
            path = os.path.realpath(path)
        return path

    def session_started(self):
        pass

    def session_ended(self):
        pass

    @returns_sftp_error
    def list_folder(self, path):
        path = self._path_join(path)
        result = []
        for filename in os.listdir(path):
            stat_data = os.stat(os.path.join(path, filename))
            item = SFTPAttributes.from_stat(stat_data)
            item.filename = filename
            result.append(item)
        return result

    @returns_sftp_error
    def mkdir(self, path, attr):
        path = self._path_join(path)
        os.mkdir(path)
        return paramiko.SFTP_OK

    @returns_sftp_error
    def rmdir(self, path):
        path = self._path_join(path)
        os.rmdir(path)
        return paramiko.SFTP_OK

    @returns_sftp_error
    def open(self, path, flags, attr):
        path = self._path_join(path)
        fd = os.open(path, flags)
        self.log.debug("open(%s): fd: %d", path, fd)
        if flags & (os.O_WRONLY | os.O_RDWR):
            mode = "w"
        elif flags & (os.O_APPEND):
            mode = "a"
        else:
            mode = "r"
        mode += "b"
        self.log.debug("open(%s): Mode: %s", path, mode)
        return SFTPHandle(os.fdopen(fd, mode), flags)

    @returns_sftp_error
    def chattr(self, path, attr):
        path = self._path_join(path, follow_symlinks=False)
        if attr.st_size is not None:
            if sys.version_info[0] >= 3:
                os.truncate(path, attr.st_size)
            else:
                fd = os.open(path, os.O_RDWR)
                try:
                    os.ftruncate(fd, attr.st_size)
                finally:
                    os.close(fd)

        if attr.st_uid is not None or attr.st_gid is not None:
            if attr.st_uid is None or attr.st_gid is None:
                return paramiko.SFTP_BAD_MESSAGE  # both must be given

            os.chown(path, attr.st_uid, attr.st_gid)

        if attr.st_mode is not None:
            os.chmod(path, attr.st_mode)

        if attr.st_atime is not None or attr.st_mtime is not None:
            if attr.st_atime is None or attr.st_mtime is None:
                return paramiko.SFTP_BAD_MESSAGE  # both must be given

            os.utime(path, (attr.st_atime, attr.st_mtime))

        return paramiko.SFTP_OK

    @returns_sftp_error
    def stat(self, path):
        path = self._path_join(path, follow_symlinks=False)
        st = os.stat(path)
        return paramiko.SFTPAttributes.from_stat(st, path)

    @returns_sftp_error
    def lstat(self, path):
        path = self._path_join(path, follow_symlinks=False)
        st = os.lstat(path)
        return paramiko.SFTPAttributes.from_stat(st, path)

    @returns_sftp_error
    def rename(self, oldpath, newpath):
        oldpath = self._path_join(oldpath, follow_symlinks=False)
        newpath = self._path_join(newpath)
        # By using shutil, the file can be copied between filesystems.
        # This falls back to os.rename() for files at the same filesystem.
        shutil.move(oldpath, newpath)
        return paramiko.SFTP_OK

    posix_rename = rename

    @returns_sftp_error
    def readlink(self, path):
        path = self._path_join(path, follow_symlinks=False)
        return os.readlink(path)

    @returns_sftp_error
    def remove(self, path):
        path = self._path_join(path, follow_symlinks=False)
        os.remove(path)
        return paramiko.SFTP_OK

    @returns_sftp_error
    def symlink(self, target_path, path):
        self._path_join(target_path)  # only to check root level.
        path = self._path_join(path, follow_symlinks=False)
        os.symlink(target_path, path)
        return paramiko.SFTP_OK
