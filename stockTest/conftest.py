import logging
import os
import pytest

# 로그 디렉토리 및 파일 설정
log_dir = "logs" #로그 디렉토리 생성
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, 'test_log.log')
#로그 저장 디렉토리경로 / 로그 파일명 ( 실행 시 마다 파일명 변경 해 줘야함)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=log_file,
                    filemode='w')
logger = logging.getLogger(__name__)


@pytest.fixture(scope='session', autouse=True)
def configure_logging():
    logging.getLogger().addHandler(logging.StreamHandler())
