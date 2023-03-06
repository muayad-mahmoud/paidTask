import pandas as pd
from nicegui import app, ui
from fastapi.responses import FileResponse


def toCSV(results: list):
    df = pd.DataFrame(results)
    df.columns = ['Course Name',
                  'Course URL', 'Coupon Code', 'Expiration Date']
    df.to_csv("downloaded/test.csv", encoding='utf-8-sig')
