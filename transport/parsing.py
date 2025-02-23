from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import time
from pytz import timezone
from datetime import datetime as dt

import config

class Parser:
    def __init__(self, route, url=config.URL, time_sleep=config.PARSER_TIME_SLEEP, direction=0):
        self.URL = url
        self.ROUTE = route
        self.TIMESLEEP = time_sleep
        self.DIRECTION = direction

    def create_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        return webdriver.Chrome(chrome_options)

    def find_checkpoints(self, driver, by_name=''):
        stops_areas = driver.find_elements(By.CLASS_NAME,
                                            "schedule-results-container-row-primary-true")
        res = []

        for area in stops_areas:
            if by_name != '':
                if area.find_element(By.CLASS_NAME, "checkpoint-title").text == by_name:
                        res.append(area)
            else:
                res.append(area)
        return res

class Schedule(Parser):
    def __init__(self, route, stop_name, url=config.URL, direction=0, time_sleep=5):
        super().__init__(route, url=url, time_sleep=time_sleep, direction=direction)
        self.STOP_NAME = stop_name

    def parse_schedule(self):
        driver = super().create_driver()
        result = []

        try:
            # Открытие страницы
            driver.get(self.URL)

            time.sleep(self.TIMESLEEP)

            #Поиск маршрута
            route_input = driver.find_element(By.ID, "select2-routes-search-container")
            if not route_input:
                result.append(f'Маршрута {self.ROUTE} не существует!')
                return
            route_input.click()


            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "select2-results__option"))
            )

            routes = driver.find_elements(By.CLASS_NAME, "select2-results__option")
            for route in routes:
                if route.text == self.ROUTE:  # Ищем нужный маршрут
                    route.click()  # Нажимаем на найденный элемент
                    break

            #кнопка поиска
            submit_button = driver.find_element(By.ID, "get-schedules")
            submit_button.click()

            time.sleep(self.TIMESLEEP)
            finded = []

            #поиск остановки
            if self.DIRECTION <= 0:
                finded = super().find_checkpoints(driver, by_name=self.STOP_NAME)

            if self.DIRECTION >= 0:
                #поиск остановки в обратке
                if len(finded) == 0:
                    backward_button = driver.find_element(By.ID, "schedule-route-backward")
                    backward_button.click()
                    time.sleep(self.TIMESLEEP)
                    finded = super().find_checkpoints(driver, by_name=self.STOP_NAME)

            time.sleep(self.TIMESLEEP)

            if len(finded) > 0:
                #поиск времени
                schedule_items = finded[0].find_elements(By.CLASS_NAME,
                                                         "schedule-results-container-row-cell-disabled")
                big_type = finded[0].find_elements(By.CLASS_NAME,
                                                    "schedule-results-container-row-cell-last")
                for item in schedule_items:
                    size = 0
                    if item in big_type:
                        size = 3
                    else:
                        size = 2
                    result.append(ScheduleItemHandler(item.text, size))
            else:
                result.append(f'Остановка **{self.STOP_NAME}** для маршрута **№{self.ROUTE}** не найдена! Проверьте правильность написания.')
            return result
        finally:
            driver.quit()

class Checkpoints(Parser):
    def __init__(self, route, direction=0, url=config.URL, time_sleep=config.PARSER_TIME_SLEEP):
        super().__init__(route, url=url, time_sleep=time_sleep, direction=direction)

    def parse_checkpoints(self):
        driver = super().create_driver()
        result = []
        try:
            driver.get(self.URL)
            time.sleep(self.TIMESLEEP)

            # Поиск маршрута
            route_input = driver.find_element(By.ID, "select2-routes-search-container")
            if not route_input:
                result.append(f'Маршрута **{self.ROUTE}** не существует!')
                return
            route_input.click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "select2-results__option"))
            )

            routes = driver.find_elements(By.CLASS_NAME, "select2-results__option")
            for route in routes:
                if route.text == self.ROUTE:  # Ищем нужный маршрут
                    route.click()  # Нажимаем на найденный элемент
                    break

            # кнопка поиска
            submit_button = driver.find_element(By.ID, "get-schedules")
            submit_button.click()

            time.sleep(self.TIMESLEEP)
            checks = []

            # поиск остановки
            if self.DIRECTION <= 0:
                checks = super().find_checkpoints(driver)

            if self.DIRECTION >= 0:
                # поиск остановки в обратке
                if len(checks) == 0:
                    backward_button = driver.find_element(By.ID, "schedule-route-backward")
                    backward_button.click()
                    time.sleep(self.TIMESLEEP)
                    checks = super().find_checkpoints(driver)

            for check in checks:
                result.append(check.find_element(By.CLASS_NAME, "checkpoint-title").text)
            return result
        finally:
            driver.quit()

class ScheduleItemHandler:
    def __init__(self, time, size):
        try:
            self.TIME = dt.combine(dt.now(), dt.strptime(time, "%H:%M").time())
            self.SIZE = int(size)
        except:
            print('Не удалось выполнить перевод времени')
            return
    def getMessage(self):
        time = self.TIME
        stime = time.strftime('%H:%M')
        check = ''
        size = ''

        if self.isPassed(): check = '✅'
        else: check = '☑️'

        if self.SIZE == 1 : size = "🟩🟩"
        elif self.SIZE == 2: size = "🟩🟩🟩🟩"
        elif self.SIZE == 3: size = "🟩🟩⬛️🟩🟩🟩"
        else: size = "Размер неизвестен."

        return f'{stime} {check} | {size}'
    def isPassed(self):
        if self.TIME < dt.now(): return True
        else: return False

if __name__ == '__main__':
    Schedule("10", "Автовокзал", time_sleep=1).parse_schedule()