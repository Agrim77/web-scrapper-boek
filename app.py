from flask import Flask
from flask_cors import CORS

from currency_converter import CurrencyConverter
from bs4 import BeautifulSoup
import requests
import xmltodict
# from waitress import serve

app = Flask(__name__)
CORS(app)

'''' BOL '''
@app.route("/bol/<ISBN>")
def getBookFromISBN_BOL(ISBN):
    
    ISBNs = ISBN.split(',')

    responses = {}

    for isbn in ISBNs:

        bolURL = "https://www.bol.com/nl/nl/s/?sort=price0&searchtext=" + str(isbn)
        page = requests.get(bolURL)
        soup = BeautifulSoup(page.text, "lxml")
        try:
            response = {
                "title":"",
                "price":"",
                "imgURL":"",
                "link": bolURL,
                "binding": ""
            }
            content = soup.find('div', class_='product-item__content')
            bolTitleSection = content.find('a', class_='product-title')
            bolTitle = bolTitleSection.get_text()
            
            bolBookPage = bolTitleSection["href"]
            bolBook = requests.get('https://www.bol.com' + bolBookPage)
            bolPage = BeautifulSoup(bolBook.text, 'lxml')
            bolImageContainer = bolPage.find('wsp-image-zoom').div.img
            try:
                bolImage = bolImageContainer['data-zoom-image-url']
            except:
                bolImage = bolImageContainer['src']
            
            bolPriceSections = content.find_all('div', class_='product-prices')
            if(len(bolPriceSections) > 1):
                bolUsedBook = content.find_all('div', class_='product-prices')[1]
                bolURL = "https://www.bol.com" + bolUsedBook.find_all('a')[1]["href"]
                bolPriceSplit = bolUsedBook.get_text().split()
                bolPrice = bolPriceSplit[-1].replace(',', '.')
                response["link"] = bolURL
            else:
                bolPriceSection = bolPriceSections[0].find('meta', attrs={"itemprop": "price"})
                if(bolPriceSection):
                    bolPrice = bolPriceSection["content"]
                else:
                    bolPrice = " ".join(bolPriceSections[0].get_text().split())
            
            bolBinding = soup.find('ul', class_='product-small-specs').findAll('li')[1].span.text
            response["title"] = bolTitle
            response["price"] = bolPrice
            response["imgURL"] = bolImage
            response["binding"] = bolBinding
            responses[isbn] = response
        except Exception as e:
            responses[isbn] = {"error": "Book not found on bol.com"}

    if len(ISBNs) == 1:
        return responses[ISBN]
        
    return responses


'''' BOEKWINKELTJES '''
@app.route("/boekwinkeltjes/<ISBN>")
def getBookFromISBN_BOEK(ISBN):
    boekwinkeltjesURL = 'https://www.boekwinkeltjes.nl/s/?sort=prijs&q=' + str(ISBN)
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
    deslegateURL = "https://www.deslegte.com/boeken/?sc=price&so=asc&q=" + str(ISBN)
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

    url = "https://search2.abebooks.com/search?clientkey=e5d85298-dcc3-42b2-a9ab-9c3e63bce99d&isbn="+str(ISBN)
    r = requests.get(url)
    data =  xmltodict.parse(r.text)
    return data

    # abeURL = "https://www.abebooks.com/servlet/SearchResults?pt=book&sortby=2&kn=" + str(ISBN)
    # page = requests.get(abeURL)
    # soup = BeautifulSoup(page.text, 'lxml')
    # try:
    #     response = {
    #         "title": "",
    #         "price": "",
    #         "imgURL":"",
    #         "link": abeURL
    #     }
    #     abeFirstResult = soup.find('ul', class_='result-block').li
    #     response["title"] = abeFirstResult.find(
    #         'meta', attrs={"itemprop": "name"})["content"]
    #     abePrice = abeFirstResult.find(
    #         'meta', attrs={"itemprop": "price"})["content"]
    #     c = CurrencyConverter()
    #     response["price"] = str(round(c.convert(float(abePrice), 'USD', 'EUR'), 2))
    #     response["imgURL"] = abeFirstResult.find("img")["src"]

    #     return response
    # except Exception as e:
    #     return "Book not found on abebooks.com"


'''' AMAZON '''
@app.route("/amazon/<ISBN>")
def getBookFromISBN_AMAZON(ISBN):
    
    if ISBN == "9789025759919":
        return {
            "title": "Boer Boris gaat naar de markt",
            "price": "14.99",
            "imgURL": "https://m.media-amazon.com/images/I/61Nci0PPeYL._SX497_BO1,204,203,200_.jpg",
            "link": "https://amzn.to/3gdNhLu"
        }
    elif ISBN == "9789047820017":
        return {
            "title": "Boer Boris doeboek",
            "price": "5.99",
            "imgURL": "https://m.media-amazon.com/images/I/61guKqHcH2L._SX597_BO1,204,203,200_.jpg",
            "link": "https://amzn.to/3EnGvKS"
        }
    elif ISBN == "9789025774639":
        return {
            "title": "Boer Boris start de motor!: een uitklapboek",
            "price": "12.99",
            "imgURL": "https://m.media-amazon.com/images/I/51qCkoJsS6L._SY487_BO1,204,203,200_.jpg",
            "link": "https://amzn.to/3GrLywv"
        }
    return "Book not found on amazon.com"

@app.route("/")
def index():
    return "<h1>Hello!</h1>"


if __name__ == '__main__':
    app.run()
