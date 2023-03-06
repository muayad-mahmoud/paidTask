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
from operator import itemgetter

headers = {
    "User-Agent": "PostmanRuntime/7.30.0",
    "Host": "www.real.discount",
    "Connection": "Keep-Alive",
}


def filterList(results):
    courses = []
    for i in results:
        if str(i["url"]).startswith("https://www.udemy.com/") and i["sale_end"] is not None:
            courses.append(i)
    return courses


def check20Courses(results):
    count = 0
    for i in results:
        if str(i["url"]).startswith("https://www.udemy.com/"):
            dt = parse(i['sale_start'])
            if datetime.now().month == dt.month and datetime.now().day - dt.day <= 3:
                count += 1

    return count


def extractInfo(filtered_list):
    courses = []
    for i in filtered_list:
        # re = requests.get(i["url"])
        if i["isexpired"] != "Available":
            continue
        else:
            name = i["name"]
            Coupon = ""
            if "?couponCode=" in str(i["url"]):
                Coupon = str(i["url"].split('?couponCode=')[1])
            expiry = parse(i["sale_end"])
            url = i["url"]
            if Coupon != "":
                result = (expiry, name, Coupon, url)
                courses.append(result)
    return courses


try:
    pages = 400
    filtered_list = []
    r = requests.get(
        f"https://www.real.discount/api-web/all-courses/?store=Udemy&page=1&per_page={pages}&orderby=date&free=1&editorschoices=0", headers=headers, timeout=10).json()
    filtered_list = filterList(r['results'])
    filtered_list.sort(key=lambda x: x['sale_start'], reverse=True)
    count = check20Courses(filtered_list)
    if count > 20:
        result = extractInfo(filtered_list)
        for i in result:
            print(i)


except Exception as e:
    print("here")
    tb = traceback.format_exc()
    print(tb)
