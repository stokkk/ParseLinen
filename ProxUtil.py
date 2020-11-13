from selenium import webdriver
from HeadersUtil import random_headers
import requests

def gen_proxy(http, https):
    pref = "http://"
    return {'http': pref+http, 'https': pref+https}

def parse_proxies_form_file(path_):
    proxs = []
    with open(path_, 'r') as fp:
        for line in fp:
            proxs.append(line.strip())
    fp.close()
    return proxs

def parse_proxies(proxy_url=r'http://free-proxy.cz/ru/proxylist/country/all/https/ping/all',count=2):
    """\
    Собирает адреса прокси-серверов с сайта http://free-proxy
    Возвращает список кортежей из (ip_address, port)
    Использует webdriver Chrome
    """
    proxs = []
    driver = webdriver.Chrome()
    driver.get(proxy_url)
    pages = driver.find_element_by_class_name('paginator').find_elements_by_tag_name('a')[:-1]
    links = [page.get_attribute('href') for page in pages[:-1]]

    table = driver.find_element_by_id('proxy_list')
    for tr in table.find_elements_by_tag_name('tr'):
        for td in tr.find_elements_by_tag_name('td')[:2]:
            proxs.append(td.text)
        proxs = list(filter(None, proxs))

    driver.close()

    for link in links[:count]:
        driver = webdriver.Chrome()
        print('parse proxies from ', link)
        driver.get(link)
        table = driver.find_element_by_id('proxy_list')
        for tr in table.find_elements_by_tag_name('tr'):
            tmp = []
            for td in tr.find_elements_by_tag_name('td')[:2]:
                tmp.append(td.text)
            tmp = list(filter(None, tmp))
            proxs += tmp
        driver.close()
    return [ ':'.join(addr) for addr in list(zip(proxs[0::2],proxs[1::2])) ]


def test_proxies(https_proxies, http_proxies):

    rhttp = []
    rhttps = []
    print("Starting test are proxies adress . . .")
    for http, https in zip(http_proxies, https_proxies):
        proxy = gen_proxy(http, https)
        try:
            resp = requests.get('https://www.trendyol.com', proxies=proxy, timeout=5, headers=random_headers())
            resp.raise_for_status()
            rhttp.append(http)
            rhttps.append(https)
            print(f"\rЗагружено {len(rhttps)} http и  {len(rhttp)} https адресов.", end='')
        except:
            pass
    http_proxies, https_proxies = rhttp, rhttps
    with open("http_proxies.txt", "w") as fp:
        for ip in http_proxies:
            fp.write(ip+"\n")
    with open("https_proxies.txt", "w") as fp:
        for ip in https_proxies:
            fp.write(ip+"\n")

    return http_proxies, https_proxies
