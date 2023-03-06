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
from multiprocessing import Process, Manager
from multiprocessing.managers import ListProxy


class logic:
    def __init__(self, placeholder, logger, max_retries, max_courses, pages, noOlder):
        super().__init__()
        self.placeHolder = placeholder
        self.logger = logger
        self.courses = []
        self.done = False
        self.max_retries = max_retries
        self.max_older = 0
        self.pages = pages
        self.noOlder = (datetime.now() - timedelta(days=noOlder)).date()

        self.rlpages = pages
        self.interupt = False
        self.max_courses = max_courses

    def getExpiry(self, url, browser):

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
            # self.logger.push("there")
            # self.logger.push(str(e))
            return None
        finally:
            pass

    def checkTime(self, date):
        threedaysThreshold = datetime.now() - timedelta(days=3)
        if date >= threedaysThreshold:
            return True
        else:
            return False
    # DU REGION START

    def checkPrevious(self, url: str, pages: int, head):
        count = 0
        for i in range(1, pages):
            try:
                r = requests.get(url + str(i), headers=head, verify=False)
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
                            check = self.checkTime(date=dt)
                            if check:
                                count += 1
                            continue
            except:
                pass
        return count

    def getInfoDU(self, url: str, pages: int, courses: list):
        # adding comment
        head = {
            "user-agent": 'Mozilla/5.0' "https://www.udemy.com/courses/search/?q=python&src=sac&kw=python",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        }
        while self.interupt != True:
            if self.interupt:
                break
            for i in range(1, pages):
                if i+1 >= pages:
                    self.interupt = True
                elif len(self.courses) >= self.max_courses:
                    self.interupt = True
                if self.interupt:
                    break
                try:
                    self.logger.push(f"Scrapping page{str(i)} for courses")
                    r = requests.get(
                        "https://www.discudemy.com/all/" + str(i), headers=head, verify=False)
                    soup = BeautifulSoup(r.content, features="html.parser")
                    elements = soup.find_all('a', {"class": "card-header"})
                    self.logger.push(
                        f"Scrapping is done , extracting courses info from page{i}")

                    for each in elements:
                        if len(self.courses) >= self.max_courses:
                            self.interupt = True
                        if self.interupt:
                            self.done = True
                            break
                        j = 0
                        while j < self.max_retries:
                            if len(self.courses) >= self.max_courses:
                                self.interupt = True
                            if self.interupt:
                                self.done = True
                                break
                            try:

                                user_agent = 'Mozilla/5.0' "https://www.udemy.com/courses/search/?q=python&src=sac&kw=python"
                                Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
                                options = webdriver.FirefoxOptions()
                                options.add_argument(
                                    f'user-agent={user_agent}')
                                options.add_argument(f'Accept={Accept}')
                                options.add_argument('--no-sandbox')
                                options.add_argument('--window-size=1920,1080')
                                options.add_argument('--headless')
                                options.add_argument('--disable-gpu')
                                options.add_argument(
                                    '--allow-running-insecure-content')
                                options.add_argument("--headless")
                                # options.add_argument('--disable-logging')
                                options.binary_location = r'/usr/bin/firefox'

                                browser = webdriver.Firefox(options=options)
                                name = each.text
                                self.logger.push(
                                    f"Found a course on discudemy.com")
                                self.logger.push(f"Attempting Extraction")
                                go_url = each["href"].split('/')[4]
                                req = requests.get(
                                    f"https://www.discudemy.com/go/{go_url},", headers=head)
                                temp_soup = BeautifulSoup(
                                    req.content, features="html.parser")
                                coupon_elem = temp_soup.find(
                                    'a', {"id": "couponLink"})
                                Coupon = ""
                                if "?couponCode=" in str(coupon_elem["href"]):
                                    Coupon = str(
                                        coupon_elem["href"].split('?couponCode=')[1])
                                expiry = self.getExpiry(
                                    coupon_elem["href"], browser)
                                if expiry is not None and Coupon != "":
                                    # self.logger.push(expiry)
                                    # self.logger.push(name)
                                    # self.logger.push(Coupon)
                                    # self.logger.push(coupon_elem["href"])
                                    if "days" in expiry:
                                        number = str(expiry).split(' ')[0]
                                        date = (datetime.now() +
                                                timedelta(days=int(number))).date()
                                        expiry = date
                                    elif "hours" in expiry:
                                        number = str(expiry).split(' ')[0]
                                        date = (datetime.now() +
                                                timedelta(hours=int(number))).date()
                                        expiry = date
                                    if expiry < self.noOlder:
                                        j = self.max_retries
                                        self.logger.push(
                                            f"Course older than constraint , moving on...")
                                        continue
                                    else:

                                        self.logger.push(
                                            f"Info Extracted, Course added to CSV")
                                        result = (
                                            name, coupon_elem["href"], Coupon, expiry)

                                        courses.append(result)

                                else:
                                    self.logger.push(
                                        f"Course Expired, Moving On...")
                                    j = self.max_retries
                            except:
                                if j+1 >= self.max_retries:
                                    self.logger.push(
                                        f"Error Occured , Skipping after attempting all retries")
                                    j = self.max_retries
                                else:
                                    self.logger.push(
                                        f"Error Occured, Retrying Attempt {j} of {self.max_retries}")
                                    j += 1
                except:
                    pass
        self.done = True

    def ProcessDU(self, course: list):
        head = {
            "user-agent": 'Mozilla/5.0' "https://www.udemy.com/courses/search/?q=python&src=sac&kw=python",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        }
        self.logger.push("Checking 20 Courses Constraint on discudemy")
        count = self.checkPrevious(
            "https://www.discudemy.com/all/", self.pages, head=head)
        if count > 20:
            self.logger.push("Passed, Moving On")
            self.getInfoDU(
                "https://www.discudemy.com/all/", self.pages, course)
        else:
            self.logger.push(
                "No Courses posted for the last 72 hours , skipping")
            self.done = True

    # DU REGIOU END

    # RL REGION START

    def filterList(self, results):
        courses = []
        for i in results:
            if str(i["url"]).startswith("https://www.udemy.com/") and i["sale_end"] is not None:
                courses.append(i)
        return courses

    def check20Courses(self, results):
        count = 0
        for i in results:
            if str(i["url"]).startswith("https://www.udemy.com/"):
                dt = parse(i['sale_start'])
                if datetime.now().month == dt.month and datetime.now().day - dt.day <= 3:
                    count += 1

        return count

    def extractInfo(self, filtered_list: list, courses: list):
        self.logger.push("Scanning real.discount for courses")
        while self.interupt != True:
            for i in filtered_list:
                # re = requests.get(i["url"])

                if filtered_list.index(i) == len(filtered_list) - 1:
                    self.interupt = True
                elif len(self.courses) >= self.max_courses:
                    self.interupt = True
                if self.interupt:
                    self.done = True
                    break
                j = 0
                while j < self.max_retries:

                    try:
                        if i["isexpired"] != "Available":
                            j = self.max_retries

                            break
                        else:
                            name = i["name"]
                            Coupon = ""
                            if "?couponCode=" in str(i["url"]):
                                Coupon = str(i["url"].split('?couponCode=')[1])
                            expiry = parse(i["sale_end"]).date()
                            if expiry == datetime.now().date() or expiry < datetime.now().date() or expiry < self.noOlder:
                                j = self.max_retries

                                break
                            else:
                                url = i["url"]
                                if Coupon != "":
                                    result = (name, url, Coupon, expiry)
                                    self.logger.push(
                                        f"Found Course at real.discount")
                                    self.logger.push(
                                        "Checking if course is free")

                                    courses.append(result)
                                    j = self.max_retries

                                    self.logger.push(
                                        "Course from real.discount is free and added to csv")
                                    break
                    except:

                        if (j+1) >= self.max_retries:
                            self.logger.push(
                                "Error Occured,Course is not availabe for free anymore")
                            break
                        else:
                            self.logger.push(
                                "Error Occured, Most Probably Course is not availabe for free anymore... retrying")
                            j += 1

        self.logger.push(f"Found {len(self.courses)} free on real.discount")
        self.done = True

    def processRL(self, courses: list):
        try:

            filtered_list = []
            r = requests.get(
                f"https://www.real.discount/api-web/all-courses/?store=Udemy&page=1&per_page={self.rlpages}&orderby=date&free=1&editorschoices=0", headers={
                    "User-Agent": "PostmanRuntime/7.30.0",
                    "Host": "www.real.discount",
                    "Connection": "Keep-Alive",
                }, timeout=10).json()

            filtered_list = self.filterList(r['results'])
            filtered_list.sort(key=lambda x: x['sale_start'], reverse=True)
            count = self.check20Courses(filtered_list)
            if count > 20:
                self.extractInfo(filtered_list, courses)

        except Exception as e:
            self.logger.push("Error with remote host")

    # RL REGION END

    # UF REGION START
    def ProcessUF(self, courses: list):
        url = "https://www.udemyfreebies.com/free-udemy-courses/"
        # self.logger.push(req.text)
        head = {
            "user-agent": 'Mozilla/5.0' "https://www.udemy.com/courses/search/?q=python&src=sac&kw=python",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        }
        try:
            count = 0
            self.logger.push(
                "Scrapping udemyfreebies for available courses")
            for i in range(1, self.pages):
                try:
                    req_url = url + str(i)
                    req = requests.get(
                        req_url, verify=False, headers=head)
                    self.logger.push(str(req.status_code))
                    soup = BeautifulSoup(req.text, "html.parser")
                    elements = soup.find_all('div', {"class": "theme-block"})
                    # check if 20 coupons were posted within 72 hours
                    for each in elements:
                        child = each.find(['small']).text
                        dt = parse(child)

                        check = self.checkTime(dt)
                        if check:
                            count += 1
                except:
                    tb = traceback.format_exc()
                    self.logger.push(tb)
            self.logger.push(
                "Scrapping done , Checking if there are 20 courses in the past 72 hours")

            if count > 20:
                while self.interupt != True:
                    self.logger.push("count is sufficient, continuing")
                    if self.interupt:
                        break
                    for i in range(1, self.pages):
                        if i+1 >= self.pages:
                            self.interupt = True
                        elif len(self.courses) >= self.max_courses:
                            self.interupt = True
                        if self.interupt:
                            self.done = True
                            break
                        self.logger.push(f"Scrapping page{str(i)} for courses")
                        req_url = url + str(i)
                        req = requests.get(
                            req_url, headers=head, verify=False)
                        soup = BeautifulSoup(req.text, "html.parser")
                        elements = soup.find_all('a', {"class": "theme-img"})
                        self.logger.push(
                            f"Successfully scrapped page{str(i)} for courses")
                        self.logger.push(
                            f"Extracting Courses info in page {str(i)}")
                        for each in elements:
                            if len(self.courses) >= self.max_courses:
                                self.interupt = True
                            if self.interupt:
                                self.done = True
                                break
                            j = 0
                            while j < self.max_retries:
                                ''''''''''
                                head = {
                                    "user-agent": 'Mozilla/5.0' "https://www.udemy.com/courses/search/?q=python&src=sac&kw=python",
                                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                                }
                                new_url = "https://www.udemyfreebies.com/out/" + \
                                    each["href"].split("/")[4]
                                session = HTMLSession()
                                req = requests.get(new_url)
                                self.logger.push(req.url)
                                r = session.get(req.url, headers=head)
                                r.html.render(timeout=100)
                                child = r.html.find('span')
                                self.logger.push(child)
                                '''
                                user_agent = 'Mozilla/5.0' "https://www.udemy.com/courses/search/?q=python&src=sac&kw=python"
                                Accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
                                options = webdriver.FirefoxOptions()
                                options.add_argument(
                                    f'user-agent={user_agent}')
                                options.add_argument(f'Accept={Accept}')
                                options.add_argument('--no-sandbox')
                                options.add_argument('--window-size=1920,1080')
                                options.add_argument('--headless')
                                options.add_argument('--disable-gpu')
                                options.add_argument(
                                    '--allow-running-insecure-content')
                                options.add_argument("--headless")
                                # options.add_argument('--disable-logging')
                                options.binary_location = r'/usr/bin/firefox'

                                browser = webdriver.Firefox(options=options)

                                new_url = "https://www.udemyfreebies.com/out/" + \
                                    each["href"].split("/")[4]
                                name = each["href"].split(
                                    "/")[4].replace("-", " ").title()

                                req = requests.get(
                                    new_url, headers=head, verify=False)
                                Coupon = ""
                                if "?couponCode=" in str(req.url):
                                    Coupon = str(
                                        req.url.split('?couponCode=')[1])
                                self.logger.push(
                                    "Found Course at udemyfreebies.com")
                                self.logger.push("Checking Expiry")
                                expiry = self.getExpiry(req.url, browser)

                                if expiry is not None and Coupon != "":
                                    if "days" in expiry:
                                        number = str(expiry).split(' ')[0]
                                        date = (datetime.now() +
                                                timedelta(days=int(number))).date()
                                        expiry = date
                                    elif "hours" in expiry:
                                        number = str(expiry).split(' ')[0]
                                        date = (datetime.now() +
                                                timedelta(hours=int(number))).date()
                                        expiry = date
                                    # self.logger.push(expiry)
                                    # self.logger.push(name)
                                    # self.logger.push(Coupon)
                                    # self.logger.push(req.url)
                                    if expiry < self.noOlder:
                                        j = self.max_retries
                                        self.logger.push(
                                            "Course is older than constraint , moving on....")
                                        continue
                                    else:
                                        result = (name, req.url,
                                                  Coupon, expiry)
                                        courses.append(result)
                                        self.logger.push(
                                            "Course is valid , Added to CSV QUEUE")
                                        j = self.max_retries
                                else:
                                    self.logger.push("Course is expired")
                                    j = self.max_retries

            # for x in courses:
            #     self.logger.push(x)
            else:
                self.logger.push("Count is not enough")
            self.done = True

        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            self.logger.push("Error Occured in freebies course, retrying...")

    def wrapper(self):
        if self.placeHolder == "rd":
            # self.logger.push("process RL Start")
            self.processRL(self.courses)

        elif self.placeHolder == "du":
            # self.logger.push("Process DU Started")
            self.ProcessDU(self.courses)

        else:
            # self.logger.push("Process UF Started")
            self.ProcessUF(self.courses)
