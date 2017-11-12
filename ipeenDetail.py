import requests
from bs4 import BeautifulSoup
import time

TEST_URL = 'http://www.ipeen.com.tw/shop/40797'
BASE_URL = 'http://www.ipeen.com.tw'
PARSER = 'html.parser'
DEV_URL = 'http://www.ipeen.com.tw/search/ilan/000/1-0-0-0/'
ITEM_PER_PAGE = 15


def shop_info(tag):
    info_dict = {}
    shop = tag['href'].split('-', 1)
    shop_name = shop[1]
    shop_id = shop[0].split('/')[2]
    shop_url = BASE_URL + shop[0]

    info_dict['name'] = shop_name
    info_dict['id'] = shop_id
    info_dict['url'] = shop_url
    # print(shop_name)
    # print(shop_id)
    # print(shop_url)
    return info_dict


def page_is_validated(parsed):
    # count page item
    item_count = parsed.find('h2', class_="num").find('b').text
    if int(item_count) is 0:
        return False
    elif int(item_count) is not 0:
        return True
    else:
        print(">>Unknown error check validator")
        return False


# TODO get rid of commercial ad
# Return type:list
def page_grab(url, grab_count):
    base_url = url
    page_counter = 0
    while True:
        page_counter += 1
        if url is None or url == "":  # test mode
            print(">>Dev Mode(or wrong usage?)")
            list_request = requests.get(DEV_URL)
        else:  # production mode
            list_request = requests.get(url)

        print(">>Page Count:", page_counter)
        print(">>Getting:", url)
        if list_request.status_code == requests.codes.ok:
            soup = BeautifulSoup(list_request.content, PARSER)

            if not page_is_validated(soup):
                print(">>End of page")
                break

            name_tags = soup.find_all('a', attrs={"data-label": "店名"})

            for name_tag in name_tags:
                shop_name = shop_info(name_tag)
                print(shop_name)

        else:
            print("error:", list_request.status_code)
            break

        time.sleep(4)
        url = base_url + '?p=' + str(page_counter + 1)

        # break timer
        if page_counter is grab_count and grab_count is not 0:
            break


def get_shop_detail(shop_url):
    list_request = requests.get(shop_url)
    if list_request.status_code == requests.codes.ok:
        soup = BeautifulSoup(list_request.content, PARSER)

        info_section = soup.find('div', class_='info')  # get page info section first

        shop_name = info_section.find('span', attrs={"itemprop": "name"}).text
        shop_category = info_section.find('a', attrs={"data-action": "up_small_classify"}).text
        shop_consumption = info_section.find('p', class_="cost i")
        shop_telephone = info_section.find('a', attrs={"data-action": "up_phone"}).text
        shop_address = info_section.find('a', attrs={"data-action": "up_address"}).text
        shop_rate = info_section.find('span', attrs={"itemprop": "ratingValue"}).text
        shop_rate_count = info_section.find('em', attrs={"itemprop": "ratingCount"}).text

        scalar_section = info_section.find('div', class_='scalar')  # tricky part

        shop_watch_count = scalar_section.contents[5].text  # wtf
        shop_bookmark_count = scalar_section.contents[7].text  # MAGIC!

        other_rating = soup.find('dl', class_="rating").contents  # new section

        delicious_rate = other_rating[3].find('meter')['value']  # ????
        service_rate = other_rating[7].find('meter')['value']
        env_rate = other_rating[11].find('meter')['value']

        # print(other_rating)

    else:
        print("error:", list_request.status_code)


def get_review_url(shop_url):
    page = 1
    counter = 0
    while True:
        review_page = shop_url + '/comments?p=' + str(page)
        comment = requests.get(review_page)
        soup = BeautifulSoup(comment.content, PARSER)

        review_list = soup.find('section', class_="review-list")

        articles = review_list.find_all('article', attrs={'itemprop': "review"})
        if len(articles) is 0:
            break
        for article in articles:
            review_url = BASE_URL + article.a['href']

            review_reply_count = article.find(attrs={'data-label': "X則回應"}).text
            review_thumbs_up = article.find(attrs={'data-label': "X人好評"}).text
            review_watch = article.find(class_='extended').span.text
            review_author = article.find('span', attrs={'itemprop': "author"}).text
            # review_reply = review_reply_to_list(article)

            print(">>Review link:", review_url)
            get_review_content(review_url)
            counter += 1
        time.sleep(2)
        page += 1
    print(">>total:", counter)
    print(">>Get review url finish")


def review_reply_to_list(tag_soup):
    reply_section = tag_soup.find('ul', class_='reply')
    if not isinstance(reply_section, type(None)):
        replies = reply_section.find_all('li')
        for reply in replies:
            reply_user = reply.find('p', class_='name').a.text
            reply_content = reply.find('div', class_='content').text
            print(reply_user + ":", reply_content)


def get_review_content(shop_url):
    description_page = requests.get(shop_url)
    soup = BeautifulSoup(description_page.content, PARSER)
    descriptions = soup.find('div', class_='description')
    print(">>start of review")
    print(descriptions.text)
    review_reply_to_list(soup)
    print(">>end of review")


def useful_user(shop_id):
    page = 1
    print('>>List user find useful')
    while True:
        query_page = 'http://www.ipeen.com.tw/comment/comment_useful.php?id=' + str(shop_id) + '&p=' + str(page)
        useful_page = requests.get(query_page)
        soup = BeautifulSoup(useful_page.content, PARSER)
        useful_section = soup.find('div', class_='main_people')
        peoples = useful_section.find_all('div', class_='list')
        if len(peoples) is 0:
            print('>>Reached the end')
            break
        for people in peoples:
            print(people.next.text)
        page += 1


# TODO get further more data in the page !

if __name__ == '__main__':
    page_grab(DEV_URL, 0)
