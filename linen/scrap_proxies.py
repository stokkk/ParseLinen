from bs4 import BeautifulSoup as BSoup



with open('proxies.html', 'rb') as fp:
    data = fp.read()

    soup = BSoup(data.decode(encoding='utf-8'), 'html.parser')

    con =  soup.find_all(class_='three')
    
    with open('http_proxies.txt', 'wb') as wfp:
        for ip in con:
            wfp.write(bytes(ip.text+"\n", encoding="ascii"))