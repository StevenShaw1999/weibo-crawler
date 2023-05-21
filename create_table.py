import pymysql
from rich import print
from items import *
from settings import * 

item_list = [
    # (WeiboChaohuaItem, "WeiboChaohuaItem"),
    # (DoubanUserFriendItem, "DoubanUserFriendItem"),
    # (DoubanUserGuangboItem, "DoubanUserGuangboItem"),
    # (WeiboTopicItem, "WeiboTopicItem"),
    # (DoubanCommentItem, "DoubanCommentItem"), # 8.24注释掉，换成try的代码
    (StatusesItem, "WeiboStatusItem4"),
    # (DoubanMovieListItem, "DoubanMovieListItem"),
]

def create():
    
    conn = pymysql.connect(host = MYSQL_HOST, 
                           port = MYSQL_PORT,
                           user = MYSQL_USER, 
                           passwd = MYSQL_PASSWORD, 
                           db = MYSQL_DBNAME,
                           charset = "utf8mb4")
    cursor = conn.cursor()

    for item, name in item_list:
        fields = list(item.fields.keys())
        field_sql = ','.join([ field + ' TEXT' for field in fields])
        create_sql = f"CREATE TABLE {name} ({field_sql}) CHARSET=utf8mb4;"
        print(f"Creating SQL: '{create_sql}'")
        try:
            cursor.execute(create_sql)
            conn.commit()
            print(f"Creating Table {name} Successfully.")
        except:
            print(f"Creating Table {name} Faield.")
        
        
create()    
    