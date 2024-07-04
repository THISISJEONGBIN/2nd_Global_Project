import configparser
import mysql.connector as db
from mysql.connector import Error
import pandas as pd
import hashlib
import sys
import os

class User :
    def __init__(self, username, pw, uname, email):
        self.username = username
        self.password = pw
        self.uname = uname
        self.email = email

class UserBuilder :
    def __init__(self):
        self.reset()

    def reset(self):
        self.username = None
        self.password = None
        self.uname = None
        self.email = None

    def setUsername(self, username):
        self.username = username
        return self

    def setPassword(self, password):
        self.password = password
        return self

    def setUname(self, uname):
        self.uname = uname
        return self

    def setEmail(self, email):
        self.email = email
        return self

    def build(self):
        return User(self.username, self.password, self.uname, self.email)

base_path = os.path.abspath(".")
config_path = os.path.join(base_path, "db_config.ini")

def createDbConfig(configPath) :
    config = configparser.ConfigParser()
    config['mysql'] = {
        'host': 'localhost',
        'database' : 'your databasename',
        'user' : 'your username',
        'password' : 'your password',
        'charset' : 'your charset'}
    with open(configPath, 'w') as configfile:
        config.write(configfile)

if not os.path.exists(config_path):
    createDbConfig(config_path)

def getDbConfig() :
    config = configparser.ConfigParser()
    config.read(config_path)
    return config['mysql']

def connectToDb() :
    try :
        config = getDbConfig()
        conn = db.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset=config['charset'])

        cur = conn.cursor()

        tableName1 = 'usertb'
        tableName2 = 'copname'

        cur.execute(f"SHOW TABLES LIKE '{tableName1}'")
        result = cur.fetchone()

        if not result :
            cur.execute(f"CREATE TABLE {tableName1}(id varchar(20), pw varchar(255), salt varchar(100), uname varchar(30), addr varchar(30))")

        cur.execute(f"SHOW TABLES LIKE '{tableName2}'")
        result = cur.fetchone()

        if not result :
            cur.execute(f"CREATE TABLE {tableName2} (stockid varchar(20), stockname varchar(20))")

        conn.commit()
        return conn
    except db.DatabaseError as e :
        print(f"Database Error: {e}")

# fdr로 다운받은 주식데이터 DB 저장
def saveStock(stockTarget, stockDf) :
    try :
        stockCode = "ST"+stockTarget # 종목코드는 숫자로 시작하는 경우가 있어, 문자 ST를 붙여 테이블 이름 지정
        conn = connectToDb()
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'stock' AND table_name LIKE 'ST%'")
        table_list = [row[0] for row in cur.fetchall()]

        # 테이블의 개수가 10개 이상시, 해당 코드의 회사 이름이 있는 행을 지운 뒤, 해당 코드의 주식 데이터 테이블 제거
        if len(table_list) >= 10 :
            table_list.sort()
            table_to_drop = table_list[0]
            copName = table_to_drop.upper()
            sql = 'delete from copname where stockid = %s'
            cur.execute(sql, (copName))
            cur.execute(f"DROP TABLE {table_to_drop}")
            print("delete copname & drop table")
            conn.commit()

        # 중복되는 테이블이 없을 경우 새로운 테이블 생성
        if stockCode.lower() not in table_list :
            cur.execute("create table %s(SK_DATE DATE, SK_OPEN FLOAT, SK_HIGH FLOAT, SK_LOW FLOAT, SK_CLOSE FLOAT, SK_VOLUME FLOAT)" % stockCode)
            for i, j in stockDf.iterrows() :
                sql = f"INSERT INTO {stockCode} VALUES(%s, %s, %s, %s, %s, %s)"
                cur.execute(sql, (i.strftime('%Y-%m-%d'), float(j['Open']), float(j['High']), float(j['Low']), float(j['Close']), float(j['Volume'])))
            conn.commit()

        # 종목 코드에 맞는 테이블 검색 후 반환
        cur.execute("select * from %s" % stockCode)
        columns = [desc[0] for desc in cur.description]
        stockData = pd.DataFrame(cur.fetchall(), columns=columns)
        stockData = stockData.sort_values(by=['SK_DATE'])

        cur.close()
        conn.close()
        return stockData

    except db.DatabaseError as e :
        print(e)

# 회사 이름 데이터 저장
def saveCop(stockTarget, stockName) :
    try :
        stockCode = "ST"+stockTarget
        conn = connectToDb()
        cur = conn.cursor()

        cur.execute("SELECT * FROM copname")
        copId_list = [row[0] for row in cur.fetchall()] # 테이블에 저장되는 종목 코드를 리스트화

        # 검색한 주식 코드가 테이블 안에 저장되어 있지 않을 경우 해당 주식 코드 및 회사 이름을 테이블에 저장
        if stockCode not in copId_list :
            sql = "INSERT INTO copname values(%s, %s)"
            cur.execute(sql, (stockCode, stockName))
            conn.commit()

        cur.close()
        conn.close()

    except db.DatabaseError as e :
        print(e)

# 비밀번호 해싱 작업
def hashPass(password, salt):
    return hashlib.sha256(password.encode() + salt).hexdigest()

# 회원가입 유저에 대한 DB 저장
def regiUser(userInfo):
    try :
        conn = connectToDb()
        cur = conn.cursor()
        salt = os.urandom(16)
        hashed_password = hashPass(userInfo.password, salt)
        sql = "INSERT INTO usertb(id, pw, salt, uname, addr) VALUES (%s, %s, %s, %s, %s)"
        cur.execute(sql, (userInfo.username, hashed_password, salt.hex(), userInfo.uname, userInfo.email))
        conn.commit()
        cur.close()
        conn.close()

    except db.DatabaseError :
        pass

# 로그인 유저에 대한 매칭 작업
def login_user(loginId, loginPass) :
    try :
        conn = connectToDb()
        cur = conn.cursor()
        sql = "SELECT pw, salt FROM usertb WHERE id = %s"
        cur.execute(sql, (loginId,))
        result = cur.fetchone()
        if result :
            dbPass, salt = result
            salt = bytes.fromhex(salt)
            hashed_password = hashPass(loginPass, salt)
            if hashed_password == dbPass :
                return True
            return False

    except db.DatabaseError as e :
        print(e)
