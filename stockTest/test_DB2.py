import pytest
import pymysql as db
import os
import hashlib

@pytest.fixture(scope='module')
def connection_db():
    # 데이터베이스 연결 설정
    connection = db.connect(host='127.0.0.1', user='root', password='1234', db='test_stock', charset='utf8')
    yield connection  # fixture가 끝날 때까지 사용
    connection.close()  # 연결 닫기

def test_db_connection(connection_db):
    # 데이터베이스 연결 확인
    assert connection_db.open

def hashPass(password, salt):
    return hashlib.sha256(password.encode() + salt).hexdigest()

def get_test_data():
    # 테스트 데이터 정의
    passwords = ['password1', 'password2', 'password3', 'password4', 'password5',
                 'password6', 'password7', 'password8', 'password9', 'password10']
    test_data = []
    for i, password in enumerate(passwords, start=233324):
        salt = os.urandom(16)
        hashed_password = hashPass(password, salt)
        test_data.append((str(i), hashed_password, salt.hex(), f'username{i-233323}', f'address{i-233323}'))
    return test_data

# def create_table(connection):
#     # 테이블 생성
#     cur = connection.cursor()
#     cur.execute("CREATE TABLE test_usertb(id VARCHAR(20), pw VARCHAR(64), salt VARCHAR(32), uname VARCHAR(20), addr VARCHAR(50))")
#     connection.commit()
#
# def test_table_creation(connection_db):
#     # 테이블 생성
#     create_table(connection_db)

def get_database_data(connection):
#     # 데이터베이스에서 실제 데이터 가져오기
     cur = connection.cursor()
     cur.execute("SELECT * FROM test_usertb")
     db_data = cur.fetchall()
     return db_data

def insert_database_data(connection, data):
    # 데이터베이스에 데이터 입력
    cur = connection.cursor()
    sql = "INSERT INTO test_usertb(id, pw, salt, uname, addr) VALUES (%s, %s, %s, %s, %s)"
    cur.executemany(sql, data)
    connection.commit()

def test_data_insertion(connection_db):
    # 테스트 데이터 삽입
    test_data = get_test_data()
    insert_database_data(connection_db, test_data)

def del_database_data(connection):
     # 데이터베이스 데이터 삭제
     cur = connection.cursor()
     cur.execute("DELETE FROM test_usertb")
     connection.commit()

def test_data_deletion(connection_db):
#     # 데이터베이스 데이터 삭제
     del_database_data(connection_db)

@pytest.mark.parametrize('test_input', get_test_data())
def test_data_consistency(connection_db, test_input):
#     # 데이터베이스에서 실제 데이터 가져오기
     db_data = get_database_data(connection_db)

#     # 데이터베이스 데이터 딕셔너리로 변환
     db_data_dict = {data[0]: data for data in db_data}

#     # 테스트 데이터에서 ID, 해시된 비밀번호, salt, 유저명, 주소 추출
     test_id, test_hashed_password, test_salt, test_uname, test_addr = test_input


#     # 데이터베이스에 해당 ID가 있는지 확인
     assert test_id in db_data_dict

#     # 데이터베이스에서 해당 ID의 해시된 비밀번호와 salt, 유저명, 주소 가져오기
     db_id, db_hashed_password, db_salt_hex, db_uname, db_addr = db_data_dict[test_id]

#     # salt을 바이트로 변환
     db_salt = bytes.fromhex(db_salt_hex)

#     # 테스트 데이터의 비밀번호를 같은 salt으로 해시화
     calculated_hashed_password = hashPass(f'password{int(test_id) - 233323}', db_salt)

#     # 해시된 비밀번호, 유저명 일치하는지 확인
     assert db_hashed_password == calculated_hashed_password
     assert test_uname == db_uname
     # assert test_addr == db_addr
     print(f'test_ID: {test_id}, Hashed Password: {test_hashed_password}, Salt: {test_salt}')
     print(f'db_ID: {db_id}, Hashed Password: {db_hashed_password}, Salt: {db_salt_hex}')

     connection_db.execute("DELETE FROM test_usertb WHERE id = %s", (test_id,))
    
# pytest 메인 함수
if __name__ == "__main__":
    pytest.main()
