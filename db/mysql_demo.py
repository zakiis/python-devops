from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

"""
The demonstration of how to use SQLAlchemy to operate a MySQL database.
pip install sqlalchemy pymysql -i https://pypi.tuna.tsinghua.edu.cn/simple

Here is the table creation statement for t_user. Note that the datetime type does not include timezone information.
```sql
CREATE TABLE `t_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(64) DEFAULT NULL,
  `password` varchar(128) DEFAULT NULL,
  `email` varchar(64) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_user_name` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User';
```
"""
DB_HOST = '192.168.137.101'
DB_PORT = '3306'
DB_USER = 'root'
DB_PASS = '123456'
DB_NAME = 'demo_db'
# Create database engine
engine_options = {
    "pool_size": 1,
    "max_overflow": 2,
    "pool_recycle": 600,
    "pool_pre_ping": True,
    "connect_args": {
        "init_command": 'SET time_zone="+08:00"'
    },
    "echo": False,
}
url = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
db = create_engine(url=url, **engine_options)
# Create database session
Session = sessionmaker(bind=db, expire_on_commit=False)


def query_data():
    with Session() as session:
        sql = 'select username, email, created_at from t_user limit 10'
        result = session.execute(text(sql))
        return result.fetchall()


if __name__ == '__main__':
    rows = query_data()
    print(f'row count: {len(rows)}')
    for row in rows:
        username, email, created_at = row
        print(f'username={username}, email={email}, created_at={created_at}')
