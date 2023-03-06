from nicegui import ui
from multiprocessing import Process, Manager
import multiprocessing as mp
import threading


def doSomething():
    for i in range(100000):
        log.push(f"lol {str(i)}")


def save_settings():
    settings = {}
    t1 = threading.Thread(target=doSomething)
    t2 = threading.Thread(target=doSomething)
    t1.start()
    t2.start()
    settings["check1"] = checkbox1.value
    settings["check2"] = checkbox2.value
    settings["check3"] = checkbox3.value
    settings["text1"] = text1.value
    settings["text2"] = text2.value
    settings["text3"] = text3.value
    settings["text4"] = text4.value
    settings["text5"] = text5.value

    return settings


with ui.header().classes('justify-center items-center'):
    ui.label("Welcome to Udemy Scraper")

with ui.column().props('inline color=black').classes('absolute-center justify-center items-center'):
    log = ui.log().classes('w-full h-96')
    with ui.row():
        with ui.column().classes('content-center justify-center items-center'):
            checkbox1 = ui.checkbox('www.udemyfreebies.com')
            text1 = ui.input(label='Number of retries',
                             placeholder='default is 0')
        with ui.column().classes('content-center justify-center items-center'):
            checkbox2 = ui.checkbox('www.real.discount')
            text2 = ui.input(label='Number of retries',
                             placeholder='default is 0')
        with ui.column().classes('content-center justify-center items-center'):
            checkbox3 = ui.checkbox('www.discudemy.com')
            text3 = ui.input(label='Number of retries',
                             placeholder='default is 0')
    text4 = ui.input(label='Max No of courses',
                     placeholder='200').classes('w-full')
    text5 = ui.input(label='Dont include older than',
                     placeholder='200').classes('w-full')
    result = ui.label()
    ui.button('Start Process', on_click=save_settings)

if __name__ in {"__main__", "__mp_main__"}:

    ui.run()
