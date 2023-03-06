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


def checkTime(date):
    threedaysThreshold = datetime.now() - timedelta(days=3)
    if date >= threedaysThreshold:
        return True
    else:
        return False


def udemyCheck(requestBody):
    soupp = BeautifulSoup(requestBody, features="html.parser")
    element = soupp.find('span', {
                         "data-purpose": "safely-set-inner-html:discount-expiration:expiration-text"})
    print("done")


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


url = "https://www.udemyfreebies.com/free-udemy-courses/"
# print(req.text)
time_start = datetime.now()
courses = []
try:
    count = 0
    for i in range(1, 7):
        req_url = url + str(i)
        req = requests.get(
            req_url)

        soup = BeautifulSoup(req.text, "html.parser")
        elements = soup.find_all('div', {"class": "theme-block"})
        # check if 20 coupons were posted within 72 hours
        for each in elements:
            child = each.find(['small']).text
            dt = parse(child)

            check = checkTime(dt)
            if check:
                count += 1

    if count > 20:

        for i in range(1, 3):
            req_url = url + str(i)
            req = requests.get(
                req_url)
            soup = BeautifulSoup(req.text, "html.parser")
            elements = soup.find_all('a', {"class": "theme-img"})

            for each in elements:
                ''''''''''
                head = {
                    "user-agent": 'Mozilla/5.0' "https://www.udemy.com/courses/search/?q=python&src=sac&kw=python",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                }
                new_url = "https://www.udemyfreebies.com/out/" + \
                    each["href"].split("/")[4]
                session = HTMLSession()
                req = requests.get(new_url)
                print(req.url)
                r = session.get(req.url, headers=head)
                r.html.render(timeout=100)
                child = r.html.find('span')
                print(child)
                '''
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

                new_url = "https://www.udemyfreebies.com/out/" + \
                    each["href"].split("/")[4]
                name = each["href"].split("/")[4].replace("-", " ").title()

                req = requests.get(new_url)
                Coupon = ""
                if "?couponCode=" in str(req.url):
                    Coupon = str(req.url.split('?couponCode=')[1])

                expiry = getExpiry(req.url, browser)
                if expiry is not None and Coupon != "":
                    print(expiry)
                    print(name)
                    print(Coupon)
                    print(req.url)
                    result = (expiry, name, Coupon, req.url)
                    courses.append(result)

    difference = datetime.now() - time_start
    print(f'total time taken {difference.total_seconds() / 60} minutes')
    for x in courses:
        print(x)

except Exception as e:
    print("here")
    tb = traceback.format_exc()
    print(tb)
