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
    def __init__(self, driver_path, username, password,  sender_email, password_email, recipient_email, months_to_extract=30):
        self.driver_path = driver_path
        self.username = username
        self.password = password
        self.sender_email = sender_email
        self.password_email = password_email
        self.recipient_email = recipient_email
        self.months_to_extract = months_to_extract
        self.all_dates = []
        self.edge_options = Options()

    def setup_driver(self):
        self.edge_options.add_argument('--headless')  # Modo sin interfaz gráfica
        self.edge_options.add_argument('--no-sandbox')  # Necesario en entornos CI
        self.edge_options.add_argument('--disable-dev-shm-usage')  # Reduce problemas de memoria compartida
        self.edge_options.add_argument('--disable-gpu')  # Asegura compatibilidad en headless mode
        self.edge_options.add_argument('--disable-blink-features=AutomationControlled')  # Evitar detección
        self.edge_options.add_argument('--disable-extensions')
        self.edge_options.add_experimental_option('useAutomationExtension', False)
        self.edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.edge_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36")
        
        service = Service()
        driver = webdriver.Edge(service=service, options=self.edge_options)
        return driver

    def login(self, driver):
        try:
            driver.get('https://ais.usvisa-info.com/es-co/niv/users/sign_in')
            WebDriverWait(driver, 180).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            print("La página se ha cargado completamente.")

            # Intentar encontrar los campos y botones con visibilidad asegurada
            username_field = WebDriverWait(driver, 180).until(EC.visibility_of_element_located((By.ID, 'user_email')))
            password_field = WebDriverWait(driver, 180).until(EC.visibility_of_element_located((By.ID, 'user_password')))
            checkbox = WebDriverWait(driver, 180).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="sign_in_form"]/div[3]/label/div')))
            login_button = WebDriverWait(driver, 180).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="sign_in_form"]/p[1]/input')))
            print("Identificados elementos para el logeo.")

            # Llenar los campos y hacer clic en los elementos
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            checkbox.click()
            login_button.click()

            # Esperar por un momento para asegurar que la siguiente página cargue (si es necesario)
            time.sleep(3)  # Pausa para verificar si la siguiente página se carga correctamente

        except TimeoutException as e:
            print("TimeoutException: El tiempo de espera para cargar la página o los elementos ha expirado.")
            print(f"Página fuente cuando ocurrió el error: {driver.page_source}")
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

            # log_file_path = './outputs/execution_log.csv'
            # # Check if log file exists
            # if not os.path.exists(log_file_path):
            #     # Create a new log file with headers
            #     pd.DataFrame([new_log_entry]).to_csv(log_file_path, index=False)
            #     print(f"Log file created and saved at: {log_file_path}")
            # else:
            #     # Append the new entry to the existing log file
            #     pd.DataFrame([new_log_entry]).to_csv(log_file_path, mode='a', header=False, index=False)
            #     print(f"New log entry appended to: {log_file_path}")

            # Print the details of the logged entry
            print(f"Execution Time: {execution_time}")
            print(f"Appointment Date: {appointment_date}")
            print(f"Available Date: {available_date}")

            # Send an email notification
            if recipient_email:
                send_email_notification(
                    execution_time,
                    appointment_date,
                    filtered_date
                )

        else:
            print("No earlier appointment available.")

    def send_email_notification(execution_time, appointment_date, available_date):
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # Create the email content
        subject = "New Appointment Available"
        body = (
            f"Hello,\n\n"
            f"A new earlier appointment is available:\n\n"
            f"Execution Time: {execution_time}\n"
            f"Current Appointment Date: {appointment_date}\n"
            f"Available Appointment Date: {available_date}\n\n"
            f"Please log in to your account to book this appointment."
        )

        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print(f"Email sent to {recipient_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def run(self):
        driver = self.setup_driver()
        try:
            self.login(driver)
            appointment_date = self.get_appointment_date(driver)
            self.reschedule(driver)
            self.extract_dates(driver)
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

    sender_email = os.getenv("SENDER_EMAIL")
    password_email = os.getenv("PASSWORD_EMAIL")

    recipient_email = os.getenv("RECIPIENT_EMAIL")

    # # In local
    # username_visa = config['global']['user']
    # password_visa = config['global']['password']
    driver_path = config['global']['driver_path']

    # Create an instance of the class and run it
    checker = VisaAppointmentChecker(driver_path, username_visa, password_visa, sender_email, password_email, recipient_email)
    checker.run()