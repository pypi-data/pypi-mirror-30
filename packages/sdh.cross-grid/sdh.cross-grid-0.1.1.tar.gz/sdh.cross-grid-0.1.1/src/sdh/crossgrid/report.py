from __future__ import unicode_literals

from collections import OrderedDict

from .column import Column
from .row import ReportRow


class CrossGridReport(object):
    def __init__(self, title, row_reduce, row_map, col_reduce, agg_function, header_map, row_sort=None):
        """
        row_reduce:   reference to row reduce function
                      it take element and should return row key

        row_map:      function to map row basic object;
                      take 1 argument: object;
                      value, returned by this function will be used when
                      printing row

        col_reduce:   same as row_reduce but for columns

        agg_function: function will call when added value to the column
                      for extract data from object;
                      take 2 arguments: object, current value

        header_map: function will call when adding new key into column header
                    take 1 argument: object

        """
        self.title = title
        self.row_reduce = row_reduce
        self.row_map = row_map
        self.col_reduce = col_reduce
        self.agg_function = agg_function
        self.header_map = header_map
        self.row_sort = row_sort

        self.row = OrderedDict()
        self.columns = OrderedDict()

    def append(self, obj):
        row_key = self.row_reduce(obj)
        col_key = self.col_reduce(obj)

        if col_key not in self.columns:
            self.columns[col_key] = self.header_map(obj)

        row_obj = self.row_map(obj)
        row = self.append_row(row_obj, row_key)
        row.append(col_key, obj)

    def append_row(self, row_obj, row_key):
        return self.row.setdefault(row_key, ReportRow(self, row_obj, row_key))

    def append_column(self, col_obj, col_key):
        self.columns.setdefault(col_key, col_obj)

    def iter_columns(self):
        return self.columns.values()

    def iter_columns_key(self):
        return self.columns.keys()

    def iter_rows(self):
        return self.row.values()

    def iter_column(self, col_key):
        for row in self.row.values():
            yield row.columns.get(col_key) or Column(self, col_key)
