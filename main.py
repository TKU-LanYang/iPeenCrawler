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


class Fire:
    def __init__(self):
        self.id_list = []
        self.grab_count = 1

    def shop_data(self):
        self.get_pages()
        print('>>LAUNCH SHOP DATA GETTER')
        data = ipeendetail.page_grab(DEV_URL, int(self.grab_count))
        print('>>PROCESSING DATA......')
        database.store_shop_data(data)

    def shop_detail(self):
        print('>>LOAD IDS')
        self.load_id()
        if len(self.id_list) is not 0:
            print('>>LAUNCH SHOP DETAIL GETTER')
            for id in self.id_list:
                shop_detail = ipeendetail.get_shop_detail(id)
                database.store_shop_detail(shop_detail)
        else:
            print('ERR : NO ID DATA ! CHECK DATABASE')
            return -1

    def shop_review_reply(self):
        print('>>LOAD IDS')
        self.load_id()
        i = 0
        if len(self.id_list) is not 0:
            print('>>LAUNCH SHOP REPLY & REVIEW GETTER<<')
            for id_chunks in self.chunks(self.id_list, 10):
                i = i + 1
                print('>>Chunk', i)
                for id in id_chunks:
                    if not database.check_is_fetch(id):
                        if database.shop_status(str(id)) == 'Normal':
                            shop_review = ipeendetail.get_shop_review(id)
                            if shop_review is None:
                                print('NO DATA')
                                database.shop_trigger_is_fetch(id)
                            else:
                                database.store_review_data(shop_review)
                                database.shop_trigger_is_fetch(id)
                        else:
                            print("Status Not Normal")
                    else:
                        print('>>Skip ', id)
        else:
            print('ERR : NO ID DATA ! CHECK DATABASE')
            return -1

    def get_pages(self):
        self.grab_count = input("How many page should grab ? (or \'0\' for all) ")

    def load_id(self):
        self.id_list = database.dump_shop_id()

    def auto_pilot(self):
        # self.get_pages()
        self.shop_data()
        self.shop_detail()
        self.shop_review_reply()

    # Create a function called "chunks" with two arguments, l and n:
    def chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]


def main():
    database.create_tables()
    banner()
    print('          ~ MENU ~          ')
    print('1. AUTO MODE')
    print('          ~ MANUAL ~        ')
    print('2. STORE SHOP ONLY')
    print('3. STORE SHOP DETAIL ONLY')
    print('4. STORE REVIEWS & REPLIES ONLY')
    print('CAUTION : YOU MUST HAVE SHOP DATA FIRST ! ')
    option = input('OPTION : ')
    # target_url = input("Input a crawling target URL (eg.\"http://www.ipeen.com.tw/search/ilan/000/1-0-0-0/\"):")
    launch = Fire()
    if option is '1':
        launch.auto_pilot()
    elif option is '2':
        launch.shop_data()
    elif option is '3':
        launch.shop_detail()
    elif option is '4':
        launch.shop_review_reply()
    else:
        return -1


if __name__ == '__main__':
    main()
