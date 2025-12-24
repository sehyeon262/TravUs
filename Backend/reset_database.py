import MySQLdb
import os

# 데이터베이스 연결 설정
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1234',
    'port': 3306
}

# MySQL 연결 (데이터베이스 지정 없이)
print("MySQL에 연결 중...")
connection = MySQLdb.connect(**db_config)
cursor = connection.cursor()

# 기존 데이터베이스 삭제 및 재생성
print("기존 travus 데이터베이스 삭제 중...")
cursor.execute("DROP DATABASE IF EXISTS travus")
print("새 travus 데이터베이스 생성 중...")
cursor.execute("CREATE DATABASE travus CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
connection.commit()
cursor.close()
connection.close()

print("\n데이터베이스 초기화 완료!")
print("이제 travus.sql 파일을 임포트합니다...\n")

# travus 데이터베이스에 연결
db_config['database'] = 'travus'
connection = MySQLdb.connect(**db_config)
cursor = connection.cursor()

# SQL 파일 읽기 및 실행
sql_file_path = r'c:\Users\seorin\Desktop\travus\Backend\travus.sql'
print(f"SQL 파일 읽는 중: {sql_file_path}")

with open(sql_file_path, 'r', encoding='utf-8') as f:
    sql_content = f.read()

# SQL 문을 세미콜론으로 분리하여 실행
sql_commands = sql_content.split(';')
total = len(sql_commands)
print(f"총 {total}개의 SQL 명령 실행 중...\n")

for i, command in enumerate(sql_commands, 1):
    command = command.strip()
    if command:
        try:
            cursor.execute(command)
            if i % 10 == 0:
                print(f"진행 중... {i}/{total}")
        except Exception as e:
            if "empty query" not in str(e).lower():
                print(f"오류 발생 (명령 {i}): {e}")
                print(f"명령: {command[:100]}...")

connection.commit()
cursor.close()
connection.close()

print("\n✓ travus.sql 임포트 완료!")
print("데이터베이스가 성공적으로 교체되었습니다.")
