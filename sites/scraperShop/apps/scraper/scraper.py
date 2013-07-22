
from dumptruck import DumpTruck

dt = DumpTruck(dbname="database_list.db")
def record_scraper_start(scraper, user, uuid):
    data = '{scraper':scraper, 'user': user, 'uuid': uuid, 'start':}
    table_name = 'scraping_record'
    unique_keys = ['uuid']
    dt.create_table(data, table_name = table_name, error_if_exists = False)
    dt.create_index(unique_keys, table_name, unique = True, if_not_exists = True)
    return dt.upsert(data, table_name = table_name)
