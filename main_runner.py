from logic.logic import *
from logic.utils import *
from multiprocessing import Process, Manager
from nicegui import ui
import threading
from threading import Thread
from pyrvsignal import Signal
import os
logicRunnerArr = []

datazz = None


class runner:
    def __init__(self) -> None:
        self.value = True


running = runner()


@app.get('/download')
def download():
    return FileResponse('downloaded/test.csv', headers={'Content-Disposition': 'attachment; filename=response.csv'})


class MyThread(Thread):
    started = Signal()
    finished = Signal()

    def __init__(self, target, args):
        self.target = target
        self.args = args
        Thread.__init__(self)

    def run(self) -> None:
        self.started.emit()
        self.target(*self.args)
        self.finished.emit()


coursesResult = []

settings = {}


def finishedWork():
    print("started")
    for i in logicRunnerArr:
        if i.done:
            coursesResult.extend(i.courses)
            logicRunnerArr.remove(i)
            new_maxCourses = settings['maxCourses'] - len(coursesResult)
            if len(coursesResult) >= settings['maxCourses']:
                for j in logicRunnerArr:
                    j.interupt = True
            else:
                count_collected = 0
                for m in logicRunnerArr:
                    count_collected += len(m.courses)
                if count_collected > new_maxCourses:
                    for j in logicRunnerArr:
                        j.interupt = True
                else:
                    for j in logicRunnerArr:
                        j.max_courses = new_maxCourses

    if len(logicRunnerArr) == 0:
        # print(coursesResult)
        log.push("Converting to CSV")
        toCSV(coursesResult[:settings['maxCourses']])
        log.push("Data updated , you can download the new courses via the link below")
        running.value = True
        threads = []
        datazz.bind_visibility_from(running, 'value')


def save_settings():

    settings["uf"] = checkbox1.value
    settings["rd"] = checkbox2.value
    settings["du"] = checkbox3.value
    if text1.value != None and int(text1.value) == text1.value and int(text1.value) > 0:
        settings["pages1"] = int(text1.value)
    else:
        log.push("Error with freebies number of pages , using default")
        settings["pages1"] = 3
    if text2.value != None and int(text2.value) == text2.value and int(text2.value) > 0:
        settings["pages2"] = int(text2.value)
    else:
        log.push("Error with realdiscount number of pages , using default")
        settings["pages2"] = 40
    if text3.value != None and int(text3.value) == text3.value and int(text3.value) > 0:
        settings["pages3"] = int(text3.value)
    else:
        log.push("Error with discudemy number of pages , using default")
        settings["pages3"] = 3
    if text4.value != None and int(text4.value) == text4.value and int(text4.value) > 0:
        settings["maxCourses"] = int(text4.value)
    else:
        log.push("Error with maxCourses number , using default")
        settings["maxCourses"] = 200
    if text5.value != None and int(text5.value) == text5.value and int(text5.value) > 0:
        settings["NoOlderThan"] = int(text5.value)
    else:
        log.push("Error with NoOlderThan number , using default")
        settings["NoOlderThan"] = 2
    if text6.value != None and int(text6.value) == text6.value and int(text6.value) > 0:
        settings['maxretries'] = int(text6.value)
    else:
        log.push("Error with max-retries number , using default")
        settings["maxretries"] = 1

    # print(settings)
    log.push(
        f"Starting Script with settings (udemyfreebies.com: ({checkbox1.value}, number of pages: {int(settings['pages1'])}), real.discount: ({checkbox2.value}, number of pages: {settings['pages2']}), discudemy.com: ({checkbox3.value}, number of pages: {settings['pages3']}), max-courses: {settings['maxCourses']}, Courses not older than: {settings['NoOlderThan']}, max-retries: {settings['maxretries']})")
    if settings["uf"]:
        lo = logic(placeholder="uf", logger=log,
                   pages=settings["pages1"], noOlder=settings['NoOlderThan'], max_courses=settings['maxCourses'], max_retries=settings['maxretries'])
        logicRunnerArr.append(lo)
    if settings["rd"]:
        lo = logic(placeholder="rd", logger=log,
                   pages=settings["pages2"], noOlder=settings['NoOlderThan'], max_courses=settings['maxCourses'], max_retries=settings['maxretries'])
        logicRunnerArr.append(lo)
    if settings["du"]:
        lo = logic(placeholder="du", logger=log,
                   pages=settings["pages3"], noOlder=settings['NoOlderThan'], max_courses=settings['maxCourses'], max_retries=settings['maxretries'])
        logicRunnerArr.append(lo)

    for i in logicRunnerArr:

        p = MyThread(target=i.wrapper, args=())
        p.finished.connect(finishedWork)
        p.start()
    # t1 = threading.Thread(target=doSomething)
    # t2 = threading.Thread(target=doSomething)
    # i = logic("uf", log)
    # t3 = threading.Thread(target=i.wrapper, args=(L,))
    # t1.start()
    # t2.start()
    # t3.start()

    log.push("hello")


