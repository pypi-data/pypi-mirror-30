#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: soya/process.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 19.03.2018

import pandas as pd

from abc import ABCMeta, abstractmethod


class Soya(object):
    """The abstract class for implementing the process.

    The class provides a interface `Soya.model` to implement the process, whose
    required parameters is given from `__init__`.

    The class initializes with following parameters:
        engine: a `Sqlalchemy.engine` to provide database connection
        input_dict: a dict of {`table_name`: a list of `table_field`}
        read_chunksize: an `int`, the chunk size of reading datum from
        database, default is None
        write_chunksize: an `int`, the chunk size of writing result to
        database, default is None
    """
    __metaclass__ = ABCMeta

    def __init__(
        self, engine, input_dict, read_chunksize=None,
        write_chunksize=None
    ):
        self.engine = engine
        self.input_dict = input_dict
        self.read_chunksize = read_chunksize
        self.write_chunksize = write_chunksize

    def _datum_import(self):
        """Import datumn from sql

        Return:
            datum: a `dict` of  (`DataFrame` or `iterator`
                    if read chunksize is not None)
        """
        return {
            tablename: pd.read_sql(
                'select {0} from {1}'.format(','.join(fields), tablename),
                self.engine, chunksize=self.read_chunksize
            ) for tablename, fields in self.input_dict.items()
        }

    @abstractmethod
    def model(self, datum, args):
        """Main process method to cal the datum

        Args:
            datum: a `dict` of  (`DataFrame` or `iterator`
                    if read chunksize is not None)
            args: an `dict`, the args to cal different result, default is None

        Return:
            result: `DataFrame`
        """
        return

    def run(self, result_name, args=None):
        """Run model to database

        Args:
            result_name: `str` of output result name
            args: an `dict`, the args to cal different result, default is None
        """
        result = self.model(self._datum_import(), args)
        result.to_sql(
            name=result_name, con=self.engine,
            chunksize=self.write_chunksize, if_exists='append',
            index=False
        )
