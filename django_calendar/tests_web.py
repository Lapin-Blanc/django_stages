#from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User

from selenium import webdriver

class AdminTestCase(StaticLiveServerTestCase):
    def setUp(self):
    # setUp is where you instantiate the selenium webdriver and loads the browser.

        self.driver = webdriver.Chrome()
        # self.driver.maximize_window()
        super(AdminTestCase, self).setUp()

    def tearDown(self):
    # Call tearDown to close the web browser
        self.driver.quit()
        super(AdminTestCase, self).tearDown()

    def test_home_page(self):
        self.driver.get(
            '%s%s' % (self.live_server_url,  "/")
        )
        self.assertIn("Gestion des stages EICA", self.driver.page_source)
