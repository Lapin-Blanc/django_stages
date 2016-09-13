#from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User

from selenium import webdriver

class AdminTestCase(StaticLiveServerTestCase):
    def setUp(self):
        # setUp is where you instantiate the selenium webdriver and loads the browser.
        User.objects.create_superuser(
            username='admin',
            password='admin',
            email='admin@example.com'
        )

        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(AdminTestCase, self).setUp()

    def tearDown(self):
        # Call tearDown to close the web browser
        self.selenium.quit()
        super(AdminTestCase, self).tearDown()

    def test_create_user(self):
        """
        Django admin create user test
        This test will create a user in django admin and assert that
        page is redirected to the new user change form.
        """
        # Open the django admin page.
        # DjangoLiveServerTestCase provides a live server url attribute
        # to access the base url in tests
        self.selenium.get(
            '%s%s' % (self.live_server_url,  "/admin/")
        )

        # Fill login information of admin
        username = self.selenium.find_element_by_id("id_username")
        username.send_keys("admin")
        password = self.selenium.find_element_by_id("id_password")
        password.send_keys("admin")

        # Locate Login button and click it
        self.selenium.find_element_by_xpath('//input[@value="Connexion"]').click()
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/admin/auth/user/add/")
        )

        # Fill the create user form with username and password
        self.selenium.find_element_by_id("id_username").send_keys("test")
        self.selenium.find_element_by_id("id_password1").send_keys("test1944")
        self.selenium.find_element_by_id("id_password2").send_keys("test1944")

        # Forms can be submitted directly by calling its method submit
        self.selenium.find_element_by_id("user_form").submit()
        self.assertIn("Modification de utilisateur", self.selenium.title)