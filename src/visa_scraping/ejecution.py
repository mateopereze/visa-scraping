import os
import re
import time
import json
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup

class VisaAppointmentChecker:
    def __init__(self, driver_path, username, password, months_to_extract=30):
        self.driver_path = driver_path
        self.username = username
        self.password = password
        self.months_to_extract = months_to_extract
        self.all_dates = []
        self.edge_options = Options()

    def setup_driver(self):
        # self.edge_options.add_argument("--headless")  # Run Edge in headless mode
        self.edge_options.add_argument("--disable-gpu")  # Disable GPU (optional but recommended)
        # self.edge_options.add_argument("--no-sandbox")  # Bypass OS security model (necessary in some CI environments)
        # self.edge_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource issues
        
        service = Service()
        driver = webdriver.Edge(service=service, options=self.edge_options)
        return driver

    def login(self, driver):
        try:
            driver.get('https://ais.usvisa-info.com/es-co/niv/users/sign_in')
            WebDriverWait(driver, 60).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            print("La página se ha cargado completamente.")

            # Intentar encontrar los campos y botones
            username_field = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'user_email')))
            password_field = driver.find_element(By.ID, 'user_password')
            checkbox = driver.find_element(By.XPATH, '//*[@id="sign_in_form"]/div[3]/label/div')
            login_button = driver.find_element(By.XPATH, '//*[@id="sign_in_form"]/p[1]/input')
            print("Identificados elementos para el logeo.")

            # Llenar los campos y hacer clic en los elementos
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            checkbox.click()
            login_button.click()

        except TimeoutException as e:
            print("TimeoutException: El tiempo de espera para cargar la página o los elementos ha expirado.")
            print(str(e))

        except NoSuchElementException as e:
            print("NoSuchElementException: No se ha encontrado uno de los elementos en la página.")
            print(str(e))

        except WebDriverException as e:
            print("WebDriverException: Ocurrió un error con el WebDriver.")
            print(str(e))

        except Exception as e:
            print("Error inesperado durante el login.")
            print(str(e))


    def get_appointment_date(self, driver):
        continue_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div[2]/div[2]/div[1]/div/div/div[1]/div[2]/ul/li/a'))
        )
        appointment_text = driver.find_element(By.CLASS_NAME, 'consular-appt').text

        # Map Spanish month names to English
        month_mapping = {
            'enero': 'January',
            'febrero': 'February',
            'marzo': 'March',
            'abril': 'April',
            'mayo': 'May',
            'junio': 'June',
            'julio': 'July',
            'agosto': 'August',
            'septiembre': 'September',
            'octubre': 'October',
            'noviembre': 'November',
            'diciembre': 'December'
        }

        # Extract the date using regex
        date_match = re.search(r'(\d{1,2}) (\w+), (\d{4})', appointment_text)
        if date_match:
            day = date_match.group(1)
            month = date_match.group(2).lower()
            year = date_match.group(3)
            month_english = month_mapping.get(month, 'Invalid month')

            appointment_date = datetime.strptime(f"{day} {month_english} {year}", '%d %B %Y')
            continue_button.click()

            return appointment_date
        else:
            raise ValueError("Could not extract appointment date.")

    def reschedule(self, driver):
        reschedule_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'fa-calendar-minus'))
        )
        reschedule_button.click()

        reschedule_confirm_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@class="button small primary small-only-expanded" and text()="Reprogramar cita"]'))
        )
        reschedule_confirm_button.click()

        calendary_button = WebDriverWait(driver, 60).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="appointments_consulate_appointment_date"]'))
        )
        calendary_button.click()

    def extract_dates(self, driver):
        for _ in range(self.months_to_extract):
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            calendar_groups = soup.find_all("div", class_="ui-datepicker-group")

            for group in calendar_groups:
                month = group.find("span", class_="ui-datepicker-month").text
                year = group.find("span", class_="ui-datepicker-year").text
                calendar = group.find("table", class_="ui-datepicker-calendar")
                days = calendar.find_all("td")

                for day in days:
                    is_selectable = "ui-datepicker-unselectable" not in day['class']
                    is_disabled = "ui-state-disabled" in day['class']

                    if day.text and "ui-datepicker-other-month" not in day['class']:
                        date_info = {
                            'day': day.text.strip(),
                            'month': month,
                            'year': year,
                            'is_selectable': is_selectable,
                            'is_disabled': is_disabled
                        }
                        self.all_dates.append(date_info)

            next_button = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@title='Next']"))
            )
            next_button.click()

    def log_results(self, appointment_date):
        df_dates = pd.DataFrame(self.all_dates)
        df_filtered = df_dates[~df_dates['is_disabled']].head(1)

        filtered_day = df_filtered['day'].values[0]
        filtered_month = df_filtered['month'].values[0]
        filtered_year = df_filtered['year'].values[0]
        filtered_date = datetime.strptime(f"{filtered_day} {filtered_month} {filtered_year}", '%d %B %Y')

        if filtered_date < appointment_date:
            execution_time = datetime.now()
            df_log = pd.DataFrame({
                'execution_time': [execution_time],
                'appointment_date': [appointment_date],
                'available_date': [filtered_date]
            })

            # filename = execution_time.strftime("%Y%m%d_%H%M%S") + "_execution_log.csv"
            # df_log.to_csv(f'./outputs/{filename}', index=False)
            row = df_log.iloc[0]

            # Print each value
            print(f"Execution Time: {row['execution_time']}")
            print(f"Appointment Date: {row['appointment_date']}")
            print(f"Available Date: {row['available_date']}")
            print(f"Log saved to {filename}")
        else:
            print("No earlier appointment available.")

    def run(self):
        driver = self.setup_driver()
        print('pass 000')
        try:
            self.login(driver)
            print('pass 001')
            appointment_date = self.get_appointment_date(driver)
            print('pass 002')
            self.reschedule(driver)
            print('pass 003')
            self.extract_dates(driver)
            print('pass 004')
            self.log_results(appointment_date)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            driver.quit()


if __name__ == "__main__":
    # Read global parameters from config.json
    with open('./src/visa_scraping/static/config.json', 'r') as config_file:
        config = json.load(config_file)

    # Asign values from config
    # # Using GitHub secrets and variables
    username_visa = os.getenv("USERNAME")
    password_visa = os.getenv("PASSWORD")
    # # In local
    # username_visa = config['global']['user']
    # password_visa = config['global']['password']
    driver_path = config['global']['driver_path']

    # Create an instance of the class and run it
    checker = VisaAppointmentChecker(driver_path, username_visa, password_visa)
    checker.run()