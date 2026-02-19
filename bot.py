import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, JavascriptException
from webdriver_manager.chrome import ChromeDriverManager


def debug_print(msg, level="INFO"):
    """Print with timestamp for debugging"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")


def inspect_firm_section(driver, wait):
    """Inspect what's visible after clicking Firm tab"""
    debug_print("\n--- INSPECTING FIRM SECTION ---", "INFO")
    
    # Check what's visible in the DOM
    try:
        # Look for any input fields
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        debug_print(f"Total input fields found: {len(all_inputs)}", "DEBUG")
        
        for i, input_elem in enumerate(all_inputs):
            input_id = input_elem.get_attribute("id")
            input_name = input_elem.get_attribute("name")
            input_placeholder = input_elem.get_attribute("placeholder")
            input_class = input_elem.get_attribute("class")
            is_displayed = input_elem.is_displayed()
            debug_print(f"Input {i+1}: id='{input_id}', name='{input_name}', placeholder='{input_placeholder}', displayed={is_displayed}", "DEBUG")
        
        # Look specifically for firm-related inputs
        firm_inputs = driver.find_elements(By.XPATH, "//input[contains(@aria-label, 'firm') or contains(@placeholder, 'Firm') or contains(@formcontrolname, 'firm')]")
        debug_print(f"Firm-related inputs found: {len(firm_inputs)}", "DEBUG")
        
        # Check if Individual tab is still active
        active_tab = driver.find_elements(By.XPATH, "//li[contains(@class, 'active') or contains(@class, 'selected')]//div[contains(text(), 'Individual')]")
        if active_tab:
            debug_print("⚠️ Individual tab still appears active!", "WARNING")
        else:
            debug_print("✅ Individual tab not active - good", "DEBUG")
        
        # Check for any error messages or loading indicators
        loading = driver.find_elements(By.XPATH, "//*[contains(@class, 'loading') or contains(@class, 'spinner')]")
        if loading:
            debug_print(f"Loading elements found: {len(loading)}", "DEBUG")
        
    except Exception as e:
        debug_print(f"Error during inspection: {e}", "ERROR")
    
    # Take screenshot
    driver.save_screenshot("debug_firm_section.png")
    debug_print("Screenshot saved as debug_firm_section.png", "INFO")


