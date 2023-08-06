from st_library.core.dataprovider.structured_data.table import Table


class StructuredData(object):
    """
    A Category for work with structured data

    Attributes
    ----------
    Table : object
        The :class:`~st_library.core.dataprovider.structured_data.table.Table` class itself

    Examples
    --------
        >>> from st_library import Library
        >>> st_lib = Library()
        >>> table = st_lib.struct_data.Table('bar', 'baz', 'bar-baz')
        >>> table.upload_data('/foo/bar.csv')
        >>> sec_matrix = st_lib.struct_data.read_sec_matrix('foo', 'foo_dataset', 'foo_table_name')

    """

    def __init__(self):
        self.Table = Table

    def read_matrix(self, matrix_id, dataset_id, table_name):
        """
        Retrieve the table data from Global Space.

        Parameters
        ----------
        matrix_id : str
        dataset_id : str
        table_name : str

        Returns
        -------
        :class:`pandas.DataFrame`

        """
        tbl = self.Table(matrix_id, dataset_id, table_name)
        return tbl.to_dataframe()

    def read_sec_matrix(self, matrix_id, dataset_id, table_name):
        """
        Retrieve the table data from Script Execution Configuration Space.

        Parameters
        ----------
        matrix_id : str
        dataset_id : str
        table_name : str

        Returns
        -------
        :class:`pandas.DataFrame`

        """
        tbl = self.Table(matrix_id, dataset_id, table_name, config_related=True)
        return tbl.to_dataframe()
