import pytest
import pymysql as db
import pandas as pd
import random


@pytest.fixture(scope='module')
def connection_db():
    # 데이터베이스 연결 설정
    connection = db.connect(host='127.0.0.1', user='root', password='1234', db='test_stock', charset='utf8')
    yield connection  # fixture가 끝날 때까지 사용
    connection.close()  # 연결 닫기


def test_db_connection(connection_db):
    # 데이터베이스 연결 확인
    assert connection_db.open


def get_test_data():
    # 테스트 데이터 정의
    stock_code = [160190, 479880, 464080, 478440, 477340, 34230, 107640, 478390, 477470, 458870]
    stock_data = []
    for i in stock_code:
        stock_data.append(f"ST{i}")
    return stock_data


# def create_table(connection):
#      stock_data = get_test_data()  # Add this line to define stock_data
#      cursor = connection.cursor()
#      for i in stock_data:
#          cursor.execute(f"create table {i} (t1 varchar(20))")
#          sql = f"INSERT INTO {i} VALUES(%s)"
#      cursor.execute(sql, ('test'))
#      cursor.commit()
#      connection.commit()
#
# def test_table_creation(connection_db):
#      # 테이블 생성
#      create_table(connection_db)

def get_database_data(connection):
    cur = connection.cursor()
    cur.execute(
        "SELECT table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'test_stock' AND table_name LIKE 'ST%'")
    table_list = [row[0] for row in cur.fetchall()]

    if len(table_list) >= 10:
        table_list.sort()
        print(f"Current tables: {table_list}")

        table_to_drop = table_list[0]
        print(f"Dropped table: {table_to_drop}")
        cur.execute(f"DROP TABLE {table_to_drop}")

        # 새로운 테이블 이름 생성
        random_suffix = str(random.randint(10000000, 99999999))  # 8자리 숫자 생성
        new_table_name = f"ST_{random_suffix}"

        # 새로운 테이블 생성 쿼리
        cur.execute(f"CREATE TABLE {new_table_name} (column1 INT, column2 VARCHAR(50))")
        print(f"Created new table: {new_table_name}")


def test_get_database_data(connection_db):
    get_database_data(connection_db)


# Add this line to define stock_data
#     stock_data = table_list
#     cur = connection.cursor()
#     for i in stock_data:
#         cur.execute(f"create table ST{i} (t1 varchar(20))")
#         sql = f"INSERT INTO {i} VALUES (%s)"
#     cursor.execute(sql, ('test'))
#     connection.commit()


# def test_data_consistency(connection_db):
#     get_database_data(connection_db)

# pytest 메인 함수
if __name__ == "__main__":
    pytest.main()
