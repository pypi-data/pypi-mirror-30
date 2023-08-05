#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-12-03
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93

from ftplib import FTP, error_perm
import os


def ftp_decorator(func):
    """
    Decorator for initialize ftp connection
    """
    def wrapper(self, *args):
        try:
            ftp = FTP()
            ftp.connect(self.host, self.port, self.timeout)
            ftp.login(self.name, self.password)
            result = func(self, ftp, *args)
            return result
        except error_perm as e:
            raise convert_exc(e, args)
        finally:
            try:
                ftp.quit()
            except:
                pass
    return wrapper

def convert_exc(exc, args):
    """
    Help method for convert ftp response error to pylib error
    """
    msg = str(exc).lower()
    if "550" not in msg:
        return exc
    if "privileges" in msg:
        return PermissionError("no permission to access file/dir in ftp: %s" % str(args))
    elif "exists" in msg:
        return FileExistsError("file/dir already exist in ftp: %s" % str(args))
    elif "no such" in msg or "not a directory" in msg:
        return FileNotFoundError("file/dir not exists in ftp: %s" % str(args))
    else:
        return Exception(msg + str(args))


class FTPClient(object):
    """
    FTP client for crud file/dir in ftp filesystem
    """

    def __init__(self, host, port, timeout, name, password, buffer_size):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.name = name
        self.password = password
        self.buffer_size = buffer_size

    def _get_info(self, ftp, path):
        """
        Obtain the information of the file/dir by the given [path]
        """
        if path.endswith("/"):
            path = path[0:-1]
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        result = []
        try:
            ftp.dir(dirname, result.append)
            for item in result:
                if item.split(" ")[-1] == basename:
                    return item
        except error_perm as e:
            exc = convert_exc(e)
            if isinstance(exc, FileNotFoundError):
                return None
            raise exc

    @ftp_decorator
    def isfile(self, ftp, path):
        """
        Check if it's a file
        """
        info = self._get_info(ftp, path)
        if info:
            return info.startswith("-")
        return False

    @ftp_decorator
    def isdir(self, ftp, path):
        """
        Check if it's a directory
        """
        if path == "" or path =="/":
            return True
        info = self._get_info(ftp, path)
        if info:
            return info.startswith("d")
        return False

    def _isexist(self, ftp, path):
        """
        Help method for checking if the file/dir is exist
        """
        try:
            ftp.dir(path)
            return True
        except Exception as e:
            exc = convert_exc(e)
            if isinstance(exc, FileNotFoundError):
                return False
            raise exc

    @ftp_decorator
    def isexist(self, ftp, path):
        """
        Check if it's exist
        """
        return self._isexist(ftp, path)

    @ftp_decorator
    def mkdir(self, ftp, path):
        """
        Make a directory
        raise a exception if already exist
        """
        ftp.mkd(path)

    @ftp_decorator
    def mkdir_if_not_exist(self, ftp, path):
        """
        Make a directory by the given 'path' in ftp
        """
        if not self._isexist(ftp, path):
            ftp.mkd(path)

    @ftp_decorator
    def download(self, ftp, localfile, dirname, filename):
        """
        Download a file from ftp
        """
        command = "RETR " + os.path.join(dirname, filename)
        ftp.retrbinary(command, localfile.write, self.buffer_size)

    @ftp_decorator
    def read(self, ftp, func, dirname, filename):
        """
        Read file in ftp server, callback 'fun' when buffer full
        """
        command = "RETR " + os.path.join(dirname, filename)
        ftp.retrbinary(command, func, self.buffer_size)

    @ftp_decorator
    def upload(self, ftp, localfile, dirname, filename):
        """
        Upload a file to ftp
        """
        command = "STOR " + os.path.join(dirname, filename)
        ftp.storbinary(command, localfile, self.buffer_size)
