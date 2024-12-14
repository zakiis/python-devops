from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

"""
The demonstration of how to use SQLAlchemy to operate a PostgreSQL database.
pip install sqlalchemy psycopg2 -i https://pypi.tuna.tsinghua.edu.cn/simple

Here is the table creation statement for t_user. Note that the TIMESTAMP type does not include timezone information.
```sql
CREATE TABLE t_user (
  id BIGSERIAL PRIMARY KEY,
  username VARCHAR(64),
  password VARCHAR(128),
  email VARCHAR(64),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_user_name ON t_user (username);
COMMENT ON TABLE t_user IS 'User';
```
You can use `SET timezone TO 'Asia/Shanghai';` or `SET timezone TO '+08:00';` to change the session timezone 
or `SHOW timezone;` to show the current timezone.
"""
DB_HOST = '192.168.137.101'
DB_PORT = '5432'
DB_USER = 'postgres'
DB_PASS = '123456'
DB_NAME = 'demo_db'
# Create database engine
engine_options = {
    "pool_size": 1,
    "max_overflow": 2,
    "pool_recycle": 600,
    "pool_pre_ping": True,
    "connect_args": {
        "options": '-c timezone=Asia/Shanghai'
    },
    "echo": False,
}
url = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
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
