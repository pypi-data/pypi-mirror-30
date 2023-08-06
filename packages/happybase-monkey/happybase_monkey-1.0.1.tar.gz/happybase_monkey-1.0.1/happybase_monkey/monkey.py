# coding:utf-8
__author__ = 'qinman'
# create by qinman on 2018/4/13
import happybase

_table_buff = set()


class Table(happybase.connection.Table):
    """overwrite"""

    def put(self, row, data, timestamp=None, wal=True):
        self.old_put(row, data, timestamp, wal)
        index_name = "%s_index" % (self.name,)
        if index_name not in _table_buff:
            tables = self.connection.tables()
            if index_name not in tables:
                self.connection.create_table(index_name, {"info": dict()})
            _table_buff.add(index_name)
        self.connection.table(index_name).old_put(row, {"info:a": ""})

    def old_put(self, row, data, timestamp=None, wal=True):
        super(Table, self).put(row, data, timestamp, wal)


def monkey_path():
    """overwrite"""
    happybase.connection.Table = Table
