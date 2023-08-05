from __future__ import unicode_literals

from .column import Column


class ReportRow(object):
    def __init__(self, report, obj, row_key):
        self.key = row_key
        self.report = report
        self.columns = {}

        # will be used while rendering report as key object for row
        self.obj = obj
        if hasattr(self.obj, 'crossgrid_init'):
            _init = getattr(self.obj, 'crossgrid_init')
            if callable(_init):
                _init(self)

    def append(self, col_key, obj):
        col = self.columns.setdefault(col_key, Column(self, col_key))
        col.append(obj)

    def iter_columns(self):
        for col_key in self.report.columns.keys():
            yield self.columns.get(col_key) or Column(self, col_key)
