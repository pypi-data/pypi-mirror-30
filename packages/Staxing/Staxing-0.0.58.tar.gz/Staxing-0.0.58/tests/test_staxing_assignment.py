"""Staxing test files - Assignment."""

import datetime
import os
import unittest
import time

from random import randint
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome import options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as expect
from staxing.assignment import Assignment
from staxing.helper import User


__version__ = '0.0.3'
DRIVER = os.getenv('DRIVER', 'chrome')


class TestStaxingAssignment(unittest.TestCase):
    """Staxing case tests for Assignment."""

    def setUp(self):
        """Pretest settings."""
        self.assignment = Assignment()
        option_set = options.Options()
        option_set.add_argument('disable-infobars')
        option_set.add_argument('enable-devtools-experiments')
        option_set.add_argument('disable-search-geolocation-disclosure')
        if 'headless' in DRIVER:
            option_set.add_argument('headless')
        option_set.add_experimental_option(
            'prefs', {
                'credentials_enable_service': False,
                'profile': {
                    'password_manager_enabled': False
                }
            }
        )
        if 'chrome' in DRIVER or 'headless' in DRIVER:
            self.driver = webdriver.Chrome(chrome_options=option_set)
        self.wait = WebDriverWait(self.driver, 15)
        self.driver.implicitly_wait(1)

    def tearDown(self):
        """Test destructor."""
        try:
            self.assignment.__del__()
        except Exception:
            pass
        try:
            self.driver.__del__()
        except Exception:
            pass

    def setup_user_and_dates(self):
        user = User(username=os.getenv('TEACHER_USER'),
                    password=os.getenv('TEACHER_PASSWORD'),
                    existing_driver=self.driver)
        user.login()
        user.select_course(appearance='biology')

        today = datetime.date.today()
        open_on = (today + datetime.timedelta(days=3)).strftime('%m/%d/%Y')
        due_at = (today + datetime.timedelta(days=6)).strftime('%m/%d/%Y')
        return (user, open_on, due_at)

    def test_assignment_class_method_rword(self):
        """Test the random character string generator."""
        x_05 = Assignment.rword(5)
        x_15 = Assignment.rword(15)
        assert(len(x_05) == 5 and len(x_15) == 15), 'Incorrect string length'
        assert(Assignment.rword(0) == ''), 'Non-empty string returned'

    def test_assignment_class_method_scroll_to(self):
        """Test page scrolling to show aspecific element."""
        self.driver.set_window_size(1024, 768)
        self.driver.get('https://www.google.com/#q=openstax')
        time.sleep(1)
        last_link = self.driver.find_elements(By.CSS_SELECTOR, 'div.g')
        assert(last_link), 'No elements found'
        last_link = last_link[-2].find_element(By.TAG_NAME, 'a')
        with self.assertRaises(WebDriverException):
            last_link.click()
        Assignment.scroll_to(self.driver, last_link, True)
        time.sleep(3)
        last_link.click()

    def test_assignment_class_method_send_keys(self):
        """Test send keystrokes individually."""
        self.driver.get('https://www.randomlists.com/random-words')
        self.driver.find_element(By.NAME, 'submit').click()
        word_list = self.driver.find_elements(By.CSS_SELECTOR, '.crux')
        word = word_list[randint(0, len(word_list) - 1)].text
        self.driver.get('https://duckduckgo.com/')
        search = self.driver.find_element(By.ID, 'search_form_input_homepage')
        Assignment.send_keys(self.driver, search, word + '\n')
        search = self.driver.find_element(By.ID, 'search_form_input')
        assert(word in self.driver.page_source.lower()), 'Word not searched'

    def test_assignment_open_assignment_menu(self):
        """Test opening the assignment creation menu."""
        self.driver.get('https://' + os.getenv('SERVER_URL'))
        self.driver.find_element(By.CSS_SELECTOR, '.login').click()
        login = self.driver.find_element(
            By.CSS_SELECTOR,
            '#login_username_or_email'
        )
        login.click()
        login.send_keys(os.getenv('TEACHER_USER'))
        self.driver.find_element(By.CSS_SELECTOR, '[type=submit]').click()
        password = self.driver.find_element(
            By.CSS_SELECTOR,
            '#login_password'
        )
        password.click()
        password.send_keys(os.getenv('TEACHER_PASSWORD'))
        self.driver.find_element(By.CSS_SELECTOR, '[type=submit]').click()
        courses = self.driver.find_elements(
            By.CSS_SELECTOR,
            '.my-courses-current [data-course-course-type=tutor]'
        )
        courses[randint(0, len(courses) - 1)].click()
        try:
            self.wait.until(
                expect.element_to_be_clickable(
                    (By.XPATH, '//button[contains(text(),"For extra credit")]')
                )
            ).click()
            self.find(By.CLASS_NAME, 'btn-primary').click()
        except Exception:
            pass
        menu = self.driver.find_element(By.CLASS_NAME, 'sidebar-toggle')
        Assignment.scroll_to(self.driver, menu)
        if 'open' not in menu.get_attribute('class'):
            time.sleep(2)
            menu.click()
        self.assignment.open_assignment_menu(self.driver)
        assert('open' in menu.get_attribute('class'))

    def test_assignment_modify_time(self):
        """Test time modification."""
        assert('400a' == self.assignment.modify_time('4:00 am'))
        assert('800a' == self.assignment.modify_time('8:00a'))
        assert('800p' == self.assignment.modify_time('800p'))
        assert('800p' == self.assignment.modify_time('8:00 pm'))
        assert('1000a' == self.assignment.modify_time('1000a'))
        assert('1000p' == self.assignment.modify_time('1000p'))

    '''def test_assignment_adjust_date_picker(self):
        """
        Test the date picker rotation to move to the
        correct month and year.
        """

        pass

    def test_assignment_assign_time(self):
        """"""

    def test_assignment_to_date_string(self):
        """"""

    def test_assignment_assign_date(self):
        """"""

    def test_assignment_assign_periods(self):
        """"""

    def test_assignment_select_status(self):
        """"""

    def test_assignment_open_chapter_list(self):
        """"""

    def test_assignment_select_sections(self):
        """"""'''

    def test_assignment_add_new_reading(self):
        """Add a new reading."""
        user, _open, _due = self.setup_user_and_dates()
        self.assignment.add_new_reading(
            driver=self.driver,
            title='New-Reading',
            description='test_assignment_add_new_reading',
            periods={'all': (_open, _due)},
            readings=['ch5'],
            status='publish'
        )

    '''def test_assignment_find_all_questions(self):
        """"""

    def test_assignment_get_chapter_list(self):
        """"""

    def test_assignment_set_tutor_selections(self):
        """"""

    def test_assignment_add_homework_problems(self):
        """"""'''

    def test_assignment_add_new_homework(self):
        """Add a new homework."""
        user, _open, _due = self.setup_user_and_dates()
        self.assignment.add_new_homework(
            driver=user.driver,
            title='NewReading',
            description='test_assignment_add_new_homework',
            periods={'all': (_open, _due)},
            problems={'1.1': 3, 'tutor': 3},
            status='publish',
            feedback='immediate'
        )

    def test_assignment_add_new_external(self):
        """Add a new external assignment."""
        user, _open, _due = self.setup_user_and_dates()
        self.assignment.add_new_external(
            driver=user.driver,
            title='New-External',
            description='test_assignment_add_new_external',
            periods={'all': (_open, _due)},
            assignment_url='google.com',
            status='publish'
        )

    def test_assignment_add_new_event(self):
        """Add a new event."""
        user, _open, _due = self.setup_user_and_dates()
        self.assignment.add_new_event(
            driver=user.driver,
            title='New-Event',
            description='test_assignment_add_new_event',
            periods={'all': (_open, _due)},
            status='publish'
        )

    '''def test_assignment_change_reading(self):
        """"""

    def test_assignment_change_homework(self):
        """"""

    def test_assignment_change_external(self):
        """"""

    def test_assignment_change_event(self):
        """"""

    def test_assignment_delete_reading(self):
        """"""

    def test_assignment_delete_homework(self):
        """"""

    def test_assignment_delete_external(self):
        """"""

    def test_assignment_delete_event(self):
        """"""'''
