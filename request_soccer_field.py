import time
import argparse
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from pathlib import Path


DAYS_MAPPING = {
    'L': 0,
    'M': 1,
    'X': 2,
    'J': 3,
    'V': 4,
    'S': 5,
    'D': 6
}
EVENT_DURATION_IN_HOURS = 1
FORM_FIX_FIELDS = {
    "park": "Parque De La Familia",
    "activity": "Deportiva",
    "age_range": "Adultos (22 - 59)",
    "ethnicity": "Otra",
    "visit_frequency": "2 o más veces al año",
    "country": "Chile",
    "specific_place": "canchas de futbolito",
    "men_count": "6",
    "women_count": "6",
    "description": "Partido de futbolito mixto."
}
OUTPUT_DATE_FORMAT = "%Y/%m/%d %H:%M"


def get_requested_date(day: str, time: str, weeks_ahead: int) -> str:
    # Parse the time from the input (e.g., "14:30")
    hour, minute = map(int, time.split(":"))
    
    # Get today's date and the weekday number for today
    today = datetime.now()
    current_weekday = today.weekday()
    
    # Get the target weekday from the day map
    target_weekday = DAYS_MAPPING.get(day.upper())
    if target_weekday is None:
        raise ValueError("Invalid day code. Use one of 'L', 'M', 'X', 'J', 'V', 'S', or 'D'.")
    
    # Calculate days until the next occurrence of the target weekday
    days_until_target = (target_weekday - current_weekday + 7) % 7
    next_target_day = today + timedelta(days=days_until_target)
    
    # Set the hour and minute for the target time
    target_date = next_target_day.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # Add the specified number of weeks
    future_date = target_date + timedelta(weeks=weeks_ahead)
    
    # Format the date as "YYYY-MM-DD HH:MM"
    return future_date.strftime(OUTPUT_DATE_FORMAT)


def request_soccer_field(user_id, request_day, request_time,
                         weeks_ahead, participants_str, plan_str,
                         path_to_image, show_browser=False,
                         test=False):
    # path_to_geckodriver = "/home/robber/Downloads/geckodriver/geckodriver"
    path_to_geckodriver = "/usr/local/bin/geckodriver"

    # Set up Firefox options for headless mode
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.headless = False
    if not show_browser:
        firefox_options.add_argument("--headless")

    # Initialize the Firefox WebDriver with GeckoDriver
    service = Service(path_to_geckodriver)
    driver = webdriver.Firefox(
        service=service,
        options=firefox_options
    )

    try:
        # Navigate to the page
        driver.get("https://tpu.parquemet.cl/")  # Replace with your target URL

        # Fill the user ID field and submit the form (similar as before)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "EntidadeRut")))  # Adjust the selector if needed
        username_field = driver.find_element(
            By.ID,
            "EntidadeRut"
        )

        # Fill in the username
        username_field.send_keys(user_id)
        # password_field.send_keys("my_password")  # Replace with your actual password

        # Find the login button and click it
        login_button = driver.find_element(
            By.CSS_SELECTOR,
            ".btn.btn-primary.pull-right"
        )
        login_button.click()

        # Wait for the new form to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn.btn-primary")))

        # Find the new request button and click it
        new_request_button = driver.find_element(
            By.CSS_SELECTOR,
            ".btn.btn-primary"
        )
        new_request_button.click()

        # Fill park field
        park = Select(driver.find_element(
            By.ID,
            "SolicitudePurbanoId"
        ))
        park.select_by_visible_text(FORM_FIX_FIELDS.get("park"))
        # Fill activity
        activity = Select(driver.find_element(
            By.ID,
            "SolicitudeTipoSolicitudeId"
        ))
        activity.select_by_visible_text(FORM_FIX_FIELDS.get("activity"))
        # Fill dates
        requested_start_date = get_requested_date(
            request_day,
            request_time,
            weeks_ahead
        )
        requested_end_date = (datetime.strptime(
            requested_start_date,
            OUTPUT_DATE_FORMAT
        ) + timedelta(hours=EVENT_DURATION_IN_HOURS)).strftime(OUTPUT_DATE_FORMAT)
        start_date = WebDriverWait(driver, 0).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".form-control#datetimepicker_A"))
            )
        start_date.send_keys(requested_start_date)
        end_date = WebDriverWait(driver, 0).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".form-control#datetimepicker_B"))
            )
        end_date.send_keys(requested_end_date)
        # Fill age range
        age_range = Select(driver.find_element(
            By.ID,
            "SolicitudeEdadeId"
        ))
        age_range.select_by_visible_text(FORM_FIX_FIELDS.get("age_range"))
        # Fill ethnicity
        ethnicity = Select(driver.find_element(
            By.ID,
            "SolicitudeEtniaId"
        ))
        ethnicity.select_by_visible_text(FORM_FIX_FIELDS.get("ethnicity"))
        # Fill visit frequency
        visit_frequency = Select(driver.find_element(
            By.ID,
            "SolicitudeFrecuenciaId"
        ))
        visit_frequency.select_by_visible_text(FORM_FIX_FIELDS.get("visit_frequency"))
        # Fill country
        country = Select(driver.find_element(
            By.CSS_SELECTOR,
            "select[name='data[Solicitude][pais_origen]']"
        ))
        country.select_by_visible_text(FORM_FIX_FIELDS.get("country"))
        # Fill place
        place = WebDriverWait(driver, 0).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".form-control#SolicitudeLugarEspecificoEvento"))
        )
        place.send_keys(FORM_FIX_FIELDS.get("specific_place"))
        # Fill men count
        men_count = WebDriverWait(driver, 0).until(
            EC.presence_of_element_located((By.ID, "SolicitudeCantidadHombres"))
        )
        men_count.send_keys(FORM_FIX_FIELDS.get("men_count"))
        # Fill women count
        women_count = WebDriverWait(driver, 0).until(
            EC.presence_of_element_located((By.ID, "SolicitudeCantidadMujeres"))
        )
        women_count.send_keys(FORM_FIX_FIELDS.get("women_count"))
        # Fill description
        description = WebDriverWait(driver, 0).until(
            EC.presence_of_element_located((By.ID, "SolicitudeDescripcion"))
        )
        description.send_keys(FORM_FIX_FIELDS.get("description"))

        # Find the 'next' button and click it
        new_request_button = driver.find_element(
            By.CSS_SELECTOR,
            ".btn.btn-primary.pull-right"
        )
        new_request_button.click()


        # Fill participants
        participants = WebDriverWait(driver, 0).until(
            EC.presence_of_element_located((By.ID, "SolicitudePlan1"))
        )
        participants.send_keys(str(participants_str))
        # Fill plan
        plan = WebDriverWait(driver, 0).until(
            EC.presence_of_element_located((By.ID, "SolicitudePlan2"))
        )
        plan.send_keys(str(plan_str))

        # Find the 'next' button and click it
        next_button = driver.find_element(
            By.CSS_SELECTOR,
            ".btn.btn-primary.pull-right"
        )
        next_button.click()

        # Upload ID image
        image = driver.find_element(
            By.ID,
            "DocumentoDocumento"
        )
        # Use JavaScript to remove the "disabled" attribute
        driver.execute_script(
            "arguments[0].removeAttribute('disabled')",
            image
        )
        image.send_keys(str(Path(path_to_image).resolve()))
        # Find upload button and click it
        load_button = driver.find_element(
            By.CSS_SELECTOR,
            "button.btn.btn-default"
        )
        load_button.click()
        
        time.sleep(1)

        # Click on "Accept"
        accept_button = driver.find_element(
            By.CSS_SELECTOR,
            "input[type='radio'][name='aceptacion'][value='SI']"
        )
        accept_button.click()

        # Click on "Finish" button
        finish_button = driver.find_element(
            By.CSS_SELECTOR,
            "button.btn.btn-primary.pull-right"
        )
        if not test:
            finish_button.click()
        else:
            print("Everything is fine up to here.")

        time.sleep(10)

    finally:
        # Close the browser
        driver.quit()


