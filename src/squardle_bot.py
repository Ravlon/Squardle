import pathlib
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from Squardle.src.LocalStorage import LocalStorage as LS
from Luca.logger import LucaLogger
logger = LucaLogger(__name__)
PATH = pathlib.Path(__file__).parent.parent.absolute()

#setup
def setup(_headless = True):
    try:
        if _headless:
            opts = Options()
            opts.add_argument("-headless")
            assert opts.headless == True
            driver = webdriver.Firefox(options=opts)
            logger.info("Headless WebDriver Initiated")
        else:
            driver = webdriver.Firefox()
            logger.info("Headbound WebDriver Initiated")
        driver.get("https://squaredle.app/")
        message = "WebDriver Connected with {0}".format(driver.title)
        logger.critical(message)
        _set_localstorage(driver)
        return driver
    except:
        message = "WebDriver NOT Connected"
        logger.critical(message)

#set local storage variables
def _set_localstorage(driver):
    
    inst = LS(driver)
    inst.set("squaredle-showedBonusWordDialog","true")
    inst.set("squaredle-didTutorial","skipped")
    inst.set("squaredle-leadebordSort","bonus words")
    inst.set("squaredle-showTimer","True")
    inst.set("squaredle-showedPremiumOnLaunch","True")
    inst.set("squaredle-showedJoinCommunity","True")
    inst.set("squaredle-showedProperNounDialog","True")
    inst.set("squaredle-showedInappropriateDialog","True")

    #refresh driver
    driver.refresh()

#get uuid of session
def get_uuid(driver):
    return LS(driver).get("squaredle-uuid")

#switch back to default frame
def default(driver:webdriver.Firefox):
    driver.switch_to.default_content()

#tutorial skip
def skips_Tutorial(driver):
    #tutorial skip
    try:
        elem = driver.find_element(By.CLASS_NAME,"skipTutorial").click()
        elem = driver.find_element(By.ID, "confirmAccept").click()
        message = "Tutorial skipped"
        logger.debug(message)
    except:
        message = "Tutorial not Skipped"
        logger.error(message)
    
    #switch back to default frame
    default(driver)

#accept cookies
def cookies(driver):
    #cookies popup
    try:
        elem = WebDriverWait(driver, 500).until(EC.presence_of_element_located((By.ID, "cookiesAcceptNecessary")))
        elem.click()
        message = "Necessary Cookies Accepted"
        logger.debug(message)
    except:
        message = "Cookies not accepted"
        logger.warning(message)
    
    #return to default frame
    default(driver)

#signin
def old_signin(driver, credentials):
    try:
        #signin popup
        elem = driver.find_element(By.ID, "drawerBtn").click()
        elem = driver.find_element(By.ID, "drawerSignIn").click()

        #signin form
        elem = driver.find_element(By.CLASS_NAME, "signInBtn").click()

        #email
        elem = driver.find_element(By.ID, "signInEmail")
        elem.clear()
        elem.send_keys(credentials["email"])

        #password
        elem = driver.find_element(By.ID, "signInPassword")
        elem.clear()
        elem.send_keys(credentials["password"])

        #submit form
        elem = driver.find_element(By.ID, "signInSubmit").click()

        #close signin popup
        try:
            elem = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.LINK_TEXT, "close this window")))
            elem.click()
        except:
            message = "Unable to Exit Login Window"
            logger.warning(message)
        
        message = "Successful Login | User: '{}'".format(credentials["email"])
        logger.info(message)
    except:
        message = "Login Unsuccessful"
        logger.warning(message)
    
    #switch back to default frame
    default(driver)
def signin(driver,credentials):#make it more stable
    #set necessary info in Local Storage for signin
    inst = LS(driver)
    inst.set("squaredle-email",credentials["email"])
    inst.set("squaredle-name",credentials["username"])
    inst.set("squaredle-userId",credentials["userId"])
    inst.set("squaredle-uuid",credentials["uuid"])

    #refresh page
    driver.refresh()

def popup_mgr(driver,pop_ups = []):
    if not(pop_ups):
        pop_ups = driver.find_elements(By.CLASS_NAME,"popup")
    for e in pop_ups:
        if e.is_displayed():
            name = e.get_dom_attribute("id")
            message = f"PopUp with ID '{name}' is open"
            logger.warning(message)
            try:
                e.find_element(By.CLASS_NAME,"closeBtn").click()
                logger.warning("Pop Up Closed")
            except:
                logger.error("Pop Up was not closed")
            break

#write word attempts
def attempt(driver, words, bonus_word, invalid_words):
    popups = driver.find_elements(By.CLASS_NAME,"popup")
    board = driver.find_element(By.CLASS_NAME,"letters")
    focus = ActionChains(driver).move_to_element(board)
    for w in words:
        if not(w==bonus_word or w in invalid_words):
            if EC.visibility_of_any_elements_located(popups):
                popup_mgr(driver,popups)
            focus.send_keys(w,Keys.ENTER).perform()
        else:
            continue
    focus.send_keys(bonus_word, Keys.ENTER).perform()

# def getLeaderboard(driver, bonus = True, speed = False, accuracy=False):
#     #get Leaderboards
#     ...

def getTime(driver):
    popup_mgr(driver)
    return driver.find_element(By.ID,"timer").text

def max_word(driver):
    return driver.find_element(By.ID,"maxWordCount").text