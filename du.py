from logic.logic import *
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import traceback


def getExpiry(url, browser):

    browser.get(url)
    try:
        elem = WebDriverWait(browser, 30).until(
            EC.presence_of_all_elements_located(
                (By.TAG_NAME, "b"))  # This is a dummy element
        )
        elements_var = BeautifulSoup(
            browser.page_source, features="html.parser").find_all('b')
        for a in elements_var:
            if 'days' in a.text:
                expiry = a.text
                browser.quit()
                return expiry
            elif 'hours' in a.text:
                expiry = a.text
                browser.quit()
                return expiry
            else:
                browser.quit()
                return None
    except Exception as e:
        print("there")
        print(e)
        return None
    finally:
        pass


head = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}
dates = {
    "Today": datetime.now().date(),
    "Yesterday": (datetime.now() - timedelta(days=1)).date(),
}


def checkTime(date):
    threedaysThreshold = datetime.now() - timedelta(days=3)
    if date >= threedaysThreshold:
        return True
    else:
        return False


def checkPrevious(url: str, pages: int):
    count = 0
    for i in range(1, pages):
        r = requests.get(url + str(i), headers=head)
        soup = BeautifulSoup(r.content, features="html.parser")
        elements = soup.find_all('span', {"class": "category"})
        for each in elements:
            child = each.findChild(
                'div', {"class": ['ui', 'green mb5', 'basic horizontal', 'label']})
            if child.text != None:
                if child.text == "Today":
                    count += 1
                    continue
                elif child.text == "Yesterday":
                    count += 1
                    continue
                else:
                    dt = parse(child.text)
                    check = checkTime(dt)
                    if check:
                        count += 1
                    continue
    return count


def getInfo(url: str, pages: int):
    courses = []

    for i in range(1, pages):
        r = requests.get("https://www.discudemy.com/all/" + str(i))
        soup = BeautifulSoup(r.content, features="html.parser")
        elements = soup.find_all('a', {"class": "card-header"})
        for each in elements:
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84"
            Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
            options = webdriver.FirefoxOptions()
            options.add_argument(f'user-agent={user_agent}')
            options.add_argument(f'Accept={Accept}')
            options.add_argument('--no-sandbox')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument("--headless")
            # options.add_argument('--disable-logging')
            options.binary_location = r'C:\\Program Files\\Mozilla Firefox\\firefox.exe'

            browser = webdriver.Firefox(options=options)
            name = each.text
            go_url = each["href"].split('/')[4]
            req = requests.get(f"https://www.discudemy.com/go/{go_url}")
            temp_soup = BeautifulSoup(req.content, features="html.parser")
            coupon_elem = temp_soup.find('a', {"id": "couponLink"})
            Coupon = ""
            if "?couponCode=" in str(coupon_elem["href"]):
                Coupon = str(coupon_elem["href"].split('?couponCode=')[1])
            expiry = getExpiry(coupon_elem["href"], browser)
            if expiry is not None and Coupon != "":
                print(expiry)
                print(name)
                print(Coupon)
                print(coupon_elem["href"])
                result = (expiry, name, Coupon, coupon_elem["href"])
                courses.append(result)
    return courses

# for i in range(1, 2):

#     r = requests.get("https://www.discudemy.com/all/1", headers=head)

#     soup = BeautifulSoup(r.content, features="html.parser")


#     # elements = soup.find_all(
#     # 'div', {"class": ['ui', 'green mb5', 'basic horizontal', 'label']})
#     elements = soup.find_all('span', {"class": "category"})
#     for each in elements:
#         child = each.findChild(
#             'div', {"class": ['ui', 'green mb5', 'basic horizontal', 'label']})
#         print(child.text)
# check courses first within 72 hours
time_start = datetime.now()

count = checkPrevious("https://www.discudemy.com/all/", 5)
if count > 20:
    courses = getInfo("https://www.discudemy.com/all/", 4)
    print(courses)

difference = datetime.now() - time_start
print(f'total time taken {difference.total_seconds() / 60} minutes')
