from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from pjMydb import saveCop

# 주식 종목 코드 및 회사 이름 크롤링
def findCopId(findData) :
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 5)

    driver.get("https://finance.naver.com/")
    search = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="stock_items"]')))
    search.click()
    search.send_keys(findData) # 사용자가 검색한 데이터 입력
    search.send_keys(Keys.RETURN)
    time.sleep(1)

    if driver.current_url.startswith("https://finance.naver.com/search/"):
        count = driver.find_element(By.CLASS_NAME, 'result_area')
        count = count.text[-3]
        if int(count) == 0 :
            driver.close()
            return False
        else :
            clickList = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="content"]/div[4]/table/tbody/tr[1]/td[1]/a')))
            clickList.click()
    copId = driver.current_url.split("=")[-1]
    copName = driver.find_element(By.XPATH, '//*[@id="middle"]/div[1]/div[1]/h2/a').text
    saveCop(copId, copName)

    driver.close()
    return copId

