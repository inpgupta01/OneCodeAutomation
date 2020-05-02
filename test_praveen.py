from appium import webdriver
from appium.common.exceptions import NoSuchContextException
from appium.webdriver.common.touch_action import TouchAction
import urllib.request
import time
import json
import os
import sys
import pytest
import allure

driver = None

with open('Input.txt') as file:
    my_dict = json.load(file)
    login_mail = my_dict["login_mail"]
    external_keeper = my_dict["external_keeper"]
    alias_name = my_dict["alias_name"]
    conf_id = my_dict["conf_id"]
    call_type = my_dict["call_type"]
file.close()

"""
login_mail = str(sys.argv[1]) + "@gmail.com"
external_keeper = str(sys.argv[2])
alias_name = str(sys.argv[1])
call_type = str(sys.argv[3])
conf_id = str(sys.argv[4])
"""

@allure.severity(allure.severity_level.NORMAL)
class TestRealPresenceMobile:
    """
    def test_checking_pre_requisites(self):
        response = os.system("ping -n 3 " + external_keeper)
        if response == 0:
            print(external_keeper + "is running")
        else:
            print("Please check"+external_keeper+ "it's not running")
            exit()
    """
    def test_setup(self):
        desired_cap = {
            "platformName": "Android",
            "deviceName": "531727d6",
            "platformVersion": "9",
            "appPackage": "com.polycom.cmad.mobile.android.phone",
            "appActivity": "com.polycom.cmad.mobile.android.phone.PhoneStartActivity",
            "autoGrantPermissions": 'True',
            "resetKeyboard": "true",
            "unicodeKeyboard": "true",
            "newCommandTimeout": '900'
        }
        global driver
        driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_cap)

    @allure.severity(allure.severity_level.NORMAL)
    def test_eula_agreement(self):
        driver.implicitly_wait(30)
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/agree").click()
        driver.implicitly_wait(5)
        eula = driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/eulaok")
        ok = eula.text
        assert ok == "OK"
        eula.click()
        driver.implicitly_wait(5)

    @allure.severity(allure.severity_level.NORMAL)
    def test_email_details(self):
        driver.find_element_by_class_name("android.widget.EditText").click()
        driver.implicitly_wait(5)
        driver.find_element_by_class_name("android.widget.EditText").send_keys(login_mail)
        driver.implicitly_wait(5)
        next1 = driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/btn_next").text
        assert next1 == "Next"
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/btn_next").click()

    def test_skip_sign_in(self):
        driver.implicitly_wait(30)
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/btn_skip_signin").click()

    # Setting Page
    def test_setting_page(self):
        driver.implicitly_wait(5)
        driver.find_element_by_accessibility_id("More options").click()
        driver.implicitly_wait(5)
        driver.find_element_by_xpath("//android.widget.TextView[@text='Settings']").click()

    if call_type == "H323":
        ## H323 Registration setting

        @allure.severity(allure.severity_level.CRITICAL)
        def test_h323_registration(self):
            driver.find_element_by_xpath("//android.widget.TextView[@text='H.323 Settings']").click()
            driver.implicitly_wait(5)

            # Selection of Environment
            # driver.find_element_by_xpath("android.widget.CheckBox[@bounds='[898,450][986,538]']").click()
            driver.find_element_by_xpath(
                "/hierarchy/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout["
                "2]/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.LinearLayout/android.widget"
                ".FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.ListView/android.widget"
                ".LinearLayout[2]/android.widget.LinearLayout/android.widget.CheckBox").click()
            driver.implicitly_wait(5)
            driver.find_element_by_xpath("//android.widget.TextView[@text='Internal Gatekeeper Selected']").click()
            driver.implicitly_wait(5)
            driver.find_element_by_xpath("//android.widget.CheckedTextView[@text='External Gatekeeper']").click()
            time.sleep(2)

            # External/Internal GateKeeper Registration
            driver.implicitly_wait(3)
            # driver.find_element_by_xpath("//android.widget.TextView[@text='External Gatekeeper']").click()
            driver.find_element_by_xpath(
                "/hierarchy/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout["
                "2]/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.LinearLayout/android.widget"
                ".FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.ListView/android.widget"
                ".LinearLayout[5]/android.widget.RelativeLayout/android.widget.TextView[1]").click()
            driver.implicitly_wait(5)
            driver.find_element_by_id("android:id/edit").send_keys(external_keeper)
            driver.implicitly_wait(2)
            driver.find_element_by_id("android:id/button1").click()
            driver.implicitly_wait(2)

            # Alias Name for H323
            driver.find_element_by_xpath("//android.widget.TextView[@text='H.323 Name']").click()
            driver.implicitly_wait(2)
            driver.find_element_by_id("android:id/edit").send_keys(alias_name)
            driver.implicitly_wait(2)
            driver.find_element_by_id("android:id/button1").click()

            driver.back()
            ##driver.back()
    else:
        @allure.severity(allure.severity_level.CRITICAL)
        def test_sip_registration(self):
            driver.implicitly_wait(5)
            driver.find_element_by_xpath("//android.widget.TextView[@text='SIP Settings']").click()
            driver.implicitly_wait(5)
            driver.find_element_by_xpath(
                "/hierarchy/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout["
                "2]/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.LinearLayout/android.widget"
                ".FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.ListView/android.widget"
                ".LinearLayout[1]/android.widget.LinearLayout/android.widget.CheckBox").click()
            driver.implicitly_wait(2)
            driver.find_element_by_xpath(
                "/hierarchy/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout["
                "2]/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.LinearLayout/android.widget"
                ".FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.ListView/android.widget"
                ".LinearLayout[3]/android.widget.LinearLayout/android.widget.CheckBox").click()

            # SIP transport Protocol
            driver.find_element_by_xpath("//android.widget.TextView[@text='Transport Protocol']").click()
            driver.find_element_by_xpath("//android.widget.CheckedTextView[@text='TCP']").click()

            # SIP Proxy server
            driver.implicitly_wait(2)
            driver.find_element_by_xpath("//android.widget.TextView[@text='SIP Proxy Server']").click()
            driver.implicitly_wait(10)
            driver.find_element_by_id("android:id/edit").send_keys(external_keeper)
            driver.find_element_by_id("android:id/button1").click()

            # SIP User Name
            driver.find_element_by_xpath("//android.widget.TextView[@text='SIP User Name']").click()
            driver.implicitly_wait(5)
            driver.find_element_by_id("android:id/edit").send_keys(alias_name)
            driver.find_element_by_id("android:id/button1").click()

            # Domain
            driver.find_element_by_xpath("//android.widget.TextView[@text='Domain']").click()
            driver.find_element_by_id("android:id/edit").send_keys(alias_name)
            driver.find_element_by_id("android:id/button1").click()

            # Authorization Name
            driver.find_element_by_xpath("//android.widget.TextView[@text='Authorization Name']").click()
            driver.find_element_by_id("android:id/edit").send_keys(alias_name)
            driver.find_element_by_id("android:id/button1").click()
            driver.back()
            time.sleep(5)
            """
            driver.implicitly_wait(30)            
            cert = driver.find_element_by_id("android:id/button1").text
            if cert == "OK":
                driver.find_element_by_id("android:id/button1").click()
            """

    @allure.severity(allure.severity_level.CRITICAL)
    def test_registration_status(self):
        # H323 Registration Status
        if call_type == "H323":
            driver.back()
            driver.find_element_by_accessibility_id("More options").click()
            driver.implicitly_wait(5)
            driver.find_element_by_xpath("//android.widget.TextView[@text='Status']").click()

            # check for H323
            h323_expected = external_keeper
            h323_actual = driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/status_content_h323").text
            assert h323_expected in h323_actual

        # SIPP Registration Status
        else:
            driver.back()
            driver.find_element_by_accessibility_id("More options").click()
            driver.implicitly_wait(5)
            driver.find_element_by_xpath("//android.widget.TextView[@text='Status']").click()

            # check for SIP
            sip_expected = external_keeper
            sip_actual = driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/status_content_sip").text
            assert sip_expected in sip_actual

    @allure.severity(allure.severity_level.BLOCKER)
    def test_phone_call(self):
        driver.back()
        if call_type == "SIP":
            driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/rb_sip").click()
        else:
            print("It's H323 Call")

        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/digits").send_keys(conf_id)
        driver.implicitly_wait(2)
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/dial_to_call").click()
        driver.orientation = "LANDSCAPE"

    ## Audio/Video Connect/Disconnect and Mute/unmute feature
    @allure.severity(allure.severity_level.CRITICAL)
    def test_functional_test(self):
        time.sleep(20)
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/phone_main_view").click()
        # check1 = driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_conv_mute_video").size()
        # for action in check1:
        #    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/phone_main_view").click()
        # else:
        #    print("Screen is visible")
        for i in range(2):
            driver.implicitly_wait(2)
            driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_conv_mute_video").click()
            time.sleep(2)
            driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_conv_mute_audio").click()
            time.sleep(2)
            driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_conv_mute_speaker").click()
            time.sleep(4)

    @allure.severity(allure.severity_level.NORMAL)
    def test_call_disconnect(self):
        time.sleep(20)
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/phone_main_view").click()
        # check = driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_conv_hangup").size()
        # for action in check:
        #    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_conv_hangup").click()
        # else:
        # driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/phone_main_view").click()
        driver.implicitly_wait(5)
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_conv_hangup").click()
        # driver.close()


"""
    def test_camera_switch(self):
        touch = TouchAction(driver)
        # driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/phone_main_view").click()
        # time.sleep(1)
        touch.press(x=702, y=483).move_to(x=1553, y=513).release().perform()
        time.sleep(3)
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/local_camera_switch").click()
        time.sleep(3)
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/local_camera_switch").click()
        time.sleep(3)
        touch.press(x=997, y=340).move_to(x=343, y=318).release().perform()

    def test_network_status(self):
        driver.implicitly_wait(5)
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/phone_main_view").click()
        driver.implicitly_wait(5)
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_network_statistics").click()
        time.sleep(2)
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_network_statistics").click()
"""
