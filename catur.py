import chess
import chess.engine
import chess.pgn
import random
import os
import time
from configparser import ConfigParser
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

otomatis_main = True
#blitz untuk mengatur kecepatan langkah, True untuk permainan kilat (blitz), False untuk langkah 1-3 detik
blitz = True

#lokasi file
lokasi_file = os.path.abspath(__file__)
lokasi_engine = "/engine/stockfish.exe"
lokasi_stockfish = lokasi_file[:-9] + lokasi_engine
lokasi_akun = lokasi_file[:-8] + "akun.txt"

#kredensial akun
def Kredensial():
    with open(lokasi_akun, "r") as f:
        pengguna = f.readline().strip()
        kata_sandi = f.readline().strip()
    if not pengguna and not kata_sandi:
        print("Nama pengguna / kata sandi tidak tersedia di akun.txt")
        pengguna = input("username: ")
        kata_sandi = input("password: ")
    return [pengguna, kata_sandi]

#selenium
def buka_selenium():
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0")
    gecko_loc = lokasi_file[:-8] + "geckodriver.exe"
    driver = webdriver.Firefox(profile, executable_path=gecko_loc)
    driver.get("https://www.chess.com/login")
    return driver

#masuk
def masuk(driver, pengguna, kata_sandi):
    form_pengguna = driver.find_element_by_id("username")
    form_pengguna.send_keys(pengguna)
    form_katasandi = driver.find_element_by_id("password")
    form_katasandi.send_keys(kata_sandi)
    form_katasandi.send_keys(Keys.RETURN)
    time.sleep(5)
    driver.get("https://www.chess.com/live")  

#buat notasi / pgn
def buat_notasi():
    time_now = datetime.now()
    lokasi_notasi = lokasi_file[:-8]+"history/pgn.pgn"
    open(lokasi_notasi, "w+").close
    return lokasi_notasi

#deteksi langkah gerakan
def deteksi_gerakan(driver, letak_gerakan):
    warnanya = [1, 0]
    gerakan_selanjutnya = ""
    warna = warnanya[letak_gerakan%2]
    lokasi = (letak_gerakan+1)//2
    xpath = f"/html/body/div[3]/div/div[1]/div[1]/div/div[1]/div/div/div[{lokasi}]/span[{warna+2}]/span[contains(@class, 'vertical-move-list-clickable')]"
    WebDriverWait(driver, 120).until(
    EC.presence_of_element_located((By.XPATH, xpath))
    )
    pindah = driver.find_element_by_xpath(xpath)
    print(letak_gerakan, pindah.text)

    if pindah.text[0].isdigit():
        print("GAME SELESAI")
        return
    if letak_gerakan % 2 == 1:
        return str(lokasi) + "." + pindah.text + " "
    else:
        return pindah.text + " "

#mencari langkah terbaik
def cari_terbaik(engine, notasi, depth):
    with open(notasi, "r") as f:
        game = chess.pgn.read_game(f)
        papan = chess.Board()
        for pindah in game.mainline_moves():
            papan.push(pindah)
        terbaik = engine.play(papan, chess.engine.Limit(depth=depth)).move
        return terbaik

#main game
def main_game(driver, engine, otomatis_main, depth):
    global blitz
    if otomatis_main:
        try:
            time.sleep(1)
            permainan_baru = driver.find_element_by_class_name("game-over-button-button").click()
        except:
            time.sleep(1)
            driver.find_element_by_xpath("//li[@data-tab='challenge']").click()
            driver.find_element_by_class_name("quick-challenge-play").click()
        else:
            print("Menunggu pertandingan dimulai")
    notasi = buat_notasi()
    time.sleep(1)
    try:
        for letak_gerakan in range(1,500):
            gerakan_selanjutnya = deteksi_gerakan(driver, letak_gerakan)
            with open(notasi, "a") as f:
                f.write(gerakan_selanjutnya)
            start_time = time.time()
            terbaik = cari_terbaik(engine, notasi, depth)
            end_time = time.time()
            print(end_time-start_time)
            warna_kotak(driver, terbaik)
            if blitz != True:
                time.sleep(random.randint(1,3))
            gerakan_otomatis(driver)
    except:
        return

#suggest warna
def warna_kotak(driver, best_move):
    kotak_awal = str(best_move)[:2]
    kotak_tujuan = str(best_move)[2:]
    lokasi_awal = str(0) + str(ord(kotak_awal[0])-96) + str(0) + kotak_awal[1]
    lokasi_tujuan = str(0) + str(ord(kotak_tujuan[0])-96) + str(0) + kotak_tujuan[1]
    driver.execute_script("""
    element = document.createElement('div');
    element.setAttribute("id", "highlight1");
    style1 = "background-color: rgb(255,0,0); opacity: 0.5;"
    class1 = "square square-{lokasi_awal} marked-square"
    element.setAttribute("style", style1)
    element.setAttribute("class", class1)
    document.getElementById("game-board").appendChild(element)
    element = document.createElement('div');
    element.setAttribute("id", "highlight2");
    style2 = "background-color: rgb(0,255,255); opacity: 0.5;"
    class2 = "square square-{lokasi_tujuan} marked-square"
    element.setAttribute("style", style2)
    element.setAttribute("class", class2)
    document.getElementById("game-board").appendChild(element)
    """.format(lokasi_awal = lokasi_awal, lokasi_tujuan = lokasi_tujuan))
    
#gerakan otomatis
def gerakan_otomatis(driver):
    element = driver.find_element(By.XPATH, '//*[@id="highlight1"]')
    ActionChains(driver).move_to_element_with_offset(element, 0, 2).click().perform()
    time.sleep(0.05)
    element = driver.find_element(By.XPATH, '//*[@id="highlight2"]')
    ActionChains(driver).move_to_element_with_offset(element, 0, 2).click().perform()
    return

#buat pengaturan 
def set_pengaturan():
    pengaturan = ConfigParser()
    pengaturan['DEFAULT'] = {'depth': '7',
                         'autoStart': '0'}
    with open('config.ini', 'w') as f:
        pengaturan.write(f)

#buka pengaturan
def buka_pengaturan():
    pengaturan = ConfigParser()
    pengaturan.read('config.ini')
    depth = int(pengaturan['DEFAULT']['depth'])
    otomatis_main = int(pengaturan['DEFAULT']['autoStart'])
    return depth, otomatis_main

#fungsi main
def main():
    driver = buka_selenium()
    pengguna, kata_sandi = Kredensial()
    masuk(driver, pengguna, kata_sandi)
    engine = chess.engine.SimpleEngine.popen_uci(lokasi_stockfish)
    main_lagi = 1
    depth, otomatis_main = buka_pengaturan()
    while main_lagi:
        main_game(driver, engine, otomatis_main, depth)
        masukan = input("Ketik 'start' untuk lanjut suggest (ketika pertandingan sudah dimulai), atau ketik 'no' untuk keluar: ")
        if masukan == 'no':
            main_lagi = 0
    driver.close()
    engine.close()

if __name__ == "__main__":
    main()