from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

Base = declarative_base()


class RestaurantIlan(Base):
    __tablename__ = 'restaurant_ilan'
    id = Column(Integer, primary_key=True)
    shopName = Column(Text)
    shopId = Column(Integer)
    shopUrl = Column(String(100))
    shopStatus = Column(String(10))

    # review = relationship("Review", order_by="Review.id")

    def __init__(self, shopName, shopId, shopUrl, shopStatus):
        self.shopName = shopName
        self.shopId = shopId
        self.shopUrl = shopUrl
        self.shopStatus = shopStatus

    def __repr__(self):
        return "RestaurantIlan('{}','{}', '{}','{}')".format(
            self.shopName,
            self.shopId,
            self.shopUrl,
            self.shopStatus
        )


class Review(Base):
    __tablename__ = 'shop_review'
    id = Column(Integer, primary_key=True)
    shopId = Column(Integer)
    reviewReplyCount = Column(Integer)
    reviewDatetime = Column(DateTime)
    reviewThumbsUp = Column(String(100))
    reviewWatch = Column(String(10))
    reviewId = Column(Integer)
    reviewAuthor = Column(String(50))
    reviewContent = Column(Text)


class ShopDetail(Base):
    __tablename__ = 'shop_detail'
    id = Column(Integer, primary_key=True)
    shopId = Column(Integer)
    SDCategory = Column(String(10))
    SDConsumption = Column(Integer)
    SDTelephone = Column(String(20))
    SDAddress = Column(String(100))
    SDRate = Column(Integer)
    SDRateCount = Column(Integer)
    SDWatchCount = Column(Integer)
    SDBookmarkCount = Column(Integer)
    SDDeliciousRate = Column(Integer)
    SDServiceRate = Column(Integer)
    SDEnvRate = Column(Integer)


class ReviewReply(Base):
    __tablename__ = 'review_reply'
    id = Column(Integer, primary_key=True)
    reviewId = Column(Integer)
    replyUser = Column(String(50))
    replyContent = Column(Text)
    replyDatetime = Column(DateTime)


def load_session():
    # metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def create_tables():
    session = load_session()
    Base.metadata.create_all(engine)
    session.commit()


def store_shop_data(data_list):
    session = load_session()
    for data in data_list:
        shop = RestaurantIlan(shopName=data['name'], shopId=data['id'], shopUrl=data['url'], shopStatus=data['status'])
        session.add(shop)
    session.commit()


def dump_shop_id():
    session = load_session()
    id_list = []
    for shop in session.query(RestaurantIlan):
        id_list.append(shop.shopId)
    session.close()
    return id_list


def store_shop_detail(data_list):
    session = load_session()
    shop_detail = ShopDetail(
        shopId=data_list['shop_id'],
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
    session.close()


def store_review_reply(id, data_list):
    session = load_session()
    for data in data_list:
        reply = ReviewReply(
            reviewId=id,
            replyUser=data['reply_user'],
            replyContent=data['reply_content'],
            replyDatetime=data['reply_time']
        )
        session.add(reply)
    session.commit()
    session.close()


if __name__ == '__main__':
    dump_shop_id()
