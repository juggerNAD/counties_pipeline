def login(driver):
    """
    Manual login required for TylerTech Cloud.
    After login, Selenium continues fully automated.
    """
    LOGIN_URL = "https://ohio.tylertech.cloud/idp/account/signin"
    driver.get(LOGIN_URL)

    print("\n🔐 MANUAL LOGIN REQUIRED")
    print("👉 Complete the login in the browser:")
    print("   - Enter email")
    print("   - Enter password")
    print("   - Solve CAPTCHA / MFA if shown")
    print("👉 Wait until the Lucas County Probate site is visible")

    input("\nPress ENTER after login is complete...")

    print("✅ Login confirmed. Automation continues.")
