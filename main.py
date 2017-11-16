import ipeendetail
import time
import database

DEV_URL = 'http://www.ipeen.com.tw/search/ilan/000/1-0-0-0/'
PARSER = 'html.parser'
BASE_URL = 'http://www.ipeen.com.tw'
ITEM_PER_PAGE = 15


def banner():
    print("#    _ ____                  ____                    _           ")
    time.sleep(0.25)
    print("#   (_)  _ \ ___  ___ _ __  / ___|_ __ __ ___      _| | ___ _ __ ")
    time.sleep(0.25)
    print("#   | | |_) / _ \/ _ \ '_ \| |   | '__/ _` \ \ /\ / / |/ _ \ '__|")
    time.sleep(0.25)
    print("#   | |  __/  __/  __/ | | | |___| | | (_| |\ V  V /| |  __/ |   ")
    time.sleep(0.25)
    print("#   |_|_|   \___|\___|_| |_|\____|_|  \__,_| \_/\_/ |_|\___|_|   ")
    time.sleep(0.25)
    print("#                            by  MT.C                            ")
    time.sleep(0.25)


def main():
    banner()
    # target_url = input("Input a crawling target URL (eg.\"http://www.ipeen.com.tw/search/ilan/000/1-0-0-0/\"):")
    grab_count = input("How many page should grab ? (or \'0\' for all) ")

    data = ipeendetail.page_grab(DEV_URL, int(grab_count))
    database.store_shop_data(data)

if __name__ == '__main__':
    main()
