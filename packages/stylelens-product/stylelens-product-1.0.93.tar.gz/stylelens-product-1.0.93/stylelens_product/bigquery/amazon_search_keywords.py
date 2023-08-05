from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from pprint import pprint
from stylelens_product.bigquery.database import DataBase

TABLE_NAME = 'amazon_search_keywords'

class AmazonSearchKeywords(DataBase):
  def __init__(self):
    super(AmazonSearchKeywords, self).__init__()
    table_ref = self.dataset.table(TABLE_NAME)
    try:
      self.table = self.client.get_table(table_ref=table_ref)
    except NotFound as e:
      print(e)
      self.create_table(TABLE_NAME)

  def create_table(self, table_name):
    print('Create a table: {}'.format(table_name))
    schema = [
      bigquery.SchemaField('keywords', 'STRING', mode='REQUIRED'),
      bigquery.SchemaField('search_index', 'STRING', mode='REQUIRED'),
      bigquery.SchemaField('response_groups', 'STRING'),
      bigquery.SchemaField('browse_node', 'STRING', mode='REQUIRED'),
      bigquery.SchemaField('sort', 'STRING', mode='REQUIRED'),
    ]
    table_ref = self.dataset.table(table_name)
    _table = bigquery.Table(table_ref=table_ref, schema=schema)
    self.table = self.client.create_table(_table)

  def add_keywords(self, keywords):
    try:
      ret = self.client.insert_rows(self.table, keywords)
    except Exception as e:
      print(str(e))
