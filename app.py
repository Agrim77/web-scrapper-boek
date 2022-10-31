from flask import Flask
import os

# from types import NoneType
# from currency_converter import CurrencyConverter
from bs4 import BeautifulSoup
import requests

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

'''' BOL '''
@app.route("/bol/<ISBN>")
def getBookFromISBN_BOL(ISBN):
    bolURL = "https://www.bol.com/nl/nl/s/?searchtext="
    page = requests.get(bolURL + str(ISBN))
    soup = BeautifulSoup(page.text, "lxml")
    try:
        response = {
            "title":"",
            "price":"",
            "link": bolURL + str(ISBN)
        }
        content = soup.find_all('div', class_='product-item__content')[0]
        response["title"] = content.find_all('a', class_='product-title')[0].get_text()
        bolPriceSplit = content.find_all(
            'div', class_='product-prices')[0].get_text().split()
        if (bolPriceSplit[0] == 'Niet'):
            response["price"] = bolPriceSplit[0] + ' ' + bolPriceSplit[1]
        else:
            response["price"] = bolPriceSplit[0] + '.' + bolPriceSplit[1]

        response["price"]
        return response
    except Exception as e:
        return "Book not found on bol.com"


'''' BOEKWINKELTJES '''
@app.route("/boekwinkeltjes/<ISBN>")
def getBookFromISBN_BOEK(ISBN):
    boekwinkeltjesURL = 'https://www.boekwinkeltjes.nl/s/?q='
    page = requests.get(boekwinkeltjesURL + str(ISBN))
    soup = BeautifulSoup(page.text, 'lxml')
    try:
        response = {
            "title": "",
            "price": "",
            "link": boekwinkeltjesURL + str(ISBN)
        }
        winkelTitleBlock = soup.find_all('td', class_='table-text')
        response["title"] = ' '.join(winkelTitleBlock[1].find(
            text=True, recursive=False).split())
        response["price"] = soup.find_all('td', class_='price')[
            0].strong.get_text()[2:]

        return response
    except Exception as e:
        return "Book not found on bol.com"


'''' DESLEGTE '''
@app.route("/deslegte/<ISBN>")
def getBookFromISBN_DES(ISBN):
    deslegateURL = "https://www.deslegte.com/boeken/?q="
    page = requests.get(deslegateURL + str(ISBN))
    soup = BeautifulSoup(page.text, 'lxml')
    try:
        response = {
            "title": "",
            "price": "",
            "link": deslegateURL + str(ISBN)
        }
        deslContent = soup.find_all('div', class_='book')[0]
        response["title"] = deslContent.h3.get_text()
        try:
            response["price"] = deslContent.find_all(
                'meta', attrs={"itemprop": "lowPrice"})[0]["content"]
        except:
            response["price"] = ' '.join(deslContent.find_all(
                'div', class_='price no-stock')[0].get_text().split())

        return response
    except Exception as e:
        return "Book not found on deslegte.com"


'''' ABEBOOKS '''
@app.route("/abebooks/<ISBN>")
def getBookFromISBN_ABE(ISBN):
    abeURL = "https://www.abebooks.com/servlet/SearchResults?pt=book&sortby=2&kn="
    page = requests.get(abeURL + str(ISBN))
    soup = BeautifulSoup(page.text, 'lxml')
    try:
        response = {
            "title": "",
            "price": "",
            "link": abeURL + str(ISBN)
        }
        abeFirstResult = soup.find('ul', class_='result-block').li
        response["title"] = abeFirstResult.find(
            'meta', attrs={"itemprop": "name"})["content"]
        abePrice = abeFirstResult.find(
            'meta', attrs={"itemprop": "price"})["content"]
        # c = CurrencyConverter()
        # response["price"] = str(round(c.convert(float(abePrice), 'USD', 'EUR'), 2))
        response["price"] = abePrice*1.01

        return response
    except Exception as e:
        return "Book not found on abebooks.com"

PORT = int(os.environ.get('PORT', 5000))

print(PORT)

app.run(port=PORT)
