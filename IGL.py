import os

import time
from datetime import datetime

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

import pandas as pd
from pandas import DataFrame

from send_email import send_email

mime_types = "application/pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml"

profile = FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.dir", "E:\\temp")
profile.set_preference("pdfjs.disabled", False)
profile.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf" )


#-------------URLS-----------------

IGL_url = "https://webonline.igl.co.in:8077/sap/bc/bsp/sap/zumcui5/webcontent/index.html?directPayment#page|%7B%22id%22%3A%22instaPayment%22%7D|0"


#__________ELEMENTS______________
CA_NUMBER       ='//*[@id="__field1"]'
SUBMIT          ='//*[@id="__button1"]'
CUSTOMER_NAME   ='//*[@id="Fntextfield"]'
DUE_DATE        ='//*[@id="__field5"]'
BILL_AMOUNT     ='//*[@id="finalBA"]'
ENTER           = u'\ue007'


#__________COMMON DIR'S____________
bill_png = "/home/sau19/web-scraping/IGL/bill_screenShots/"
bill_log = "/home/sau19/web-scraping/IGL/bill_logs/igl_log.csv"
fail_log ="/home/sau19/web-scraping/IGL/fail_logs.txt"



#___________GLOBAL VARIABLES__________

dateTime = datetime.now()
dateTime = str( dateTime.strftime("%d-%m-%Y %H:%M:%S") )

AMOUNT = []
BILL_ISSUE_DATE = []
BILL_DUE_DATE = []
CUSTOMER = []
CON_NUMBER = []

class IGL_Bills:

    def setUp(self):
        #define a browser instance, for example Chrome

        self.browser = webdriver.Firefox(firefox_profile=profile , executable_path=None)
        self.browser.maximize_window()

        browser = self.browser
        browser.get( IGL_url )

    def Get_IGL_Bills_data(self, CA_no):
        self.CA_no = CA_no

        browser = self.browser

        CA_number = browser.find_element_by_xpath( CA_NUMBER )
        CA_number.click()
        CA_number.send_keys( CA_no )
        CON_NUMBER.append( CA_no )
        print("Entering CA_number",CA_no)

        submit = browser.find_element_by_xpath( SUBMIT )
        submit.click()
        print("Submitting...")
        time.sleep(3)

        try:
            bill_amount = browser.find_elements_by_xpath( BILL_AMOUNT )[0].get_attribute('value')
            amount = str(bill_amount)
            amount = amount.replace(" ","")
            amount = amount.strip()
            AMOUNT.append( amount )

            due_date = browser.find_elements_by_xpath( DUE_DATE )[0].get_attribute('value')
            due_date = str(due_date).replace(".", "-")

            dueDate_obj = datetime.strptime( due_date  , "%d-%m-%Y").date()
            dueDate_obj = str( dueDate_obj.strftime("%d-%b-%Y") )

            BILL_DUE_DATE.append( dueDate_obj )

            # read if this is a newly generated bill
            previous_dueDate = pd.read_csv( bill_log ).iloc[-1][ "Due date" ]


            print("previous_dueDate ", previous_dueDate)
            print("new_duedate ", BILL_DUE_DATE[0] )

            if ( BILL_DUE_DATE[0] == str(previous_dueDate) ) or ( AMOUNT[0] == "0.00"):
                print("No new bill have been generated :")
            else:

                Customer_name = browser.find_elements_by_xpath( CUSTOMER_NAME )[0].get_attribute('value')
                CUSTOMER.append( Customer_name )

                # Saving bill screen shot as today date
                bill_name = datetime.today()

                browser.save_screenshot( bill_png + str( bill_name.date().strftime('%d-%m-%Y') ) +".png" )
                print("Bill downloaded!")

                print(CUSTOMER[0])
                print(CON_NUMBER[0])
                print(BILL_DUE_DATE[0])
                print(AMOUNT[0])

                Save_bill_log()
        except Exception as err:
            print(err)
            with open( fail_log , 'a') as file:
                    log_msg = "\n" + "IGL Failed at :" + str( datetime.now() ) + "\n" + str( err )
                    file.write( log_msg )
                    file.close()
            send_email("ykings.saurabh@gmail.com", "Bill Alert Failed, IGL", log_msg )

    def tearDown(self):
        time.sleep(1)
        #self.browser.close()
        self.browser.quit()


def Save_bill_log():
    # Wirting to csv file log
    Data = {

            "DATE TIME"        : dateTime,
            "CUSTOMER NAME"    : CUSTOMER[0],
            "CONSUMER NUMBER"  : CON_NUMBER[0],
            "DUE DATE"         : BILL_DUE_DATE[0],
            "AMOUNT"           : AMOUNT[0],

            }

    df = pd.DataFrame ( Data , columns=['DATE TIME', 'CUSTOMER NAME', 'CONSUMER NUMBER', \
                       'DUE DATE', 'AMOUNT'], index=[0])

    with open( bill_log , 'a') as file:
        df.to_csv(file, mode='a', header=False, index=False )
        file.close()
        print("log saved successfully!")


consumers_list = ['1000148978']

"""if __name__ == "__main__":

    with Display():
        try:
        	p = IGL_Bills()
        	p.setUp()
        	p.Get_IGL_Bills_data( "1000148978" )
        except Exception as err:
        	print(err)
        finally:
        	print"\nExit"
        	p.tearDown()"""










