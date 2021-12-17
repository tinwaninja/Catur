import chess
import chess.engine
import chess.pgn
import random
import os
import re
import time
from configparser import ConfigParser
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

#Modes: bullet, blitz, rapid. Bullet for fast paced 1 minute matches, blitz for 3-5 minute matches, rapid for a 10+ minute match.
mode = 'blitz'
user = ''
#Get engine location:
current_directory = os.path.abspath(__file__)
engine_executable = "/engine/stockfish.exe"
stockfish_location = current_directory[:-9] + engine_executable
account_location = current_directory[:-8] + "account.txt"
total_opponents_found = 0
total_wins = ""
#Get account credentials:
def credentials():
    global user
    with open(account_location, "r") as f:
        user = f.readline().strip()
        password = f.readline().strip()
        password = f.readline().strip()
    if not user and not password:
        print("Username / password not found in account.txt")
        user = input("username: ")
        password = input("password: ")
    return [user, password]

#Setup firefox's marionette (Selenium/WebDriver):
def open_selenium():
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0")
    gecko_location = current_directory[:-8] + "geckodriver.exe"
    driver = webdriver.Firefox(profile, executable_path=gecko_location)
    driver.get("https://www.chess.com/login")
    return driver

#Login:
def enter(driver, user, password):
    form_user = driver.find_element_by_id("username")
    form_user.send_keys(user)
    form_password = driver.find_element_by_id("password")
    form_password.send_keys(password)
    form_password.send_keys(Keys.RETURN)
    time.sleep(5)
    driver.get("https://www.chess.com/live")

#Create PGN notation:
def create_notation():
    notation_location = current_directory[:-8]+"history/pgn.pgn"
    open(notation_location, "w+").close
    return notation_location

#Detect board movement:
def board_movement(driver, movement_location):
    colours = [1, 0]
    next_move = ""
    colour = colours[movement_location%2]
    location = (movement_location+1)//2
    xpath = f"/html/body/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[{location}]/span[{colour+2}]/span[contains(@class, 'vertical-move-list-clickable')]"
    WebDriverWait(driver, 120).until(
    EC.presence_of_element_located((By.XPATH, xpath))
    )
    move = driver.find_element_by_xpath(xpath)
    print(movement_location, move.text)

    if move.text[0].isdigit():
        print("GAME FINISHED")
        return
    if movement_location % 2 == 1:
        return str(location) + "." + move.text + " "
    else:
        return move.text + " "

#Look for the best move:
def search_best_move(engine, notation, depth):
    with open(notation, "r") as f:
        game = chess.pgn.read_game(f)
        board = chess.Board()
        for move in game.mainline_moves():
            board.push(move)
        best_move = engine.play(board, chess.engine.Limit(depth=depth)).move
        return best_move

#Skip aborted game:
def skip_aborted():
    try:
        game_finished = driver.find_element_by_class_name("game-over-dialog-content")
        if game_finished:
            try:
                time.sleep(5)
                new_game = driver.find_element_by_class_name("game-over-button-button").click()
                print("Game aborted, skipping...")
                time.sleep(1)
                driver.get("https://www.chess.com/live")
            except:
                pass
    except:
        pass

    #Game resigned by opponent:
    try:
        game_resigned = driver.find_element_by_class_name("game-over-header-userWon")
        if game_resigned:
            try:
                time.sleep(5)
                new_game = driver.find_element_by_class_name("game-over-button-button").click()
                print("Skip game karena lawan game_resigned")
                time.sleep(1)
                driver.get("https://www.chess.com/live")
            except:
                pass
    except:
        pass

#Main game:
def main_game(driver, engine, automation_main, depth, colour):
    global mode, total_wins
    notation = create_notation()
    time.sleep(1)
    try:
        if "win 0" not in total_wins:
            if colour == 'white':
                colour_box(driver, 'e2e4')
                engine_movement(driver)

        for movement_location in range(1,500):
            skip_aborted()
            if movement_location == 1 or movement_location == 2:
                if "win 0" in total_wins:
                    print("Our opponent is too weak, aborting match in 25 seconds.")
                    total_wins = ""
                    time.sleep(25)
                    return
            next_move = board_movement(driver, movement_location)
            with open(notation, "a") as f:
               f.write(next_move)
            best_move = search_best_move(engine, notation, depth)
            if((colour == 'white' and movement_location % 2 == 0) or (colour == 'black' and movement_location % 2 == 1)):
                if mode == 'bullet':
                    if movement_location <= 15:
                        delay_time = random.uniform(0.05,0.10)
                        print('Waiting: ', delay_time,'seconds')
                        time.sleep( delay_time )
                    if movement_location >= 15:
                        delay_time = random.uniform(0.05,0.25)
                        print('Waiting: ', delay_time,'seconds')
                        time.sleep( delay_time )
                if mode == 'blitz':
                    if movement_location <= 15:
                        delay_time = random.uniform(0.05,0.25)
                        print('Waiting: ', delay_time,'seconds')
                        time.sleep( delay_time )
                    if movement_location >= 15:
                        delay_time = random.uniform(0.05,1.25)
                        print('Waiting: ', delay_time,'seconds')
                        time.sleep( delay_time )
                if mode == 'rapid':
                    if movement_location <= 15:
                        delay_time = random.uniform(0.05,1.25)
                        print('Waiting: ', delay_time,'seconds')
                        time.sleep( delay_time )
                    if movement_location >= 15:
                        delay_time = random.uniform(0.05,2.25)
                        print('Waiting: ', delay_time,'seconds')
                        time.sleep( delay_time )
                colour_box(driver, best_move)
                engine_movement(driver)
                ambil_promosi(driver, best_move)

    except:
        return

