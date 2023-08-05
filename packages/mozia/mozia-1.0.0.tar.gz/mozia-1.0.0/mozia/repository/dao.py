import pymysql


def create_connection(db):
    return pymysql.connect(host='localhost',
                           user='root',
                           password='dba123456',
                           db=db,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)


class Repository:
    def __init__(self, db="browns"):
        self.connection = create_connection(db)
