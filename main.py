# отладить код настроить вызовы исключений
import sys
import requests

import json
from ProxUtil import parse_proxies, parse_proxies_form_file, gen_proxy, test_proxies
from bs4 import BeautifulSoup as BSoup
from HeadersUtil import random_headers
from TextUtil import simplify
from time import sleep
from exceptions import CriticalConnectionError, CriticalProxyError
from selenium.common.exceptions import NoSuchElementException


DEBUG = False
PROXY = False
DOWNLOAD_IMAGES = False
TEST = False
TIMEOUT = 10
GAP = 0.0
PERPAGE = 1
COUNT_LINKS = 2

HEADERS = "Brand;Name;ID;GroupID;Size;Images;Stock;Price;DiscountPrice;color;"
count_products = 0 # кол-во спаршеных страниц продуктов

api_url = r'https://api.trendyol.com/websearchgw/api/infinite-scroll/kadin+{0}?siralama=6&pi={1}&storefrontId=1&culture=tr-TR&userGenderId=1&searchStrategyType=DEFAULT&pId=ljZd49AsB3&scoringAlgorithmId=1&categoryRelevancyEnabled=undefined&isLegalRequirementConfirmed=True'
group_url = r'https://api.trendyol.com/webproductgw/api/productGroup/{0}?storefrontId=1&culture=tr-TR'

categories = [
    'ic-giyim-aksesuar', 'babydoll', 'jartiyer', 'slip', 'sutyen', 'bustiyer', 'kulot',
    'korse', 'atlet--body', 'fantezi-giyim', 'pijama', 'ic-camasiri-takimlari', 'gecelik', 'string',
]

url_http = r'http://free-proxy.cz/ru/proxylist/country/all/http/ping/all'
url_https = r'http://free-proxy.cz/ru/proxylist/country/all/https/ping/all'

list_group_id = set()

def add_group_id(group_id):
    for id in list_group_id:
        if id == group_id:
            return False
    list_group_id.add(group_id)
    return True


def init():
    try:
        with open("http_proxies.txt", "w") as fp:
            for line in parse_proxies(url_http, COUNT_LINKS):
                fp.write(line)
                fp.write("\n")
        fp.close()
        with open("https_proxies.txt", "w") as fp:
            for line in parse_proxies(url_https, COUNT_LINKS):
                fp.write(line)
                fp.write("\n")
        fp.close()
    except NoSuchElementException:
        print("Проблемы с прокси сервером")
        sys.exit(-1)

try:
    with open("config.json", "rb") as fp:
        data = fp.read().decode(encoding='utf-8')
        conf = json.loads(data)

        GAP = float(conf['gap'])
        TIMEOUT = float(conf['timeout'])
        PERPAGE = int(conf['perpage'])
        COUNT_LINKS = int(conf['count-links'])
        HEADERS = conf['headers']
        HEADERS += "\n"
        api_url = conf['api-url']
        categories = conf['categories']

        if conf['test'] == 'yes':
            TEST = True
        if conf['local'] == 'yes':
            DOWNLOAD_IMAGES = True
        if conf['key'] != "1jfksdhg*H@#*FJV:cj2892238hvVCxCKNVDSKLVIW&#@Y@#HGUVDLSAJKHFVSAGASgqhj3gr2rf":
            sys.exit(-10)
        if conf['proxy'] == 'yes':
            PROXY = True
        if conf['debug'] == 'yes':
            DEBUG = True
    fp.close()
except (json.JSONDecodeError, IOError):
    print(">>> Невозможно открыть файл config.json. Возможно он используется в другом приложении или поврежден.")
    sys.exit(-1)


if PROXY:
    init()

https_proxies = parse_proxies_form_file(path_='https_proxies.txt')
http_proxies = parse_proxies_form_file(path_='http_proxies.txt')


def get_response(url):
    for http, https in zip(http_proxies, https_proxies):
        proxy = gen_proxy(http, https)
        with requests.Session() as sess:
            try:
                resp = sess.get(url, timeout=TIMEOUT,
                                headers=random_headers(), proxies=proxy)
                resp.raise_for_status()  # raise HTTPError
                return resp # response
            except requests.ConnectionError:
                if DEBUG:
                    print("\n>>> (ConnectionError) Ошибка подключения. ip-address - %s" % proxy['http'])
            except requests.HTTPError as http_err:
                if DEBUG:
                    print("\n>>> (HTTPError) Код ошибки %d" % http_err.response.status_code)
            except requests.Timeout:
                raise CriticalConnectionError

    raise CriticalProxyError

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