def runMethod():
    running.value = False

    datazz.bind_visibility_from(running, 'value')
    save_settings()

    # if settings["uf"]:
    #     lo = logic(placeholder="uf")
    #     logicRunnerArr.append(lo)
    # if settings["rd"]:
    #     lo = logic(placeholder="rd")
    #     logicRunnerArr.append(lo)
    # if settings["du"]:
    #     lo = logic(placeholder="du")
    #     logicRunnerArr.append(lo)

    with Manager() as manager:
        L = manager.list()  # <-- can be shared between processes.
        processes = []
        # for i in logicRunnerArr:
        #     p = threading.Thread(target=i.wrapper, args=(L,))

        #     processes.append(p)
        # for i in range(0, 3):
        #     p = Process(target=logic.wrapper, args=(logicRunnerArr[i], L, i))
        #     processes.append(p)
        # p = Process(target=logic.wrapper, args=(
        #     logicRunner, L, 0))
        # p2 = Process(target=logic.wrapper, args=(
        #     logicRunner2, L, 1))
        # # Passing the list
        # p3 = Process(target=logic.wrapper, args=(
        #     logicRunner3, L, 2))

        # processes.append(p)
        # processes.append(p2)
        # processes.append(p3)
        # for j in processes:
        #     j.start()
        # print("got here")
        # while len(L) < 300:
        #     print(len(L))
        #     # log.push("doing some work")
        # print(L)
        # print("Converting to CSV")
        # p_list = list(L)
        # toCSV(p_list)


with ui.header().classes('justify-center items-center'):
    ui.label("Welcome to Udemy Scraper")

with ui.column().props('inline color=black').classes('absolute-center justify-center items-center w-full'):
    log = ui.log().classes('w-full h-96')

    with ui.row():
        with ui.column().classes('content-center justify-center items-center'):
            checkbox1 = ui.checkbox('www.udemyfreebies.com')
            text1 = ui.number(label='Number of pages',
                              placeholder='default is 3', validation={'Wrong Entry': lambda value: int(value) > 0, 'Fractions are not allowed': lambda value: int(value) == value})
        with ui.column().classes('content-center justify-center items-center'):
            checkbox2 = ui.checkbox('www.real.discount')
            text2 = ui.number(label='Number of pages',
                              placeholder='default is 40', validation={'Wrong Entry': lambda value: int(value) > 0, 'Fractions are not allowed': lambda value: int(value) == value})
        with ui.column().classes('content-center justify-center items-center'):
            checkbox3 = ui.checkbox('www.discudemy.com')
            text3 = ui.number(label='Number of pages',
                              placeholder='default is 3', validation={'Wrong Entry': lambda value: int(value) > 0, 'Fractions are not allowed': lambda value: int(value) == value})
    text4 = ui.number(label='Max No of courses',
                      placeholder='200', validation={'Wrong Entry': lambda value: int(value) > 0, 'Fractions are not allowed': lambda value: int(value) == value}).classes('w-64 text-center')
    text5 = ui.number(label='Dont include older than ... days',
                      placeholder='2', validation={'Wrong Entry': lambda value: int(value) > 0, 'Fractions are not allowed': lambda value: int(value) == value}).classes('w-64 text-center')
    text6 = ui.number(label='Max Retries',
                      placeholder='1', validation={'Wrong Entry': lambda value: int(value) > 0, 'Fractions are not allowed': lambda value: int(value) == value}).classes('w-64 text-center')
    result = ui.label()
    ui.link('Download precollected courses , or press after collection is done for new ones', '/download')
    datazz = ui.button('Start Process', on_click=runMethod)
    datazz.bind_visibility_from(running, 'value')


if __name__ in {"__main__", "__mp_main__"}:

    ui.run(uvicorn_reload_includes='*.py, *.css, *.html')
    # time_start = datetime.now()

    # difference = datetime.now() - time_start
    # print(f'total time taken {difference.total_seconds() / 60} minutes')
