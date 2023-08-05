from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from pprint import pprint
from stylelens_product.bigquery.database import DataBase

TABLE_NAME = 'products'

class Products(DataBase):
  def __init__(self):
    super(Products, self).__init__()
    table_ref = self.dataset.table(TABLE_NAME)
    try:
      self.table = self.client.get_table(table_ref=table_ref)
    except NotFound as e:
      print(e)
      self.create_table(TABLE_NAME)

  def create_table(self, table_name):
    print('Create a table: {}'.format(table_name))
    schema = [
      bigquery.SchemaField('product_id', 'STRING', mode='REQUIRED'),
      bigquery.SchemaField('host_code', 'STRING', mode='REQUIRED'),
      bigquery.SchemaField('asin', 'STRING'),
      bigquery.SchemaField('host_group', 'STRING', mode='REQUIRED'),
      bigquery.SchemaField('host_name', 'STRING', mode='REQUIRED'),
    ]
    table_ref = self.dataset.table(table_name)
    _table = bigquery.Table(table_ref=table_ref, schema=schema)
    self.table = self.client.create_table(_table)

  def add_product(self, product):
    ret = self.client.insert_rows(self.table, [product])
    if not ret:
      print('Loaded {} row(s) into'.format(len(ret)))
    else:
      print('Errors:')
