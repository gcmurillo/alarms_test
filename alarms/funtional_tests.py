
import selenium
import unittest
from selenium.webdriver.common.keys import Keys

class FuntionalTest(unittest.TestCase):

    def setUp(self):
        # executable_path use for local tests
        self.browser = selenium.webdriver.Firefox(executable_path="/usr/local/bin/geckodriver/geckodriver", log_path="geckodriver.log")
        self.username = 'user_prueba1'
        self.password = 'djangoprueba'

    def tearDown(self):
        self.browser.quit()

    def test_admin_index_page(self):
        ''' Get access to admin page '''
        self.browser.get('http://127.0.0.1:8000/admin/')
        assert 'Log in' in self.browser.page_source

    def test_alarms_api_page(self):
        ''' Get access to api_alarms API'''

        self.browser.get('http://localhost:8000/api/api_alarms')
        assert 'HTTP 200 OK' in self.browser.page_source

    def test_refuse_events_api_page(self):
        ''' Refuse access to events API, because user is not logged '''
        self.browser.get('http://localhost:8000/api/api_alarms/events/')
        self.assertNotIn('HTTP 200 OK', self.browser.page_source)

    def test_refuse_notifications_api_page(self):
        self.browser.get('http://localhost:8000/api/api_alarms/notifications/')
        self.assertNotIn('HTTP 200 OK', self.browser.page_source)

    def test_admin_login(self):
        self.browser.get('http://127.0.0.1:8000/admin')
        username_field = self.browser.find_element_by_css_selector("form input[name='username']")
        password_field = self.browser.find_element_by_css_selector("form input[name='password']")
        username_field.send_keys(self.username)
        password_field.send_keys(self.password)

        submit = self.browser.find_element_by_css_selector('form input[type="submit"]')
        submit.click()

    def test_notification_api_page(self):
        self.browser.get('http://127.0.0.1:8000/admin')
        username_field = self.browser.find_element_by_css_selector("form input[name='username']")
        password_field = self.browser.find_element_by_css_selector("form input[name='password']")
        username_field.send_keys(self.username)
        password_field.send_keys(self.password)

        submit = self.browser.find_element_by_css_selector('form input[type="submit"]')
        submit.click()

        self.browser.get('http://localhost:8000/api/alarms/notifications/')
        self.assertIn('HTTP 200 OK', self.browser.page_source)

if __name__ == '__main__':
    unittest.main(warnings='ignore')