# отладить код настроить вызовы исключений
import sys

import requests
from torpy.http.requests import tor_requests_session
import cfscrape # обход cloudflare

import json
from bs4 import BeautifulSoup as BSoup
from HeadersUtil import random_headers
from TextUtil import simplify
from time import sleep
from exceptions import CriticalConnectionError, CriticalProxyError

import logging

logging.basicConfig(format="[ %(asctime)-15s ] %(url)s %(message)s")
logger = logging.Logger(name='trendyolParser',level=logging.NOTSET)

DEBUG = False
DOWNLOAD_IMAGES = False
TEST = False
TIMEOUT = 10
GAP = 0.0
PERPAGE = 1
MAX_COUNT_PRODUCTS = 300

HEADERS = "Brand;Name;Barcode;GroupID;Size;Images;Stock;Price;DiscountPrice;color;"
count_products = 0 # кол-во спаршеных страниц продуктов

api_url = r'https://api.trendyol.com/websearchgw/api/infinite-scroll/kadin+{0}?siralama=6&pi={1}&storefrontId=1&culture=tr-TR&userGenderId=1&searchStrategyType=DEFAULT&pId=ljZd49AsB3&scoringAlgorithmId=1&categoryRelevancyEnabled=undefined&isLegalRequirementConfirmed=True'
group_url = r'https://api.trendyol.com/webproductgw/api/productGroup/{0}?storefrontId=1&culture=tr-TR'

categories = [
    'ic-giyim-aksesuar', 'babydoll', 'jartiyer', 'slip', 'sutyen', 'bustiyer', 'kulot',
    'korse', 'atlet--body', 'fantezi-giyim', 'pijama', 'ic-camasiri-takimlari', 'gecelik', 'string',
]


list_group_id = set()

def add_group_id(group_id):
    for id in list_group_id:
        if id == group_id:
            return False
    list_group_id.add(group_id)
    return True



# make configuration
try:
    with open("config.json", "rb") as fp:
        data = fp.read().decode(encoding='utf-8')
        conf = json.loads(data)

        GAP = float(conf['gap'])
        TIMEOUT = float(conf['timeout'])
        PERPAGE = int(conf['perpage'])
        HEADERS = conf['headers']
        HEADERS += "\n"
        api_url = conf['api-url']
        categories = conf['categories']

        if conf['local'] == 'yes':
            DOWNLOAD_IMAGES = True
        if conf['key'] != "1jfksdhg*H@#*FJV:cj2892238hvVCxCKNVDSKLVIW&#@Y@#HGUVDLSAJKHFVSAGASgqhj3gr2rf":
            sys.exit(-10)

        if conf['debug'] == 'yes':
            DEBUG = True
            logger.setLevel(level=logging.DEBUG)

    fp.close()
except (json.JSONDecodeError, IOError):
    logging.critical(msg="Невозможно открыть файл config.json. Возможно он используется в другом приложении или поврежден.")
    sys.exit(-1)



def get_response(url):  
    """
    Делает запрос по адресу через сети Tor и возвращает ответ. 
    Обрабатывает исключения.

    Return type -> Response

    Parametrs:
        - url: адрес страницы

    Exceptions:
        - CriticalConnectionError: ошибки подключения на стороне клиента
    """
    logger.debug(msg="trying load page with url - %s" % url)
    with tor_requests_session() as session:
        sess = cfscrape.create_scraper(sess=session, delay=GAP)
        try:
            resp = sess.get(url, timeout=TIMEOUT,
                            headers=random_headers())
            resp.raise_for_status()  # raise HTTPError
            return resp # response
        except requests.ConnectionError:
            logger.debug(msg="'ConnectionError'", extra={'url': url})
        except requests.HTTPError as http_err:
            logger.debug(msg="'HTTPError' Код ошибки - %s" % http_err.response.status_code, extra={'url': url})
        except requests.Timeout:
            raise CriticalConnectionError




def download_image(urls):
    domain = r'https://cdn.dsmcdn.com//'
    path_ = 'data/images/'
    source_paths = []
    for url in urls:
        out_path = path_ + url.partition(domain)[-1].replace('/', '.')
        p = get_response(url)
        with open(out_path, 'wb') as f:
            f.write(p.content)
        f.close()
        source_paths.append(out_path.partition(path_)[-1])
    return source_paths

def find_json(static,start_token="window.__PRODUCT_DETAIL_APP_INITIAL_STATE__ = ", end_token="</script>"):
    """
    Ищет в тексте json по фразе-началу и фразе-концу. 
    Возвращает словарь содержащий json.

    Return type -> dict (json)

    Parameters:
        - static: текст содержащий json
        - start_token: начинающий токен
        - end_token: конечный токен

    Exceptions:
        - JSONDecodeError: ошибка в коде json
    """
    json_ = static[static.find(start_token) + len(start_token):]  # обрезает часть js-кода в которой содержится
    json_ = json.loads(simplify(json_[:json_.find(end_token)])[:-1])  # json и парсит его.
    return json_

