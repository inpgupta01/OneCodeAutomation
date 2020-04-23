from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
import urllib.request
import time
import json
import sys

# DESRIED CAPABILITIES REQUIRED TO RUN ANDROID APPLICATION
desired_cap = {
    "platformName": "Android",
    "deviceName": "531727d6",
    "platformVersion": "10",
    "appPackage": "com.polycom.cmad.mobile.android.phone",
    "appActivity": "com.polycom.cmad.mobile.android.phone.PhoneStartActivity",
    "autoGrantPermissions": 'True',
    "clearSystemFiles": "true",
    "resetKeyboard": "true",
    "unicodeKeyboard": "true",
    "newCommandTimeout": '900'
}
driver = webdriver.Remote("http://localhost:4723/wd/hub", desired_cap)

# READING INPUT FROM INPUT FILE

"""
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


# Sign To ULA Agreement
def eula_agreement():
    driver.implicitly_wait(30)
    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/agree").click()
    driver.implicitly_wait(5)
    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/eulaok").click()
    driver.implicitly_wait(5)


# Email Enter
def email_details(email):
    driver.find_element_by_class_name("android.widget.EditText").click()
    driver.implicitly_wait(5)
    driver.find_element_by_class_name("android.widget.EditText").send_keys(email)
    driver.implicitly_wait(5)
    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/btn_next").click()
    driver.implicitly_wait(30)


# Sign In Code
"""def sign_in():
    driver.find_element_by_class_name("android.widget.EditText").send_keys("video.myrpp.com")
    driver.implicitly_wait(1)
    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/btn_next").click()
    driver.implicitly_wait(30)
    driver.find_element_by_class_name("android:id/button3").click()
"""


## Skip the Sign In
def skip_sign_in():
    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/btn_skip_signin").click()
    driver.implicitly_wait(5)


# Setting Page
def setting_page():
    driver.find_element_by_accessibility_id("More options").click()
    driver.implicitly_wait(5)
    driver.find_element_by_xpath("//android.widget.TextView[@text='Settings']").click()


## H323 Registration setting
def h323_registration():
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


def sip_registration():
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
    # driver.find_element_by_xpath("//android.widget.TextView[@text='Transport Protocol']").click()
    # driver.find_element_by_xpath("//android.widget.CheckedTextView[@text='TLS']").click()

    # SIP Proxy server
    driver.implicitly_wait(2)
    driver.find_element_by_xpath("//android.widget.TextView[@text='SIP Proxy Server']").click()
    driver.find_element_by_id("android:id/edit").send_keys(external_keeper)
    driver.find_element_by_id("android:id/button1").click()

    # Domain
    driver.find_element_by_xpath("//android.widget.TextView[@text='Domain']").click()
    driver.find_element_by_id("android:id/edit").send_keys(alias_name)
    driver.find_element_by_id("android:id/button1").click()

    # SIP User Name
    driver.find_element_by_xpath("//android.widget.TextView[@text='SIP User Name']").click()
    driver.implicitly_wait(5)
    driver.find_element_by_id("android:id/edit").send_keys(alias_name)
    driver.find_element_by_id("android:id/button1").click()

    # Authorization Name
    driver.find_element_by_xpath("//android.widget.TextView[@text='Authorization Name']").click()
    driver.find_element_by_id("android:id/edit").send_keys(alias_name)
    driver.find_element_by_id("android:id/button1").click()
    driver.back()


def registration_status():
    driver.back()
    driver.find_element_by_accessibility_id("More options").click()
    driver.implicitly_wait(5)
    driver.find_element_by_xpath("//android.widget.TextView[@text='Status']").click()

    # check for H323
    h323_expected = "Gatekeeper: " + external_keeper
    sip_expected = "Your registration request was rejected by the server."
    h323_actual = driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/status_content_h323").text
    sip_actual = driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/status_content_sip").text

    # assert h323_actual == h323_expected, "Failed due to :" + h323_actual
    # assert sip_actual != sip_expected, "Failed due to :" + sip_actual

    #  Call Connection


def phone_call():
    if call_type == "SIP":
        sip_registration()
    else:
        h323_registration()

    # driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/digits").click()
    driver.back()
    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/digits").send_keys(conf_id)
    driver.find_element_by_id('com.polycom.cmad.mobile.android.phone:id/top').click()
    # driver.back()
    driver.implicitly_wait(2)
    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/dial_to_call").click()


## Audio/Video Connect/Disconnect and Mute/unmute feature
def functional_test():
    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/phone_main_view").click()
    for i in range(2):
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_conv_mute_video").click()
        time.sleep(2)
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_conv_mute_audio").click()
        time.sleep(2)
        driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_conv_mute_speaker").click()
        time.sleep(4)


def camera_switch():
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


def network_status():
    driver.implicitly_wait(5)
    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/phone_main_view").click()
    driver.implicitly_wait(5)
    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_network_statistics").click()
    time.sleep(2)
    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_network_statistics").click()


def call_disconnect():
    driver.implicitly_wait(10)
    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/phone_main_view").click()
    #driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/phone_main_view").click()
    driver.implicitly_wait(10)
    driver.find_element_by_id("com.polycom.cmad.mobile.android.phone:id/toolbar_conv_hangup").click()


eula_agreement()
email_details(login_mail)
skip_sign_in()
setting_page()
# registration_status()
phone_call()
time.sleep(30)
functional_test()
# camera_switch()
# network_status()
time.sleep(40)
call_disconnect()
