from .column import *

class Table:
    def __init__(self, table_name: str, *args):
        """
        :param table_name: XML tag preceded with parent tags separated by underscore.
            eg. Parent_Child_Child
        :param *args: A list of column and constraint definitions
        """
        self._table_name = table_name
        self.column_definitions = []
        self.constraint_definitions = []
        for arg in args:
            if isinstance(arg, Column):
                self.column_definitions.append(arg)
            elif isinstance(arg, Key):
                self.constraint_definitions.append(arg)

    def get_column(self, column_name: str):
        """
        Returns column definition. Raises a KeyError if column wasn't defined

        :param column_name: Name of the column to retrieve
        """
        try:
            return next(column for column in self.column_definitions if column.column_name == column_name)
        except StopIteration:
            raise KeyError()

    @property
    def table_name(self):
        return self._table_name