def test_format_date():
    day = "J"
    hour = "19:00"
    weeks_ahead = 1
    requested_start_date = get_requested_date(
        day,
        hour,
        weeks_ahead
    )
    requested_end_date = (datetime.strptime(
        requested_start_date,
        OUTPUT_DATE_FORMAT
    ) + timedelta(hours=EVENT_DURATION_IN_HOURS)).strftime(OUTPUT_DATE_FORMAT)
    print(requested_start_date)
    print(requested_end_date)


def main():
    parser = argparse.ArgumentParser(
        description="Make a request in 'tpu.parquemet.cl'.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'user_id',
        type=str,
        help="""RUT in the format 13477xxxx (i.e. without
        hyphen before the last digit)."""
    )
    parser.add_argument(
        'path_to_image',
        type=str,
        help="""Path to the image containing the identity card
        (aka 'carnet') picture."""
    )
    parser.add_argument(
        'requested_day',
        type=str,
        choices=list(DAYS_MAPPING.keys()),
        help="""Day to be requested."""
    )
    parser.add_argument(
        "requested_time",
        type=str,
        help="""Requested time in the format HH:MM."""
    )
    parser.add_argument(
        'weeks_ahead',
        type=int,
        help="""Minimum number of weeks in advance to make
        the request. It means the requested starting date
        is just after the specified weeks. Consider the platform
        only accepts requests made with 5 days in advance."""
    )
    parser.add_argument(
        '--path_to_participants',
        type=str,
        default="participants/participants.txt",
        help="""Path to the txt file specifying the participants."""
    )
    parser.add_argument(
        '--path_to_plan',
        type=str,
        default="plans/plan.txt",
        help="""Path to the txt file specifying the cleaning action
        plan."""
    )
    parser.add_argument(
        '--show_browser',
        action='store_true',
        help="""Add this flag to show the browser while making
        the request."""
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="""Add this flag to run all the code except clicking
        the last button."""
    )
    args = parser.parse_args()

    with open(args.path_to_participants, 'r') as file:
        participants = file.read()
    with open(args.path_to_plan, 'r') as file:
        plan = file.read()

    request_soccer_field(
        args.user_id,
        args.requested_day,
        args.requested_time,
        args.weeks_ahead,
        participants,
        plan,
        args.path_to_image,
        args.show_browser,
        args.test
    )

if __name__ == "__main__":
    main()
