"""Module doing the actual Spark management
"""
from contextlib import contextmanager
from functools import update_wrapper
from pyspark.sql import SparkSession
from six import iteritems

import json
import os
import time


class SparkReport(object):
    """Save time differences to a file
    """
    def __init__(self, filename, manager):
        """Create a new instance

        :param filename: filename to store data in
        :param manager: spark manager to query for additional data
        """
        self.__filename = filename
        self.__report = {
            'parallelism': manager.defaultParallelism,
            'timing': [[]],
            'version': manager.spark.version
        }
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        elif os.path.exists(filename):
            with open(filename, 'r') as fd:
                data = json.load(fd)
                self.__report['timing'] = data['timing'] + [[]]

    def __call__(self, name, delta):
        """Update stored information

        :param name: key to use
        :param delta: timedifference to store
        """
        self.__report['timing'][-1].append((name, delta))
        with open(self.__filename, 'w') as fd:
            json.dump(self.__report, fd)


class SparkManager(object):
    """Manage Spark with a singular object
    """
    def __init__(self):
        self.__session = None
        self.__context = None

        self.__allowed = None
        self.__overlap = None

        self.__gstack = [(None, None)]

        self.__cleaning = False
        self.__report = None

    @property
    def spark(self):
        """:property: the Spark session
        """
        return self.__session

    @property
    def sc(self):
        """:property: the Spark context
        """
        return self.__context

    def __getattr__(self, attr):
        """Provide convenient access to Spark functions
        """
        if attr in self.__dict__:
            return self.__dict__[attr]
        if self.__overlap is None:
            raise ValueError("Spark has not been initialized yet!")
        if attr in self.__overlap:
            raise AttributeError("Cannot resolve attribute unambiguously!")
        if attr not in self.__allowed:
            raise AttributeError("Cannot resolve attribute '{}'! Allowed attributes: {}".format(
                attr, ", ".join(sorted(self.__allowed))))
        try:
            return getattr(self.__session, attr)
        except AttributeError:
            return getattr(self.__context, attr)

    def create(self, name=None, config=None, options=None, report=None, reset=False):
        """Create a new Spark session if needed

        Will use the name and configuration options provided to create a new
        spark session and populate the global module variables.

        :param name: the name of the spark application
        :param config: configuration parameters to be applied before
                       building the spark session
        :param options: environment options for launching the spark session
        :param report: filename to save a timing report
        :type report: str
        :param reset: create a new Spark session
        :type reset: bool
        """
        if self.__session and not reset:
            return self.__session

        # TODO auto-generate name?
        if not name:
            raise ValueError("need a name for a new spark session")

        if options:
            os.environ['PYSPARK_SUBMIT_ARGS'] = options + ' pyspark-shell'

        session = SparkSession.builder.appName(name)

        if config:
            for k, v in iteritems(config):
                session.config(k, v)

        self.__session = session.getOrCreate()
        self.__context = self.__session.sparkContext

        s_attr = set(dir(self.__session))
        c_attr = set(dir(self.__context))

        self.__allowed = s_attr | c_attr
        self.__overlap = s_attr & c_attr

        identical = set(i for i in self.__overlap
                        if getattr(self.__session, i) is getattr(self.__context, i))
        self.__overlap -= identical
        self.__allowed |= identical

        if report:
            self.__report = SparkReport(report, self)

        return self.__session

    def assign_to_jobgroup(self, f):
        """Assign a spark job group to the jobs started within the decorated
        function

        The job group will be named after the function, with the docstring as
        description.

        :param f: function to decorate
        """
        n = f.__name__
        d = f.__doc__.strip() if f.__doc__ else ''

        def new_f(*args, **kwargs):
            with self.jobgroup(n, d):
                return f(*args, **kwargs)
        return update_wrapper(new_f, f)

    @contextmanager
    def benchmark(self):
        """Create a setup for benchmarking

        Performs a little warmup procedure.

        .. warning::

           Will clear the cache when running!
        """
        try:
            self.reset_cache()
            # Warm-up
            df = self.spark.range(1000)
            df.count()
            yield
        finally:
            pass

    @contextmanager
    def clean_cache(self):
        """Clean the rdd cache

        .. warning::

           May not preserve Dataframes correctly!
        """
        if self.__cleaning:
            msg = "Nested cleaning of temporary RDDs is not supported!"
            raise NotImplementedError(msg)
        self.__cleaning = True
        pre = set(rdd.id() for _, rdd in iteritems(self.sc._jsc.getPersistentRDDs()))
        try:
            yield
        finally:
            post = set(rdd.id() for _, rdd in iteritems(self.sc._jsc.getPersistentRDDs()))
            by_id = {r.id(): r for r in self.sc._jsc.getPersistentRDDs().values()}
            for rdd in post - pre:
                by_id[rdd].unpersist()
            self.__cleaning = False

    @contextmanager
    def jobgroup(self, name, desc=""):
        """Temporarily assign a job group to spark jobs within the context

        :param name: the name of the spark group to use
        :param desc: a longer description of the job group
        """
        self.__context.setJobGroup(name, desc)
        self.__gstack.append((name, desc))
        try:
            start = time.time()
            yield
        finally:
            if self.__report:
                self.__report(name, time.time() - start)
            self.__gstack.pop()
            self.__context.setJobGroup(*self.__gstack[-1])

    def reset_cache(self):
        """Clear all caches
        """
        for _, rdd in iteritems(self.sc._jsc.getPersistentRDDs()):
            rdd.unpersist()
        self.catalog.clearCache()
