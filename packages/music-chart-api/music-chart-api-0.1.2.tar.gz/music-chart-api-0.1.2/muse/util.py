from selenium.webdriver import Chrome, ChromeOptions

"""
    Module for utility
    classes and functions
"""


class HeadlessChrome(Chrome):
    """
        ChromeDriver with
        headless options

        '--headless' '--disable-gpu'
    """

    def __init__(self):
        # chrome options for headless
        options = ChromeOptions()

        # add argument to headless chrome
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        # initialize headless chrome
        super(HeadlessChrome, self).__init__(chrome_options=options)

    # called when with statement started
    def __enter__(self):
        return self

    # called when with statement finished
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
