from flask import Flask
from flask_cors import CORS

# from types import NoneType
# from currency_converter import CurrencyConverter
from bs4 import BeautifulSoup
import requests
# from waitress import serve

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)
CORS(app)

'''' BOL '''
@app.route("/bol/<ISBN>")
def getBookFromISBN_BOL(ISBN):
    bolURL = "https://www.bol.com/nl/nl/s/?searchtext=" + str(ISBN)
    page = requests.get(bolURL)
    soup = BeautifulSoup(page.text, "lxml")
    try:
        response = {
            "title":"",
            "price":"",
            "imgURL":"",
            "link": bolURL
        }
        content = soup.find('div', class_='product-item__content');
        bolTitle = content.find('a', class_='product-title').get_text()
        bolPriceSections = content.find_all('div', class_='product-prices');
        if(len(bolPriceSections) > 1):
            bolUsedBook = content.find_all('div', class_='product-prices')[1]
            bolURL = "https://www.bol.com" + bolUsedBook.find_all('a')[1]["href"]
            bolPriceSplit = bolUsedBook.get_text().split()
            bolPrice = bolPriceSplit[-1].replace(',', '.')
            response["link"] = bolURL
        else:
            bolPriceSection = bolPriceSections[0].find('meta', attrs={"itemprop": "price"});
            if(bolPriceSection):
                bolPrice = bolPriceSection["content"];
            else:
                bolPrice = " ".join(bolPriceSections[0].get_text().split());
            
        bolImage = soup.find('div', class_='product-item__image').find('img')["src"]
        
        response["title"] = bolTitle
        response["price"] = bolPrice
        response["imgURL"] = bolImage
        
        return response
    except Exception as e:
        return "Book not found on bol.com"


'''' BOEKWINKELTJES '''
@app.route("/boekwinkeltjes/<ISBN>")
def getBookFromISBN_BOEK(ISBN):
    boekwinkeltjesURL = 'https://www.boekwinkeltjes.nl/s/?q=' + str(ISBN)
    page = requests.get(boekwinkeltjesURL)
    soup = BeautifulSoup(page.text, 'lxml')
    try:
        response = {
            "title": "",
            "price": "",
            "imgURL":"",
            "link": boekwinkeltjesURL
        }
        winkelTitleBlock = soup.find_all('td', class_='table-text')
        response["title"] = ' '.join(winkelTitleBlock[1].find(
            text=True, recursive=False).split())
        response["price"] = soup.find_all('td', class_='price')[
            0].strong.get_text()[2:]
        response["imgURL"] = soup.find('td', class_="table-image").find('a').find('img')["src"]

        return response
    except Exception as e:
        return "Book not found on bol.com"


'''' DESLEGTE '''
@app.route("/deslegte/<ISBN>")
def getBookFromISBN_DES(ISBN):
    deslegateURL = "https://www.deslegte.com/boeken/?q=" + str(ISBN)
    page = requests.get(deslegateURL)
    soup = BeautifulSoup(page.text, 'lxml')
    try:
        response = {
            "title": "",
            "price": "",
            "imgURL":"",
            "link": deslegateURL
        }
        deslContent = soup.find_all('div', class_='book')[0]
        response["title"] = deslContent.h3.get_text()
        try:
            response["price"] = deslContent.find_all(
                'meta', attrs={"itemprop": "lowPrice"})[0]["content"]
        except:
            response["price"] = ' '.join(deslContent.find_all(
                'div', class_='price no-stock')[0].get_text().split())
        response["imgURL"] = "https://www.deslegte.com" + deslContent.find('img')["src"]

        return response
    except Exception as e:
        return "Book not found on deslegte.com"


'''' ABEBOOKS '''
@app.route("/abebooks/<ISBN>")
def getBookFromISBN_ABE(ISBN):
    abeURL = "https://www.abebooks.com/servlet/SearchResults?pt=book&sortby=2&kn=" + str(ISBN)
    page = requests.get(abeURL)
    soup = BeautifulSoup(page.text, 'lxml')
    try:
        response = {
            "title": "",
            "price": "",
            "imgURL":"",
            "link": abeURL
        }
        abeFirstResult = soup.find('ul', class_='result-block').li
        response["title"] = abeFirstResult.find(
            'meta', attrs={"itemprop": "name"})["content"]
        abePrice = abeFirstResult.find(
            'meta', attrs={"itemprop": "price"})["content"]
        c = CurrencyConverter()
        response["price"] = str(round(c.convert(float(abePrice), 'USD', 'EUR'), 2))
        response["imgURL"] = abeFirstResult.find("img")["src"]

        return response
    except Exception as e:
        return "Book not found on abebooks.com"
    

@app.route("/")
def index():
    return "<h1>Hello!</h1>"


if __name__ == "__main__":
    app.run()