# parse
def parse_info(resp,path):
    picdomain = r'https://cdn.dsmcdn.com/'
    json_ = {}
    try:
        json_ = find_json(static=resp.text)
    except json.JSONDecodeError as je:
        logger.debug(msg="'JSONDecodeError' static - %s" % resp.text)
    with open(path, '+ab') as fp:
        try:
            # unpack json
            prod = json_['product']
            name = prod['name']
            brand = prod['brand']['name']
            color = prod['color']
            group_id = prod['productGroupId']
            description = simplify(BSoup(prod['description'], 'html.parser').text)

            for variant in prod['variants']:
                stock = variant['stock']
                size = variant['attributeValue']
                price = variant['price']['originalPrice']['value']
                discount = variant['price']['discountedPrice']['value']
                barcode = variant['barcode']
                if DOWNLOAD_IMAGES:
                    images = ','.join(
                        download_image([picdomain + ipath for ipath in prod['images']]))
                else:
                    images = ','.join([picdomain + ipath for ipath in prod['images']])

                # writing into csv file
                fp.write(bytes(
                    f"{brand};{name};{barcode};{group_id};{size};{color};{stock};{price};{discount};{description};{images};\n"
                    , encoding="utf-8"))

                
        except KeyError as ke:
            logger.debug("'KeyError' Json - %s" % str(json_))


def parse_group(resp, path):
    """
    """
    domain = r'https://www.trendyol.com'
    json_ = {}
    try:
        json_ = find_json(static=resp.text)
    except json.JSONDecodeError as je:
        logger.debug(msg="'JSONDecodeError' static - %s" % resp.text)

    try:
        prod = json_['product']
        url = prod['url']
        id = prod['id']
        productGroupId = prod['productGroupId']

        response = get_response(group_url.format(productGroupId))

        groupId_json = response.json()
        group = groupId_json['result']['slicingAttributes'] # список

        for slic_attrib in group: # словарь
            attributes = slic_attrib['attributes'] # список словарей
            if len(attributes) > 0: # если у товара есть группа, спарсить всю группу
                for attrib in attributes:
                    con = attrib['contents']
                    attrib_url = con[0]['url']
                    link = domain + attrib_url
                    info_resp = get_response(link)
                    parse_info(info_resp,path)
            else: # если нету - только сам товар
                link = domain+url
                info_resp = get_response(link)
                parse_info(info_resp,path)
    except KeyError as ke:
        logger.debug(msg="")

def parse_json_pack(data,path):
    """
    Returns type: bool

    Parameters:
        - data:

        - path:

    Exceptions:
        - No
    """
    domain = r'https://www.trendyol.com'

    if data['statusCode'] == 200:
        data = data['result']['products']
        if len(data) == 0:
            return True

        for prod in data:
            link = domain + prod['url']
            resp = get_response(url=link)
            parse_group(resp,path)
            sleep(GAP)

            global count_products
            count_products += 1
            if count_products > MAX_COUNT_PRODUCTS:
                count_products = 0
                return True   
            print(f'\rФайл [{path}] Загружено {count_products} товаров . . .', end='')
        return False
    else:
        return True

def parse(category):
    i = 1
    path_ = 'data/'+category+'.csv'

    with open(path_, 'wb+') as fp: # print out headers
        fp.write(bytes(HEADERS,encoding='utf-8'))
    try:
        # main loop
        while True:
            url = api_url.format(category, str(i))
            resp = get_response(url)
            sleep(GAP)
            # попытка парсинга блока json
            end = parse_json_pack(resp.json(), path=path_)
            if end is True:
                return
            else:
                i += PERPAGE
    except CriticalConnectionError:
        logger.critical(msg="Сервер не отправил никаких данных в отведенное время.\nПожалуйста проверьте интернет соединение.")
        sys.exit(-1)
    except CriticalProxyError:
        logger.critical("Нету надежных прокси серверов.")
        sys.exit(-1)




links = ['https://ifconfig.me', 'https://vk.com', 'https://trendyol.com', 'https://youtube.com']




# print configuration
print()
print('*' * 60)
print("configuration of this program\n")
print(f"\nDEBUG: {DEBUG}\nTIMEOUT: {TIMEOUT}\nGAP:{GAP}\nCOUNT_PAGE_FOR_ONE_TIME: {PERPAGE}\nDOWNLOAD IMAGES: {DOWNLOAD_IMAGES}")
print(api_url)
print("Список категорий:\n",categories)
print("Заголовки таблицы: %s\n\n" % HEADERS)
print('*' * 60)

# start

for categ in categories:
    parse(categ)







