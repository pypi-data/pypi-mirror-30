from __future__ import unicode_literals


class Column(object):
    def __init__(self, report_row, key):
        self.key = key
        self.report_row = report_row
        self.value = None

    def append(self, obj):
        self.value = self.report_row.report.agg_function(obj, self.value)