def force_input_update(driver, input_element, value):
    """Force the input to update using multiple methods"""
    debug_print("\n--- FORCING INPUT UPDATE ---", "INFO")
    
    # Method 1: Clear and send_keys with events
    debug_print("Method 1: Clear and send_keys with events", "DEBUG")
    input_element.clear()
    input_element.send_keys(value)
    
    # Trigger events
    driver.execute_script("""
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
    """, input_element)
    
    time.sleep(0.5)
    
    # Check if it worked
    current = driver.execute_script("return arguments[0].value;", input_element)
    if current == value:
        debug_print("✅ Method 1 succeeded", "SUCCESS")
        return True
    
    # Method 2: JavaScript set + events
    debug_print("Method 2: JavaScript set + events", "DEBUG")
    driver.execute_script("""
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
    """, input_element, value)
    
    time.sleep(0.5)
    
    current = driver.execute_script("return arguments[0].value;", input_element)
    if current == value:
        debug_print("✅ Method 2 succeeded", "SUCCESS")
        return True
    
    # Method 3: Character by character with events
    debug_print("Method 3: Character by character", "DEBUG")
    input_element.clear()
    for char in value:
        input_element.send_keys(char)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", input_element)
        time.sleep(0.05)
    
    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", input_element)
    driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", input_element)
    
    time.sleep(0.5)
    
    current = driver.execute_script("return arguments[0].value;", input_element)
    if current == value:
        debug_print("✅ Method 3 succeeded", "SUCCESS")
        return True
    
    # Method 4: ActionChains simulation
    debug_print("Method 4: ActionChains simulation", "DEBUG")
    actions = ActionChains(driver)
    actions.move_to_element(input_element).click().perform()
    time.sleep(0.2)
    
    # Select all and delete
    input_element.send_keys(Keys.CONTROL + 'a')
    input_element.send_keys(Keys.DELETE)
    time.sleep(0.2)
    
    # Type slowly
    for char in value:
        actions = ActionChains(driver)
        actions.send_keys(char).perform()
        time.sleep(0.05)
    
    # Press Tab to trigger blur
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB).perform()
    
    time.sleep(0.5)
    
    current = driver.execute_script("return arguments[0].value;", input_element)
    if current == value:
        debug_print("✅ Method 4 succeeded", "SUCCESS")
        return True
    
    # Method 5: Direct DOM manipulation with multiple events
    debug_print("Method 5: Direct DOM manipulation", "DEBUG")
    driver.execute_script("""
        var input = arguments[0];
        var value = arguments[1];
        
        // Set the value
        input.value = value;
        
        // Dispatch ALL the events
        var events = ['focus', 'keydown', 'keypress', 'input', 'keyup', 'change', 'blur'];
        events.forEach(function(eventType) {
            var event = new Event(eventType, { bubbles: true });
            input.dispatchEvent(event);
        });
        
        // Also try with KeyboardEvents for good measure
        var keyboardEvents = ['keydown', 'keypress', 'keyup'];
        keyboardEvents.forEach(function(eventType) {
            var event = new KeyboardEvent(eventType, {
                bubbles: true,
                key: 'Enter',
                code: 'Enter'
            });
            input.dispatchEvent(event);
        });
    """, input_element, value)
    
    time.sleep(0.5)
    
    current = driver.execute_script("return arguments[0].value;", input_element)
    if current == value:
        debug_print("✅ Method 5 succeeded", "SUCCESS")
        return True
    
    debug_print("❌ All methods failed to set value", "ERROR")
    return False


