"""Squaredle Bot"""
import Squardle.src.credential_handler as CH
import Squardle.src.squardle_bot as SB
import Squardle.src.squardle_solver as SS
import Squardle.src.board_parser as BP
import pathlib
from time import time,ctime
import requests
import json
from Luca.logger import LucaLogger
logger = LucaLogger(__file__)
telegram_message = LucaLogger("Stats Message")

def init_LOG():

    PATH = pathlib.Path(__file__).parent.absolute()
    LOG_PATH = PATH.joinpath("Squaredle.log")

    loggers = [logger,SB.logger,SS.logger,BP.logger,CH.logger]

    #log_file init
    for l in loggers:
        #log_file init
        l.new_time_rotator(LOG_PATH)

    credentials = CH.getcredentials("TELEGRAM")

    for l in loggers:
        #telegram log init
        l.telegram_bot(credentials["token"],credentials["chatID"])
    telegram_message.telegram_bot(credentials["token"],credentials["chatID"])
    
    logger.critical("Log initialised")
    
def result(uuid):
    logger.debug("Request Sync of results")
    url = "https://squaredle.app/api/index.php"
    data = {"op":"requestSync","args":{"uuid":uuid,"game":"squaredle"}}
    response= requests.post(url,json=data,timeout=100)
    if not(response.ok):
        logger.error("Not able to sync results")
    sync_data = response.json()
    todays_data = sync_data["data"]["newState"]["today"]
    found = len(todays_data["words"])
    bonuses = len(todays_data["optionalWords"])
    non_word = todays_data["nonWordCount"]
    puzzle_time = todays_data["ms"]
    return found,bonuses,non_word,puzzle_time
    

def bot():
    #quick solution of board
    quick_start = time()
    solution, bonus, invalid = SS.squardle_solver(quick_solution=True)
    quick_time = time()-quick_start
    
    #set up of driver
    credentials = CH.getcredentials("SQUAREDLE")
    driver = SB.setup(_headless = False)
    SB.cookies(driver)
    SB.signin(driver,credentials)
    max_words = SB.max_word(driver)

    #quick solution
    first_attempt_start = time()
    SB.attempt(driver= driver, words= solution, bonus_word= bonus, invalid_words =invalid)
    first_attempt_time = time()-first_attempt_start
    
    #get Timer of the game
    message = "Timer: {0}".format(SB.getTime(driver))
    logger.info(message)

    #long solution
    long_start = time()
    long_solution, bonus, invalid = SS.squardle_solver(quick_solution=False, quick_list=solution)
    long_time = time()-long_start
    second_attempt_start = time()
    SB.attempt(driver= driver, words= long_solution, bonus_word= bonus, invalid_words= invalid)
    second_attempt_time = time()-second_attempt_start

    #close driver
    driver.close()
    
    found_words, optional_words, non_words, puzzle_time = result(credentials["uuid"])
    puzzle_time = str(int(puzzle_time/60000))+":"+str(int((puzzle_time/1000)%60))
    
    message = """{date}
    User: {username}
    Quick Solution Execution Time: {quick_solver}
    Number of Possible Words: {solution_size}
    Bonus Word: {bonus_word}
    Time to execute quick solution: {quick_execution}
    {timer_message}
    Long Solution Execution Time: {long_solver}
    Number of Possible Words: {long_solution_size}
    Time to executo bonus word solution: {long_execution}
    Result:
        Found Words: {result_valid}/{target_words}
        Found Bonus Words: {result_bonus}
        Invalid Words: {result_invalid}
        Puzzle Time: {result_time}""".format(date = ctime(),
                                             username = credentials["username"],
                                             quick_solver = quick_time,
                                             solution_size = len(solution),
                                             bonus_word = bonus,
                                             quick_execution = first_attempt_time,
                                             timer_message = message,
                                             long_solver = long_time,
                                             long_solution_size = len(long_solution),
                                             long_execution = second_attempt_time,
                                             result_valid = found_words,
                                             result_bonus = optional_words,
                                             result_invalid = non_words,
                                             result_time = puzzle_time,
                                             target_words = max_words
                                             )
    telegram_message.critical(message)
    
def main():
    bot()

if __name__ == "__main__":
    init_LOG()
    main()
# https://betterstack.com/community/guides/linux/cron-jobs-getting-started/