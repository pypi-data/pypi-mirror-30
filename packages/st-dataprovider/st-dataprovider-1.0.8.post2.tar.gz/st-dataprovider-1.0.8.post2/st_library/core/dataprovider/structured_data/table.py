# Copyright 2017 Shortest Track Company. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.

"""Implements Table, and related Table BigQuery APIs."""
import pandas

from st_library.core.dataprovider.structured_data import parser
from st_library.core.dataprovider.structured_data import schema
from st_library.utils.api_client.services.structured_data import StructuredDataService
from st_library import exceptions


# import of Query is at end of module as we have a circular dependency of
# Query.execute().results -> Table and Table.sample() -> Query

class Table(object):
    """
    Represents a Table object referencing a BigQuery table.

    Parameters
    ----------
    matrix_id : str
    dataset_id : str
    name : str
        The name of the table
    context
    config_related : bool
        This parameter determines whether the table is related to
        Script Execution Configuration or not

    Attributes
    ----------
    schema : :class:`~st_library.core.dataprovider.structured_data.schema.Schema`
        A Schema object containing a list of schema fields and associated metadata.

    """

    # Allowed characters in a BigQuery table column name
    _VALID_COLUMN_NAME_CHARACTERS = '_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    # When fetching table contents, the max number of rows to fetch per HTTP request
    _DEFAULT_PAGE_SIZE = 1024

    # Milliseconds per week
    _MSEC_PER_WEEK = 7 * 24 * 3600 * 1000

    def __init__(self, matrix_id=None, dataset_id=None, name=None, context=None, config_related=False):
        self._context = context
        self._service = StructuredDataService()
        self._name_parts = name
        self._datasets_id = dataset_id
        self._matrices_id = matrix_id
        self._info = None
        self._cached_page = None
        self._cached_page_index = 0
        self._schema = None
        self._config_related = config_related

    def _load_info(self):
        """
        Loads metadata about this table.
        """
        if self._info is None:
            try:
                self._info = self._service.tables_get(self._matrices_id)
            except Exception as e:
                raise e

    def _get_row_fetcher(self, start_row=0, max_rows=None, page_size=_DEFAULT_PAGE_SIZE):
        """
        Get a function that can retrieve a page of rows.

        Parameters
        ----------
            start_row: int
                the row to start fetching from; default 0.

            max_rows: int
                the maximum number of rows to fetch (across all calls, not per-call). Default
                is None which means no limit.

            page_size: int
                the maximum number of results to fetch per page; default 1024.

        Returns
        -------
            `callable` A function that can be called repeatedly with a page token and running count, and that
            will return an array of rows and a next page token; when the returned page token is None
            the fetch is complete.

        Notes
        -----
            The function returned is a closure so that it can have a signature suitable for use
            by Iterator.

        """
        if not start_row:
            start_row = 0
        elif start_row < 0:  # We are measuring from the table end
            if self.length >= 0:
                start_row += self.length
            else:
                raise Exception('Cannot use negative indices for table of unknown length')

        schema = self.schema._bq_schema
        name_parts = self._name_parts

        def _retrieve_rows(page_token, count):

            page_rows = []
            if max_rows and count >= max_rows:
                page_token = None
            else:
                if max_rows and page_size > (max_rows - count):
                    max_results = max_rows - count
                else:
                    max_results = page_size

                try:
                    if page_token:
                        response = self._service.tabledata_list(self._config_related, self._datasets_id,
                                                                name_parts, page_token=page_token,
                                                                max_results=max_results)
                    else:
                        response = self._service.tabledata_list(self._config_related, self._datasets_id,
                                                                name_parts, start_index=start_row,
                                                                max_results=max_results)
                except Exception as e:
                    raise e
                page_token = response['pageToken'] if 'pageToken' in response else None
                if 'rows' in response:
                    page_rows = response['rows']

            rows = []
            for row_dict in page_rows:
                rows.append(parser.Parser.parse_row(schema, row_dict))

            return rows, page_token

        return _retrieve_rows

    def to_dataframe(self, start_row=0, max_rows=None):
        """
        Exports the table to a Pandas dataframe.

        Parameters
        ----------
            start_row: int
                the row of the table at which to start the export (default 0)

            max_rows: int
                an upper limit on the number of rows to export (default None)

        Returns
        -------
            :class:`pandas.DataFrame` containing the table data.

        """
        fetcher = self._get_row_fetcher(start_row=start_row, max_rows=max_rows)
        count = 0
        page_token = None
        df = None
        while True:
            page_rows, page_token = fetcher(page_token, count)
            if len(page_rows):
                count += len(page_rows)
                if df is None:
                    df = pandas.DataFrame.from_records(page_rows)
                else:
                    df = df.append(page_rows, ignore_index=True)
            if not page_token:
                break

        # Need to reorder the dataframe to preserve column ordering
        ordered_fields = [field.name for field in self.schema]
        return df[ordered_fields] if df is not None else pandas.DataFrame()

    @property
    def schema(self):
        if not self._schema:
            try:
                self._load_info()
                self._schema = schema.Schema(self._info['matrixScheme']['fieldSchemes'])

            except KeyError:
                raise exceptions.InternalError('Unexpected table response: missing schema')
        return self._schema

    def upload_data(self, filename=None):
        """
        Upload csv data file to table.

        Parameters
        ----------
        filename: str
            the name of the csv file

        """
        response = self._service.tabledata_post(self._datasets_id, self._name_parts, filename)

    def insert_data(self, json_data=None):
        """
        Insert streams data into matrix.

        Parameters
        ----------
        json_data: object
            the records of the matrix

        """
        response = self._service.insert_data(self._datasets_id, self._name_parts, json_data)

    def insert_sec_data(self, json_data=None):
        """
        Insert streams data into matrix.

        Parameters
        ----------
        json_data: object
            the records of the matrix

        """
        response = self._service.insert_sec_data(self._datasets_id, self._name_parts, json_data)

    def insert_batch_sec_data(self, file_path=None, file_name=None):
        """
        Insert streams data into matrix.

        Parameters
        ----------
        file_path: str
            the path to the csv file

        file_name: str
            the name of the csv file

        """
        response = self._service.insert_batch_sec_data(self._datasets_id, self._name_parts, file_path, file_name)
