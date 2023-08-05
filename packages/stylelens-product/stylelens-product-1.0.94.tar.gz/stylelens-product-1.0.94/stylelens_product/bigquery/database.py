import os
from google.cloud import bigquery

DATASET = 'bluelens'

GOOGLE_SERVICE_ACCOUNT_FILE = os.environ['GOOGLE_SERVICE_ACCOUNT_FILE']

class DataBase(object):
  def __init__(self):
    self.client = bigquery.Client.from_service_account_json(GOOGLE_SERVICE_ACCOUNT_FILE)
    self.job_config = bigquery.LoadJobConfig()

    self.dataset = self.client.dataset(DATASET)


  def list_datasets(self, project=None):
    """Lists all datasets in a given project.

    If no project is specified, then the currently active project is used.
    """
    bigquery_client = bigquery.Client(project=project)

    for dataset in bigquery_client.list_datasets():
      print(dataset.dataset_id)


  def create_dataset(self, dataset_id, project=None):
    """Craetes a dataset in a given project.

    If no project is specified, then the currently active project is used.
    """
    bigquery_client = bigquery.Client(project=project)

    dataset_ref = bigquery_client.dataset(dataset_id)

    dataset = bigquery_client.create_dataset(bigquery.Dataset(dataset_ref))

    print('Created dataset {}.'.format(dataset.dataset_id))


  def list_tables(self, dataset_id, project=None):
    """Lists all of the tables in a given dataset.

    If no project is specified, then the currently active project is used.
    """
    bigquery_client = bigquery.Client(project=project)
    dataset_ref = bigquery_client.dataset(dataset_id)

    for table in bigquery_client.list_dataset_tables(dataset_ref):
      print(table.table_id)


  def create_table(self, dataset_id, table_id, project=None):
    """Creates a simple table in the given dataset.

    If no project is specified, then the currently active project is used.
    """
    bigquery_client = bigquery.Client(project=project)
    dataset_ref = bigquery_client.dataset(dataset_id)

    table_ref = dataset_ref.table(table_id)
    table = bigquery.Table(table_ref)

    # Set the table schema
    table.schema = (
      bigquery.SchemaField('Name', 'STRING'),
      bigquery.SchemaField('Age', 'INTEGER'),
      bigquery.SchemaField('Weight', 'FLOAT'),
    )

    table = bigquery_client.create_table(table)

    print('Created table {} in dataset {}.'.format(table_id, dataset_id))


  def list_rows(self, dataset_id, table_id, project=None):
    """Prints rows in the given table.

    Will print 25 rows at most for brevity as tables can contain large amounts
    of rows.

    If no project is specified, then the currently active project is used.
    """
    bigquery_client = bigquery.Client(project=project)
    dataset_ref = bigquery_client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)

    # Get the table from the API so that the schema is available.
    table = bigquery_client.get_table(table_ref)

    # Load at most 25 results.
    rows = bigquery_client.list_rows(table, max_results=25)

    # Use format to create a simple table.
    format_string = '{!s:<16} ' * len(table.schema)

    # Print schema field names
    field_names = [field.name for field in table.schema]
    print(format_string.format(*field_names))

    for row in rows:
      print(format_string.format(*row))