#Search by colour:
def search_colour(driver, automation_main):
    global total_opponents_found, total_wins
    while (1):
        try:
            if automation_main:
                try:
                    check = driver.find_element_by_class_name("game-over-dialog-content")
                    print("Checking if the match is over:")
                    if check:
                        try:
                            game_finished = driver.find_element_by_class_name("game-over-button-seeking")
                            print("Waiting for an opponent...")
                        except:
                            time.sleep(2)
                            try:
                                rematch = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[4]/div[2]/div/div[4]/button[2]").text
                                if rematch != 'Rematch':
                                    sebelumnya_kalah = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[4]/div[2]/div/div[1]/h3").text
                                    if "You Won" in sebelumnya_kalah:
                                        if "win 0" not in total_wins:
                                            #Accept rematch if both players are equal:
                                            rematch = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[4]/div[2]/div/div[4]/button[2]").click()
                                            print("Aceepting rematch because we are equal opponents.")
                                        else:
                                            #Reject rematch because players aren't equal:
                                            rematch = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[4]/div[2]/div/div[4]/button[1]").click()
                                            print("Rejecting rematch because we are not equal opponents.")
                                    else:
                                        rematch = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[4]/div[2]/div/div[4]/button[1]").click()
                                        print("Rejecting rematch because our opponent is too strong.")
                            except:
                                time.sleep(2)
                                find_new_game = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[4]/div[2]/div/div[4]/button[1]").click()
                                if find_new_game:
                                    print("Trying to find a new game...")
                            try:
                                new_game = driver.find_element_by_class_name("game-over-button-button").click()
                                print("Trying to find a new game...")
                            except:
                                try:
                                    time.sleep(1)
                                    driver.find_element_by_xpath("//li[@data-tab='challenge']").click()
                                    driver.find_element_by_class_name("quick-challenge-play").click()
                                except:
                                    pass
                except:
                    try:
                        check = driver.find_element_by_class_name("quick-challenge-play").click()
                        print("Trying to find a new game...")
                    except:
                        pass
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'draw-button-component')))
            break
        except TimeoutException:
            print("Waiting for match: ",total_opponents_found," to start.")
            total_opponents_found += 1
            if(total_opponents_found > 8):
                total_opponents_found = 0
                try:
                    find_new_game = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[4]/div[2]/div/div[4]/button[1]").click()
                    if find_new_game:
                        print("Trying to find a new game...")
                except:
                    pass
                driver.get("https://www.chess.com/live")

    component = driver.find_elements_by_class_name("chat-message-component")
    try:
        if('warn-message-component' in component[-1].get_attribute('class')):
            colour_mentah = component[-2]
        else:
            colour_mentah = component[-1]
        total_wins = colour_mentah.text
        print(colour_mentah.text)
    except:
        return
    colour_user = re.findall(r'(\w+)\s\(\d+\)', colour_mentah.text)

    white_check = colour_user[0]

    global user
    global mode
    print('Selected game mode is: ' + mode)
    if white_check == user:
        print(user + ' is playing as white.')
        return "white"
    else:
        print(user + ' is playing as black')
        return "black"

#Move for current colour:
def colour_box(driver, best_move):
    #Highlight piece boxes:
    box_start_pos = str(best_move)[:2]
    box_dest_pos = str(best_move)[2:]
    #Piece movement:
    location_start = str(0) + str(ord(box_start_pos[0])-96) + str(0) + box_start_pos[1]
    location_dest = str(0) + str(ord(box_dest_pos[0])-96) + str(0) + box_dest_pos[1]
    driver.execute_script("""
    element = document.createElement('div');
    element.setAttribute("id", "highlight1");
    style1 = "background-color: rgb(255,0,0); opacity: 0.5;"
    class1 = "square square-{location_start} marked-square"
    element.setAttribute("style", style1)
    element.setAttribute("class", class1)
    document.getElementById("game-board").appendChild(element)
    element = document.createElement('div');
    element.setAttribute("id", "highlight2");
    style2 = "background-color: rgb(0,255,255); opacity: 0.5;"
    class2 = "square square-{location_dest} marked-square"
    element.setAttribute("style", style2)
    element.setAttribute("class", class2)
    document.getElementById("game-board").appendChild(element)
    """.format(location_start = location_start, location_dest = location_dest))

#Do engine's movement:
def engine_movement(driver):
    element = driver.find_element(By.XPATH, '//*[@id="highlight1"]')
    ActionChains(driver).move_to_element_with_offset(element, 0, 2).click().perform()
    time.sleep(0.05)
    element = driver.find_element(By.XPATH, '//*[@id="highlight2"]')
    ActionChains(driver).move_to_element_with_offset(element, 0, 2).click().perform()
    return

#Write config:
def set_config():
    pengaturan = ConfigParser()
    pengaturan['DEFAULT'] = {'depth': '7',
                         'autoStart': '0'}
    with open('config.ini', 'w') as f:
        pengaturan.write(f)

#Open config:
def get_config():
    pengaturan = ConfigParser()
    pengaturan.read('config.ini')
    depth = int(pengaturan['DEFAULT']['depth'])
    automation_main = int(pengaturan['DEFAULT']['autoStart'])
    return depth, automation_main

#Play game:
def main():
    driver = open_selenium()
    user, password = credentials()
    enter(driver, user, password)
    engine = chess.engine.SimpleEngine.popen_uci(stockfish_location)
    play_again = 1
    depth, automation_main = get_config()
    while play_again:
        skip_aborted()
        colour = search_colour(driver, automation_main)
        main_game(driver, engine, automation_main, depth, colour)
        if automation_main:
            play_again = 1
        else:
            print("Press enter once a new game has started for the engine to start playing.")
            input("Or press CTRL+C to quit.")
    driver.close()
    engine.close()

if __name__ == "__main__":
    main()