# parse
def parse_info(resp,path):
    picdomain = r'https://cdn.dsmcdn.com/'

    static = resp.text
    phrase = "window.__PRODUCT_DETAIL_APP_INITIAL_STATE__ = "
    try:
        json_ = static[static.find(phrase) + len(phrase):]  # обрезает часть js-кода в которой содержится
        json_ = json.loads(simplify(json_[:json_.find("</script>")])[:-1])  # json и парсит его.
    except json.JSONDecodeError as je:
        if DEBUG:
            print("\n>>> (JSONDecodeError) Содержимое ответа resp.content:\n%s" % resp.text)
    with open(path, '+ab') as fp:
        try:
            # unpack json
            prod = json_['product']
            for variant in prod['variants']:
                stock = "instock" if variant['stock'] is None else "outstock"
                size = variant['attributeValue']
                price = variant['price']['originalPrice']['value']
                discount = variant['price']['discountedPrice']['value']
                group_id = prod['productGroupId']
                description = simplify(BSoup(prod['description'], 'html.parser').text)
                name = prod['name']
                brand = prod['brand']['name']
                color = prod['color']
                barcode = variant['barcode']
                if DOWNLOAD_IMAGES:
                    images = ','.join(
                        download_image([picdomain + ipath for ipath in prod['images']]))
                else:
                    images = ','.join([picdomain + ipath for ipath in prod['images']])

                global count_products
                count_products += 1

                # writing into csv file
                fp.write(bytes(
                    f"{brand};{name};{barcode};{group_id};{size};{color};{stock};{price};{discount};{description};{images};\n"
                    , encoding="utf-8"))

                print(f'\rЗагружено {count_products} вариантов товаров . . .', end='')
        except KeyError:
            if DEBUG:
                print(">>> (KeyError) Содержимое ответа:\n %s" % str(json_))


def parse_json_pack(data,path):
    domain = r'https://www.trendyol.com'

    if data['statusCode'] == 200:
        data = data['result']['products']
        if len(data) == 0:
            return True

        for prod in data:
            link = domain + prod['url']
            resp = get_response(url=link)
            parse_info(resp,path)
            sleep(GAP)
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
            if DEBUG:
                print(f"\nКатегория '{category}' страница №{i}.")
                print("*" * 60)
            resp = get_response(url)
            sleep(GAP)
            # попытка парсинга блока json
            end = parse_json_pack(resp.json(), path=path_)
            if end is True:
                return
            else:
                i += PERPAGE
    except CriticalConnectionError:
        print("\n>>> Сервер не отправил никаких данных в отведенное время.")
        input("\n>>> Пожалуйста проверьте интернет соединение.")
        sys.exit(-1)
    except CriticalProxyError:
        input("""Нету надежных прокси серверов. Пожалуйста добавьте ip-адреса в файлы http_proxies.txt и https_proxies.txt""")
        sys.exit(-1)

# тестирование проксей
if TEST:
    http_proxies, https_proxies = test_proxies(http_proxies, https_proxies)

# print configuration
print()
print('*' * 60)
print("configuration of this program")
print()
print(
    f"PROXY: {PROXY}\nDEBUG: {DEBUG}\nTIMEOUT: {TIMEOUT}\nGAP:{GAP}\nCOUNT_OF_PROXY_ADDRESS: {len(https_proxies)}\nCOUNT_PAGE_FOR_ONE_TIME: {PERPAGE}\nDOWNLOAD IMAGES: {DOWNLOAD_IMAGES}")
print(api_url)
print("Список категорий:\n",categories)
print("Заголовки таблицы: %s\n" % HEADERS)
print()
print('*' * 60)

# start
if https_proxies and https_proxies:
    # for url in urls:
    #     parse_info(get_response(url), r"data/out.csv")
    for categ in categories:
        parse(categ)
else:
    print("""Нету надежных прокси серверов. Пожалуйста добавьте ip-адреса в файлы http_proxies.txt и https_proxies.txt""")
sys.exit(0)




