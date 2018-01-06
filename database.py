from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import DOUBLE

# from sqlalchemy import desc

USER = 'root'
PASSWORD = 'root'
HOST = 'localhost'
CHARSET = 'utf8mb4'
DATABASE = 'iPeen'

init_sql = create_engine('mysql+pymysql://{0}:{1}@{2}'.format(USER, PASSWORD, HOST), echo=False)

init_sql.execute('CREATE DATABASE IF NOT EXISTS {0} CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;'.format(DATABASE))

engine = create_engine(
    'mysql+pymysql://{0}:{1}@{2}/{3}?charset={4}'.format(USER, PASSWORD, HOST, DATABASE, CHARSET), echo=False
)

metadata = MetaData()
Base = declarative_base()


# TODO change thumbs up 's data type and inspect the data type set
class RestaurantIlan(Base):
    __tablename__ = 'ilan_restaurant'
    id = Column(Integer, primary_key=True)
    shopName = Column(Text)
    shopId = Column(Integer)
    shopUrl = Column(String(100))
    shopStatus = Column(String(50))
    isFetched = Column(Boolean, default=False)

    # review = relationship("Review", order_by="Review.id")

    # def __init__(self, shopName, shopId, shopUrl, shopStatus):
    #     self.shopName = shopName
    #     self.shopId = shopId
    #     self.shopUrl = shopUrl
    #     self.shopStatus = shopStatus
    #
    # def __repr__(self):
    #     return "RestaurantIlan('{}','{}', '{}','{}')".format(
    #         self.shopName,
    #         self.shopId,
    #         self.shopUrl,
    #         self.shopStatus
    #     )


class Review(Base):
    __tablename__ = 'ilan_shop_review'
    id = Column(Integer, primary_key=True)
    shopId = Column(Integer)
    reviewReplyCount = Column(Integer)
    reviewDatetime = Column(DateTime)
    reviewThumbsUp = Column(String(100))
    reviewWatch = Column(String(50))
    reviewId = Column(Integer)
    reviewAuthor = Column(String(50))
    reviewContent = Column(Text)
    reviewRate = Column(Integer)


class ShopDetail(Base):
    __tablename__ = 'ilan_shop_detail'
    id = Column(Integer, primary_key=True)
    shopId = Column(Integer)
    shopLatitude = Column(DOUBLE, nullable=False, default=0)
    shopLongitude = Column(DOUBLE, nullable=False, default=0)
    SDCategory = Column(String(50))
    SDConsumption = Column(Integer)
    SDTelephone = Column(String(50))
    SDAddress = Column(String(100))
    SDRate = Column(Integer)
    SDRateCount = Column(Integer)
    SDWatchCount = Column(Integer)
    SDBookmarkCount = Column(Integer)
    SDDeliciousRate = Column(Integer)
    SDServiceRate = Column(Integer)
    SDEnvRate = Column(Integer)


class ReviewReply(Base):
    __tablename__ = 'ilan_review_reply'
    id = Column(Integer, primary_key=True)
    reviewId = Column(Integer)
    replyUser = Column(String(50))
    replyContent = Column(Text)
    replyDatetime = Column(DateTime)


class UserLike(Base):
    __tablename__ = 'ilan_user_like'
    id = Column(Integer, primary_key=True)
    reviewId = Column(Integer)
    replyUser = Column(String(50))
    replyContent = Column(Text)
    replyDatetime = Column(DateTime)


def load_session():
    # metadata = Base.metadata
    _session = sessionmaker(bind=engine)
    session = _session()
    return session


def create_tables():
    session = load_session()
    metadata.create_all(engine)
    session.commit()
    session.close()


def store_shop_data(data_list):
    session = load_session()
    for data in data_list:
        shop = RestaurantIlan(shopName=data['name'],
                              shopId=data['id'],
                              shopUrl=data['url'],
                              shopStatus=data['status'],
                              isFetched=False
                              )
        session.add(shop)
    session.commit()
    session.close()


def dump_shop_id():
    session = load_session()
    id_list = []
    for shop in session.query(RestaurantIlan):
        id_list.append(shop.shopId)
    session.close()
    return id_list


def dump_review_shop_id():
    session = load_session()
    id_list = []
    for shop in session.query(Review):
        id_list.append(shop)
    session.close()
    return id_list


