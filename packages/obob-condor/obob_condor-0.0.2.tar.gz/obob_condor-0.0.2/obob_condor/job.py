# -*- coding: UTF-8 -*-
# Copyright (c) 2018, Thomas Hartmann
#
# This file is part of the obob_condor Project, see: https://gitlab.com/obob/obob_condor
#
#    obob_condor is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    obob_condor is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with obob_subjectdb. If not, see <http://www.gnu.org/licenses/>.
import gzip
import importlib
import inspect
import json
import os
import sys
import six


class JobBase(object):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def shall_run(self, *args, **kwargs):
        return True

    def run_private(self):
        return self.run(*self._args, **self._kwargs)

    def shall_run_private(self):
        return self.shall_run(*self._args, **self._kwargs)

class Job(JobBase):
    """
    Abstract class for Jobs. This means, in order to define you own jobs, they need to be a subclass of this one.

    You **must** implement (i.e. define in your subclass) the :func:`run` method. The run method can take as many
    arguments as you like. Only the types of arguments are restricted because they need to be saved to disk. In general,
    strings, numbers, lists and dictionaries are fine.

    You **can** implement :func:`shall_run`. This can be used to see whether some output file already exists and restrict
    job submission to missing files.
    """

    def run(self, *args, **kwargs):
        """
        Implement this method to do the job.
        """
        raise NotImplementedError

    def shall_run(self, *args, **kwargs):
        """
        This is an optional method. It gets called with the same arguments as the :func:`run` method, **before** the job
        is submitted. If it returns True, the job is submitted, if it returns False, it is not.
        """
        return True


class JobItem(object):
    """
    Internal class for items in the job queue
    """

    def __init__(self, job_class_or_file, *args, **kwargs):
        if isinstance(job_class_or_file, six.string_types):
            self._init_from_json(job_class_or_file)
        elif Job in inspect.getmro(job_class_or_file):
            self._init_from_class(job_class_or_file, *args, **kwargs)
        else:
            raise TypeError('JobItem needs either a filename or a job class')

    def _init_from_class(self, job_class, *args, **kwargs):
        self.job_module = inspect.getmodule(job_class).__name__
        if self.job_module == '__main__':
            (path, f_name) = os.path.split(sys.argv[0])
            self.job_module = os.path.splitext(f_name)[0]

        self.job_class = job_class.__name__

        self.args = args
        self.kwargs = kwargs

    def _init_from_json(self, f_name):
        with gzip.open(f_name, 'rt') as gzip_file:
            raw_dict = json.load(gzip_file)
            self.job_class = raw_dict['job_class']
            self.job_module = raw_dict['job_module']
            self.args = raw_dict['args']
            self.kwargs = raw_dict['kwargs']

    def make_object(self):
        mod = importlib.import_module(self.job_module)
        this_class = getattr(mod, self.job_class)

        return this_class(*self.args, **self.kwargs)

    def to_json(self, f_name):
        with gzip.open(f_name, 'wt') as gzip_file:
            json.dump({
                'job_class': self.job_class,
                'job_module': self.job_module,
                'args': self.args,
                'kwargs': self.kwargs
            }, gzip_file)

    def __str__(self):
        return '.'.join((self.job_module, self.job_class))