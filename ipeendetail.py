import requests
from bs4 import BeautifulSoup
import time

TEST_URL = 'http://www.ipeen.com.tw/shop/40797'
BASE_URL = 'http://www.ipeen.com.tw'
PARSER = 'html.parser'
DEV_URL = 'http://www.ipeen.com.tw/search/ilan/000/1-0-0-0/'


def extract_info(tag, status):
    info_dict = {}
    shop = tag['href'].split('-', 1)
    shop_name = shop[1]
    shop_id = shop[0].split('/')[2]
    shop_url = BASE_URL + shop[0]
    if isinstance(status, type(None)):
        status_flag = 'Normal'
    elif status.text == '【已搬遷】':
        status_flag = 'Moved'
    elif status.text == '【已歇業】':
        status_flag = 'Closed'
    else:
        status_flag = status.text

    info_dict['name'] = shop_name
    info_dict['id'] = shop_id
    info_dict['url'] = shop_url
    info_dict['status'] = status_flag
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
    result = []
    base_url = url
    page_counter = 0
    print(">>Fetching...")
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

            #
            sections = soup.find_all('div', class_='serShop')

            for section in sections:
                name_tag = section.find('a', attrs={"data-label": "店名"})
                status = section.find('span', class_='status')

                result.append(extract_info(name_tag, status))

        else:
            print("error:", list_request.status_code)
            break

        time.sleep(2)
        url = base_url + '?p=' + str(page_counter + 1)

        # break timer
        if page_counter is grab_count and grab_count is not 0:
            break
    return result


def extract_int(string):
    if not isinstance(string, type(None)):
        preprocessed_string = str(string).replace(",", "")
        for s in preprocessed_string.split():
            if s.isdigit():
                return s


def get_shop_detail(shop_id):
    result = {}
    shop_url = BASE_URL + '/shop/' + str(shop_id)
    list_request = requests.get(shop_url)
    if list_request.status_code == requests.codes.ok:
        soup = BeautifulSoup(list_request.content, PARSER)

        info_section = soup.find('div', class_='info')  # get page info section first

        result['shop_name'] = info_section.find('span', attrs={"itemprop": "name"}).text
        result['shop_category'] = info_section.find('a', attrs={"data-action": "up_small_classify"}).text
        result['shop_consumption'] = extract_int(info_section.find('p', class_="cost i"))
        result['shop_telephone'] = info_section.find('a', attrs={"data-action": "up_phone"}).text
        result['shop_address'] = info_section.find('a', attrs={"data-action": "up_address"}).text.strip()
        result['shop_rate'] = info_section.find('span', attrs={"itemprop": "ratingValue"}).text
        result['shop_rate_count'] = info_section.find('em', attrs={"itemprop": "ratingCount"}).text

        scalar_section = info_section.find('div', class_='scalar')  # tricky part

        result['shop_watch_count'] = extract_int(scalar_section.contents[5].text)  # wtf
        result['shop_bookmark_count'] = extract_int(scalar_section.contents[7].text)  # MAGIC!

        other_rating = soup.find('dl', class_="rating").contents  # new section

        result['delicious_rate'] = other_rating[3].find('meter')['value']  # ????
        result['service_rate'] = other_rating[7].find('meter')['value']
        result['env_rate'] = other_rating[11].find('meter')['value']

        print("Fetch shop detail success")
        return result

    else:
        print("error:", list_request.status_code)
        return None


# extract review url and review data
def get_shop_review(shop_id):
    result = {}
    tmp_list = []
    page = 1
    counter = 0
    while True:
        review_page = BASE_URL + '/shop/' + str(shop_id) + '/comments?p=' + str(page)
        comment = requests.get(review_page)
        soup = BeautifulSoup(comment.content, PARSER)

        review_list = soup.find('section', class_="review-list")

        articles = review_list.find_all('article', attrs={'itemprop': "review"})
        if len(articles) is 0:
            break
        for article in articles:
            review_url = BASE_URL + article.a['href']

            review_reply_count = extract_int(article.find(attrs={'data-label': "X則回應"}).text)
            review_thumbs_up = extract_int(article.find(attrs={'data-label': "X人好評"}).text)
            review_watch = extract_int(article.find(class_='extended').span.text)
            review_author = article.find('span', attrs={'itemprop': "author"}).text

            print(">>Review link:", review_url)

            result['shop_id'] = shop_id
            review = get_review_content(review_url, review_reply_count, review_thumbs_up, review_watch, review_author)
            tmp_list.append(review)

            counter += 1
        result['review_detail'] = tmp_list
        time.sleep(3)
        page += 1
    print(">>total:", counter)
    print(">>Get review url finish")
    print(result)
    return result


# get review content and get reply content calling review_reply_to_list()
def get_review_content(review_url, review_reply_count, review_thumbs_up, review_watch, review_author):
    result = {}

    review_id = review_url.split('/')[4]

    description_page = requests.get(review_url)
    soup = BeautifulSoup(description_page.content, PARSER)
    descriptions = soup.find('div', class_='description')
    print(">>Reading review")
    # print(">>start of review")
    # print(descriptions.text)
    result['review_id'] = review_id
    result['review_reply_count'] = review_reply_count
    result['review_thumbs_up'] = review_thumbs_up
    result['review_watch'] = review_watch
    result['review_author'] = review_author
    result['review_content'] = descriptions.text.strip()
    data = review_reply_to_list(soup)
    result['review_reply'] = data
    # print(">>Close get_review_content()")
    return result


# return all reply data in list type in a 'single' review page
def review_reply_to_list(tag_soup):
    result = []
    reply_section = tag_soup.find('ul', class_='reply')
    if not isinstance(reply_section, type(None)):
        replies = reply_section.find_all('li')
        for reply in replies:
            data = {}
            user = reply.find('p', class_='name')
            content = reply.find('div', class_='content')
            if isinstance(user, type(None)):
                reply_user = None
            else:
                reply_user = user.a.text
            if isinstance(content, type(None)):
                reply_content = None
            else:
                reply_content = content.text
            # print(reply_user + ":", reply_content)
            data['reply_user'] = reply_user
            data['reply_content'] = reply_content
            result.append(data)
    return result


def useful_user(shop_id):
    result = []
    page = 1
    print('>>List user find useful')
    while True:
        query_page = BASE_URL + '/comment/comment_useful.php?id=' + str(shop_id) + '&p=' + str(page)
        useful_page = requests.get(query_page)
        soup = BeautifulSoup(useful_page.content, PARSER)
        useful_section = soup.find('div', class_='main_people')
        peoples = useful_section.find_all('div', class_='list')
        if len(peoples) is 0:
            print('>>Reached the end')
            break
        for people in peoples:
            result.append(people.next.text)
            # print(people.next.text)
        page += 1
    return result


# TODO get further more data in the page !

if __name__ == '__main__':
    # page_grab(DEV_URL, 0)
    a = get_shop_review(84984)
    print(a)