def shop_status(shop_id):
    session = load_session()
    query = session.query(RestaurantIlan.shopStatus).filter(RestaurantIlan.shopId == shop_id).first()
    # for query in session.query(RestaurantIlan).filter(RestaurantIlan.shopId == int(id)):
    #     print(query.shopStatus)
    session.close()
    return str(query[0])


def store_shop_detail(data_list):
    session = load_session()
    shop_detail = ShopDetail(
        shopId=data_list['shop_id'],
        shopLatitude=data_list['latitude'],
        shopLongitude=data_list['longitude'],
        SDCategory=data_list['shop_category'],
        SDConsumption=data_list['shop_consumption'],
        SDTelephone=data_list['shop_telephone'],
        SDAddress=data_list['shop_address'],
        SDRate=data_list['shop_rate'],
        SDRateCount=data_list['shop_rate_count'],
        SDWatchCount=data_list['shop_watch_count'],
        SDBookmarkCount=data_list['shop_bookmark_count'],
        SDDeliciousRate=data_list['delicious_rate'],
        SDServiceRate=data_list['service_rate'],
        SDEnvRate=data_list['env_rate'],

    )
    session.add(shop_detail)
    session.commit()
    session.close()


def store_review_data(data_list):
    session = load_session()
    try:
        shop_id = int(data_list['shop_id'])
        for haystack in data_list['review_detail']:
            shop = Review(shopId=shop_id)
            shop.reviewId = int(haystack['review_id'])
            shop.reviewDatetime = haystack['review_datetime'],
            shop.reviewReplyCount = int(haystack['review_reply_count'])
            shop.reviewThumbsUp = int(haystack['review_thumbs_up'])
            shop.reviewWatch = int(haystack['review_watch'])
            shop.reviewAuthor = haystack['review_author']
            shop.reviewContent = haystack['review_content'].strip()
            # call function to store reply data
            store_review_reply(int(haystack['review_id']), haystack['review_reply'])
            session.add(shop)
            session.commit()
    except:
        print('>>Store review fail')
        # shop_id = int(data_list['shop_id'])
        # review_delete(shop_id)
    session.close()


def store_review_reply(shop_id, data_list):
    session = load_session()
    for data in data_list:
        reply = ReviewReply(
            reviewId=shop_id,
            replyUser=data['reply_user'],
            replyContent=data['reply_content'],
            replyDatetime=data['reply_time']
        )
        session.add(reply)
    session.commit()
    session.close()


def shop_trigger_is_fetch(shop_id):
    session = load_session()
    query = session.query(RestaurantIlan).filter(RestaurantIlan.shopId == shop_id)
    query.update({'isFetched': 1})
    session.commit()
    session.close()


def shop_is_fetch_reset(shop_id):
    session = load_session()
    query = session.query(RestaurantIlan).filter(RestaurantIlan.shopId == shop_id)
    query.update({'isFetched': 0})
    session.commit()
    session.close()


def check_is_fetch(shop_id):
    session = load_session()
    query = session.query(RestaurantIlan.isFetched).filter(RestaurantIlan.shopId == shop_id).first()
    # a = query.filter_by(RestaurantIlan.shopStatus).first()
    # a = query.shopId
    # print(query[0])
    session.close()
    return bool(query[0])


def check_shop_id_is_fetch(shop_id):
    session = load_session()
    query = session.query(ShopDetail).filter(ShopDetail.shopId == shop_id).first()
    session.close()
    if query is None:
        return False
    else:
        return True


def dump_comment_ids():
    session = load_session()
    id_list = []
    for shop in session.query(Review.reviewId):
        id_list.append(shop[0])
    session.close()
    return id_list


def patch_update_review_rate(id,rate):
    session = load_session()
    query = session.query(Review).filter(Review.reviewId == id)
    query.update({'reviewRate': rate})
    session.commit()
    session.close()


# def review_last_id():
#     session = load_session()
#     query = session.query(Review.shopId).order_by(Review.id.desc()).first()
#     session.close()
#     return query[0]


def cleanup(shop_id):
    session = load_session()
    try:
        print('>>Delete review id ', shop_id)
        query = session.query(Review).filter(Review.shopId == shop_id).delete()
        print('>>Affected rows:', query)
        session.commit()
    except:
        print('>>Delete review fail on ', shop_id)
    session.close()


# def tool_check_is_fetch():
#     session = load_session()
#     query = session.query(Review).filter()


if __name__ == '__main__':
    # pass
    # shop_trigger_is_fetch(1028564)
    # print(shop_status(42367))
    # a = dump_comment_ids()
    # print(a)
    pass
