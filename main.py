"""Squaredle Bot"""
import Squardle.src.credential_handler as CH
import Squardle.src.squardle_bot as SB
import Squardle.src.squardle_solver as SS
import Squardle.src.board_parser as BP
import pathlib
from Luca.logger import LucaLogger
logger = LucaLogger(__file__)

def init_LOG():

    PATH = pathlib.Path(__file__).parent.absolute()
    LOG_PATH = PATH.joinpath("Squaredle.log")

    #log_file init
    logger.new_time_rotator(LOG_PATH)
    SB.logger.new_time_rotator(LOG_PATH)
    SS.logger.new_time_rotator(LOG_PATH)
    BP.logger.new_time_rotator(LOG_PATH)
    CH.logger.new_time_rotator(LOG_PATH)

    #telegram log init
    ...

def main(solution:list, bonus, invalid):
    #set up of driver
    credentials = CH.getcredentials("SQUAREDLE")
    driver = SB.setup(_headless = False)
    SB.cookies(driver)
    SB.signin(driver,credentials)

    #quick solution
    SB.attempt(driver= driver, words= solution, bonus_word= bonus, invalid_words =invalid)
    
    #get Timer of the game
    message = "Timer: {0}".format(SB.getTime(driver))
    logger.info(message)

    #long solution
    long_solution, bonus, invalid = SS.squardle_solver(quick_solution=False, quick_list=solution)
    SB.attempt(driver= driver, words= long_solution, bonus_word= bonus, invalid_words= invalid)

    #get UUID of Account
    message = f"UUID: {SB.get_uuid(driver)}"
    logger.critical(message)
    driver.close()

if __name__ == "__main__":
    init_LOG()
    quick_solution, bonus_word, invalid_words = SS.squardle_solver(quick_solution=True)
    main(quick_solution, bonus_word, invalid_words)
# https://betterstack.com/community/guides/linux/cron-jobs-getting-started/