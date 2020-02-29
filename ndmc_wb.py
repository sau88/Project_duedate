import os
from os import path

import time
from datetime import datetime

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

import pandas as pd
from pandas import DataFrame

from send_email import send_email

# Common paths

#chrome_path = "C:\Program Files\Google\Chrome\Application"
#chrome_driver = "C:\Program Files\Google\Chrome\Application\chromedriver.exe"

download_dir = "/home/sau19/web-scraping/ndmc/temp/bipt.pdf"
save_pdf  = "/home/sau19/web-scraping/ndmc_water/bill_pdfs/"
save_png  = "/home/sau19/web-scraping/ndmc_water/bill_receipts/"
csv_log   = "/home/sau19/web-scraping/ndmc_water/bill_logs/log.csv"
fail_log  = "/home/sau19/web-scraping/ndmc_water/fail_logs.txt"
# Firefox settings
mime_types = "application/pdf,application/vnd.adobe.xfdf,application/vnd.fdf,application/vnd.adobe.xdp+xml"

profile = FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.dir", "E:\\temp")
profile.set_preference("pdfjs.disabled", False)
profile.set_preference("plugin.disable_full_page_plugin_for_types", "application/pdf" )


#-------------URLS-----------------

NDMC_url="https://ccb.ndmc.gov.in/DisplayBill/PayBill.jsp?nw"



#______________________________COMMON ELEMENTS______________________________

CA_NUMBER       ='//*[@id="consumerNo"]'
BILL_AMOUNT     ='//*[@id="collapse1"]/div[1]/div[8]/div/div[4]/span'
CUSTOMER_NAME   ='//*[@id="collapse1"]/div[1]/div[2]/div/div[4]/span'
ISSUE_DATE      ='//*[@id="collapse1"]/div[1]/div[4]/div/div[4]/span'
DUE_DATE        ='//*[@id="collapse1"]/div[1]/div[5]/div/div[4]/span'
ENTER           = u'\ue007'

# Global variables

dateTime = datetime.now()
dateTime = str( dateTime.strftime("%d-%m-%Y %H:%M:%S") )

AMOUNT = []
BILL_ISSUE_DATE = []
BILL_DUE_DATE = []
CUSTOMER = []


class Water:

    """Get Electricity and water bill from NDMC"""

    def setUp(self):
        #define a browser instance, for example Chrome

        self.browser = webdriver.Firefox( firefox_profile=profile )

        browser = self.browser
        browser.get( NDMC_url )

    def Get_Water_Bill(self, CA_no):

        self.CA_no = CA_no

        browser = self.browser

        CA_number = browser.find_element_by_xpath( CA_NUMBER )
        CA_number.click()
        CA_number.send_keys( CA_no )
        print("\nEntering CA_number",CA_no)
        CA_number.send_keys( ENTER )
        print("\nSubmitting...plaese wait")
        time.sleep(3)

        try:
            due_date = browser.find_elements_by_xpath( DUE_DATE )[0].get_attribute('textContent')
            BILL_DUE_DATE.append( str(due_date).replace("/", "-") )

            # read if this is a newly generated bill
            previous_dueDate = pd.read_csv( csv_log ).iloc[-1][ "Due date" ]

            print("previous_dueDate ", previous_dueDate)
            print("BILL_DUE_DATE[0] ", BILL_DUE_DATE[0])

            if BILL_DUE_DATE[0] == str(previous_dueDate):
                print("No new bill have been generated :")
            else:
                bill_amount = browser.find_elements_by_xpath( BILL_AMOUNT )[0].get_attribute('textContent')
                amount = str(bill_amount)
                amount = amount.replace(" ","")
                amount = amount.strip()
                AMOUNT.append( amount )

                Customer_name = browser.find_elements_by_xpath( CUSTOMER_NAME )[0].get_attribute('textContent')
                CUSTOMER.append( str(Customer_name) )

                issue_date = browser.find_elements_by_xpath( ISSUE_DATE )[0].get_attribute('textContent')
                BILL_ISSUE_DATE.append( str(issue_date).replace("/", "-") )

                print(CUSTOMER[0])
                print(CUSTOMER_NAME[0])
                print(BILL_ISSUE_DATE[0])
                print(BILL_DUE_DATE[0])
                print(AMOUNT[0])

                # Previous bill reciept
                receipt_name = pd.read_csv( csv_log ).iloc[-1][ "Issue date" ]
                recpt = browser.find_element_by_xpath( '//*[@id="collapse1"]/div[1]/div[7]/div/div[4]/span/a' ).click()
                browser.switch_to.window( browser.window_handles[1] )
                time.sleep(5)
                # Save previous bill receipt as last bill's issue date
                browser.save_screenshot( save_png + str(receipt_name) + ".png")
                browser.close()
                browser.switch_to.window( browser.window_handles[0] )
                print("Bill receipt downloaded!")


                # Get pdf
                pdf = browser.find_element_by_xpath( '//*[@id="view"]' ).click()
                browser.switch_to.window( browser.window_handles[1] )
                time.sleep(30)
                browser.save_screenshot( save_pdf + str(BILL_ISSUE_DATE[0]) + ".png")
                print("Bill downloaded!")
                Save_bill_log()

                # Simulate enter key-press
                """try:
                    keyboard.press_and_release('enter')
                    time.sleep(3)
                    print("Download successful !")
                except Exception as err:
                    print("Download fialed .")
                    print(err)"""

        except Exception as err:
            print( err )
            with open( fail_log , 'a') as file:
                    log_msg = "\n" + "Failed at :" + str( datetime.now() ) + "\n" + str( err )
                    file.write( log_msg )
                    file.close()
            send_email("ykings.saurabh@gmail.com", "Bill Alert Failed", log_msg )

    def tearDown(self):
        time.sleep(1)
        print("------------Exiting-----------")
        #self.browser.close()
        self.browser.quit()

def Save_bill_log():
    # Wirting to csv file log
    Data = {

            "DATE TIME"        : dateTime,
            "CUSTOMER NAME"    : CUSTOMER[0],
            "CONSUMER NAME"    : CUSTOMER_NAME[0],
            "ISSUE DATE"       : BILL_ISSUE_DATE[0],
            "DUE DATE"         : BILL_DUE_DATE[0],
            "AMOUNT"           : AMOUNT[0],

            }

    df = pd.DataFrame ( Data , columns=['DATE TIME', 'CUSTOMER NAME', 'CONSUMER_NAME', 'ISSUE DATE', \
                       'DUE DATE', 'AMOUNT'], index=[0])

    with open( csv_log , 'a') as file:
        df.to_csv(file, mode='a', header=False, index=False )
        file.close()
        print("log saved successfully!")

def Rename_pdf():
    src=""
    # Electricity
    if path.exists( download_dir ):
        src = path.realpath( download_dir )
    os.rename( src, save_pdf + BILL_ISSUE_DATE[0] +".pdf" )



"""if __name__ == "__main__":

    with Display():
        try:
            Obj = Water()
            Obj.setUp()
            Obj.Get_Water_Bill( "2048599" )
        finally:
            print("Exit")
            Obj.tearDown()"""




