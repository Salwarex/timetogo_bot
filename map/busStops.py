from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import time

import config


class ScheduleForCheckpoints:
    def __init__(self, url, route, stopname, direction=0):
        self.URL = url
        self.ROUTE = route
        self.STOPNAME = stopname
        self.DIRECTION = direction

    def find_checkpoints(self, driver):
        stops_areas = driver.find_elements(By.CLASS_NAME,
                                           "schedule-results-container-row-primary-true")
        res = []

        for area in stops_areas:
            if area.find_element(By.CLASS_NAME, "checkpoint-title").text == self.STOPNAME:
                res.append(area)
        return res

    def parse_schedule(self):
        #драйвер
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(chrome_options)

        try:
            # Открытие страницы
            driver.get(self.URL)

            time.sleep(5)

            #Поиск маршрута
            route_input = driver.find_element(By.ID, "select2-routes-search-container")
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

            time.sleep(5)
            #поиск остановки
            finded = self.find_checkpoints(driver)

            #поиск остановки в обратке
            if len(finded) == 0:
                backward_button = driver.find_element(By.ID, "schedule-route-backward")
                backward_button.click()
                time.sleep(5)
                finded = self.find_checkpoints(driver)

            time.sleep(5)

            #поиск остановок
            schedule_items = finded[0].find_elements(By.CLASS_NAME,
                                                     "schedule-results-container-row-cell-disabled")
            for item in schedule_items:
                print(item.text)
        finally:
            driver.quit()

if __name__ == '__main__':
    ScheduleForCheckpoints(config.URL, "", "").parse_schedule()