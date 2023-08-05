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
      bigquery.SchemaField('asin', 'STRING'),
      bigquery.SchemaField('parent_asin', 'STRING'),
      bigquery.SchemaField('detail_page_link', 'STRING'),
      bigquery.SchemaField('add_to_wishlist_link', 'STRING'),
      bigquery.SchemaField('title', 'STRING'),
      bigquery.SchemaField('s_image', 'RECORD',
                           fields=[
                             bigquery.SchemaField('url', 'STRING'),
                             bigquery.SchemaField('height', 'STRING'),
                             bigquery.SchemaField('width', 'STRING'),
                             bigquery.SchemaField('unit', 'STRING'),
                           ]
                           ),
      bigquery.SchemaField('m_image', 'RECORD',
                           fields=[
                             bigquery.SchemaField('url', 'STRING'),
                             bigquery.SchemaField('height', 'STRING'),
                             bigquery.SchemaField('width', 'STRING'),
                             bigquery.SchemaField('unit', 'STRING'),
                           ]
                           ),
      bigquery.SchemaField('l_image', 'RECORD',
                           fields=[
                             bigquery.SchemaField('url', 'STRING'),
                             bigquery.SchemaField('height', 'STRING'),
                             bigquery.SchemaField('width', 'STRING'),
                             bigquery.SchemaField('unit', 'STRING'),
                           ]
                           ),
      bigquery.SchemaField('binding', 'STRING'),
      bigquery.SchemaField('brand', 'STRING'),
      bigquery.SchemaField('department', 'STRING'),
      bigquery.SchemaField('color', 'STRING'),
      bigquery.SchemaField('clothing_size', 'STRING'),
      bigquery.SchemaField('size', 'STRING'),
      bigquery.SchemaField('price', 'RECORD',
                           fields=[
                             bigquery.SchemaField('amount', 'STRING'),
                             bigquery.SchemaField('currency_code', 'STRING'),
                             bigquery.SchemaField('formatted_price', 'STRING'),
                           ]
                           ),
      bigquery.SchemaField('lowest_price', 'RECORD',
                           fields=[
                             bigquery.SchemaField('amount', 'STRING'),
                             bigquery.SchemaField('currency_code', 'STRING'),
                             bigquery.SchemaField('formatted_price', 'STRING'),
                           ]
                           ),
      bigquery.SchemaField('highest_price', 'RECORD',
                           fields=[
                             bigquery.SchemaField('amount', 'STRING'),
                             bigquery.SchemaField('currency_code', 'STRING'),
                             bigquery.SchemaField('formatted_price', 'STRING'),
                           ]
                           ),
      bigquery.SchemaField('features', 'STRING'),
      bigquery.SchemaField('label', 'STRING'),
      bigquery.SchemaField('manufacturer', 'STRING'),
      bigquery.SchemaField('product_group', 'STRING'),
      bigquery.SchemaField('product_type_name', 'STRING')
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
