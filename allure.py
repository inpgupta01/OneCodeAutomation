
import pytest
import allure

@allure.severity(allure.severity_level.NORMAL)
def test_eula_agreement():
    print("It's OK")
    
@allure.severity(allure.severity_level.CRITICAL)
def test_eula_signup():
    print("It's OK")


test_eula_agreement()
test_eula_signup()