def open_site():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    debug_print("Starting Chrome browser...", "INFO")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    # Remove automation traces
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    wait = WebDriverWait(driver, 30)
    
    debug_print("Navigating to https://brokercheck.finra.org/", "INFO")
    driver.get("https://brokercheck.finra.org/")
    time.sleep(3)

    # ---------- 1️⃣ Handle Cookie Consent ----------
    debug_print("\n--- HANDLING COOKIE CONSENT ---", "INFO")
    try:
        # Try multiple cookie button selectors
        cookie_selectors = [
            "//button[contains(text(),'Continue')]",
            "//button[contains(text(),'continue')]",
            "//button[contains(@class,'cookie')]",
            "//button[contains(text(),'Accept')]",
            "//button[contains(text(),'Customize')]"
        ]
        
        for selector in cookie_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements and elements[0].is_displayed():
                    debug_print(f"Found cookie button: {selector}", "INFO")
                    # Try both click methods
                    try:
                        elements[0].click()
                    except:
                        driver.execute_script("arguments[0].click();", elements[0])
                    debug_print("🍪 Cookie button clicked", "SUCCESS")
                    time.sleep(2)
                    break
            except Exception as e:
                continue
    except Exception as e:
        debug_print(f"Cookie handling: {e}", "DEBUG")

    # ---------- 2️⃣ Click Firm tab with verification ----------
    debug_print("\n--- CLICKING FIRM TAB ---", "INFO")
    
    # Wait for the tab to be clickable
    firm_tab = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//li[.//div[contains(.,'Firm')]]")
        )
    )
    
    # Try multiple click methods
    click_success = False
    click_methods = [
        ("normal click", lambda: firm_tab.click()),
        ("JavaScript click", lambda: driver.execute_script("arguments[0].click();", firm_tab)),
        ("ActionChains click", lambda: ActionChains(driver).move_to_element(firm_tab).click().perform())
    ]
    
    for method_name, method_func in click_methods:
        try:
            method_func()
            debug_print(f"✅ {method_name} succeeded", "SUCCESS")
            click_success = True
            break
        except Exception as e:
            debug_print(f"❌ {method_name} failed: {e}", "DEBUG")
    
    if not click_success:
        debug_print("❌ All click methods failed for Firm tab!", "ERROR")
        return driver
    
    debug_print("🏢 Firm tab clicked", "SUCCESS")
    time.sleep(3)
    
    # Inspect what's visible after clicking
    inspect_firm_section(driver, wait)

    # ---------- 3️⃣ Wait for Firm Name input with fallback ----------
    debug_print("\n--- LOCATING FIRM INPUT ---", "INFO")
    
    # Try multiple strategies to find the input
    firm_input = None
    input_strategies = [
        (By.CSS_SELECTOR, "input[formcontrolname='firmNameCrd']"),
        (By.CSS_SELECTOR, "input[aria-label='firm-name']"),
        (By.XPATH, "//input[@placeholder='Firm Name or CRD/SEC#']"),
        (By.XPATH, "//input[contains(@placeholder, 'Firm')]"),
        (By.XPATH, "//label[contains(text(), 'Firm')]/following::input[1]"),
        (By.XPATH, "//div[contains(text(), 'Firm Name')]/following::input[1]")
    ]
    
    for by, selector in input_strategies:
        try:
            debug_print(f"Trying to find input with: {selector}", "DEBUG")
            elements = driver.find_elements(by, selector)
            if elements:
                for elem in elements:
                    if elem.is_displayed():
                        firm_input = elem
                        debug_print(f"✅ Found visible input with: {selector}", "SUCCESS")
                        break
            if firm_input:
                break
        except Exception as e:
            debug_print(f"Error with {selector}: {e}", "DEBUG")
            continue
    
    if not firm_input:
        debug_print("❌ Could not find firm input with any strategy!", "ERROR")
        
        # Check if we're on the wrong tab
        debug_print("Checking if Individual tab is active...", "INFO")
        individual_active = driver.find_elements(By.XPATH, "//li[contains(@class, 'active')]//div[contains(text(), 'Individual')]")
        if individual_active:
            debug_print("⚠️ Individual tab is still active! Trying to click Firm tab again...", "WARNING")
            # Try clicking Firm tab again with JavaScript
            firm_tab = driver.find_element(By.XPATH, "//li[.//div[contains(.,'Firm')]]")
            driver.execute_script("arguments[0].click();", firm_tab)
            time.sleep(3)
            # Try finding input again
            try:
                firm_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[formcontrolname='firmNameCrd']")))
                debug_print("✅ Found input after second click attempt", "SUCCESS")
            except:
                pass
        
        if not firm_input:
            return driver
    
    # Scroll and focus
    driver.execute_script("arguments[0].scrollIntoView({block:'center', behavior: 'instant'});", firm_input)
    time.sleep(1)
    
    # Click to focus
    try:
        firm_input.click()
    except:
        driver.execute_script("arguments[0].click();", firm_input)
    
    time.sleep(1)

    # ---------- 4️⃣ Set firm name ----------
    debug_print("\n--- SETTING FIRM NAME ---", "INFO")
    test_value = "Goldman Sachs"
    
    # Force the input to update
    success = force_input_update(driver, firm_input, test_value)
    
    if not success:
        debug_print("❌ Failed to set value properly!", "ERROR")
        # One last desperate attempt
        debug_print("Desperate attempt: Using JavaScript to directly set and submit", "WARNING")
        driver.execute_script("""
            var input = arguments[0];
            input.value = arguments[1];
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
        """, firm_input, test_value)
        time.sleep(2)
    
    # Verify the value was set
    current_value = driver.execute_script("return arguments[0].value;", firm_input)
    debug_print(f"Final value in input: '{current_value}'", "INFO")
    
    # Take screenshot for verification
    driver.save_screenshot("debug_screenshot_before_search.png")
    debug_print("Screenshot saved before search", "INFO")
    
    # Wait a moment for Angular to process
    time.sleep(2)

    # ---------- 5️⃣ Click Search button ----------
    debug_print("\n--- CLICKING SEARCH BUTTON ---", "INFO")
    
    # Find search button with multiple strategies
    search_button = None
    search_selectors = [
        (By.CSS_SELECTOR, "button[aria-label='FirmSearch']"),
        (By.XPATH, "//button[contains(@class,'search-button')]"),
        (By.XPATH, "//button[@type='submit']"),
        (By.XPATH, "//button[contains(text(),'SEARCH')]"),
        (By.CSS_SELECTOR, ".btn-accent"),
        (By.XPATH, "//button[contains(@class, 'btn-accent')]")
    ]
    
    for by, selector in search_selectors:
        try:
            elements = driver.find_elements(by, selector)
            if elements:
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        search_button = elem
                        debug_print(f"Found search button with: {selector}", "DEBUG")
                        break
            if search_button:
                break
        except:
            continue
    
    if not search_button:
        debug_print("❌ Could not find search button!", "ERROR")
        return driver
    
    # Try multiple click methods
    click_success = False
    click_methods = [
        ("normal click", lambda: search_button.click()),
        ("JavaScript click", lambda: driver.execute_script("arguments[0].click();", search_button)),
        ("ActionChains click", lambda: ActionChains(driver).move_to_element(search_button).click().perform())
    ]
    
    for method_name, method_func in click_methods:
        try:
            method_func()
            debug_print(f"✅ {method_name} succeeded", "SUCCESS")
            click_success = True
            break
        except Exception as e:
            debug_print(f"❌ {method_name} failed: {e}", "DEBUG")
    
    if not click_success:
        debug_print("❌ All click methods failed for search button!", "ERROR")
        return driver
    
    debug_print("🔍 Search button clicked", "INFO")
    time.sleep(3)

    # ---------- 6️⃣ Wait for results ----------
    debug_print("\n--- WAITING FOR RESULTS ---", "INFO")
    
    # Look for any of these indicators
    result_indicators = [
        "div.table-container",
        ".search-results",
        ".loading-spinner",
        ".crd-number",
        ".firm-result",
        "app-firm-results",
        "[class*='result']",
        "//div[contains(text(), 'results found')]",
        "//div[contains(text(), 'Found')]",
        "//div[contains(text(), 'No results')]",
        "//table",
        ".results-list"
    ]
    
    start_time = time.time()
    timeout = 30
    found = False
    
    while time.time() - start_time < timeout:
        # Check for any results
        for indicator in result_indicators:
            try:
                if indicator.startswith("//"):
                    elements = driver.find_elements(By.XPATH, indicator)
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, indicator)
                
                if elements:
                    for elem in elements[:3]:  # Check first few
                        if elem.is_displayed() and elem.text.strip():
                            debug_print(f"✅ Found indicator: {indicator}", "SUCCESS")
                            debug_print(f"Sample text: {elem.text[:100]}", "INFO")
                            found = True
                            break
                    if found:
                        break
            except:
                continue
        
        if found:
            break
        
        # Check for URL change
        if "search" in driver.current_url or "results" in driver.current_url:
            debug_print(f"URL changed to: {driver.current_url}", "INFO")
            found = True
            break
        
        time.sleep(1)
    
    if not found:
        debug_print("⚠️ Timeout waiting for results", "WARNING")
        driver.save_screenshot("debug_screenshot_timeout.png")
        
        # Check for error message
        try:
            error_msg = driver.find_element(By.XPATH, "//*[contains(text(), 'Please enter')]")
            if error_msg.is_displayed():
                debug_print(f"Final error message: '{error_msg.text}'", "ERROR")
        except:
            pass
    
    debug_print("✅ Script completed!", "SUCCESS")
    return driver


if __name__ == "__main__":
    try:
        driver = open_site()
        debug_print("\n🎯 Script finished. Browser will stay open until you press Enter.", "INFO")
        input("Press Enter to close browser...")
        driver.quit()
    except Exception as e:
        debug_print(f"🔥 Unhandled exception: {e}", "ERROR")
        import traceback
        traceback.print_exc()