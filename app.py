from flask import Flask
from flask_cors import CORS

from currency_converter import CurrencyConverter
from bs4 import BeautifulSoup
import requests
import xmltodict
import base64

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# from waitress import serve

app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address, default_limits=["1 per 3 seconds"])
CORS(app)

'''' BOL '''
@app.route("/bol/<ISBN>")
@limiter.limit("1 per 3 seconds")
def getBookFromISBN_BOL(ISBN):
    ISBNs = ISBN.split(',')
    responses = {}

    # Authentication Process
    client_id = "c866b744-6084-4afc-b575-137d176c9be6"
    client_secret = "a5MZZ10Yg!XFjCQDmecxU1hmtfwIQKJKZebB3WXoO?4CAsPyRVfs(zQ(pUON)q(8"
    message = f"{client_id}:{client_secret}"
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    encoded_message = base64_bytes.decode('ascii')
    authorization_header = f"Basic {encoded_message}"

    # Affiliate program details
    siteId = "1202520" # Replace with your actual SiteId
    subId = "affiliate" # Replace with your SubID - Used for personal tracking
    name = "boekengezocht_second_hand_pdp" # Replace with your Name - Used for personal tracking

    for isbn in ISBNs:
        singleBookResponse = {
            "title": "",
            "price": "",
            "imgURL": "",
            "link": "",
            "binding": "",
            "language": ""
        }

        bolURL = "https://api.bol.com/catalog/v4/search"
        bolAuthenticateURL = "https://login.bol.com/token?grant_type=client_credentials"
        headers = {"Authorization": authorization_header}

        try:
            response = requests.post(bolAuthenticateURL, headers=headers)
            if response.status_code == 200:
                access_token = response.json()["access_token"]
                bearer_token = f"Bearer {access_token}"
                headers = {"Authorization": bearer_token}

                try:
                    response = requests.get(bolURL, headers=headers, params={
                        "includeattributes": "true",
                        "q": isbn,
                        "limit": 1
                    })

                    if response.status_code == 200:
                        data = response.json()
                        productId = data["products"][0]["id"]
                        productURL = f"https://api.bol.com/catalog/v4/products/{productId}?offers=all"
                        productResponse = requests.get(productURL, headers=headers, params={
                            "includeattributes": "true",
                            "q": productId,
                            "limit": 1
                        })

                        print("Product Response Status -> ", productResponse.status_code)

                        if productResponse.status_code == 200:
                            productData = productResponse.json()
                            print("Product Response Data -> ", productData)
                            offers = productData["products"][0]['offerData']['offers']
                            if offers:
                                # Find the lowest price offer
                                lowest_price_offer = min(offers, key=lambda offer: offer['price'])
                                singleBookResponse["price"] = lowest_price_offer['price']


                            singleData = productData["products"][0]
                            print("Single Data -> ", singleData)

                            tempUrl = tempImage = tempBinding = tempLanguage = None
                            for url in singleData['urls']:
                                if url["key"] == "DESKTOP":
                                    tempUrl = url["value"]
                                    tempUrl = tempUrl.replace("/p/", "/prijsoverzicht/")
                                    tempUrl = tempUrl + "?filter=all&sort=price&sortOrder=asc"

                            for images in singleData['images']:
                                if images["key"] == "XL":
                                    tempImage = images["url"]

                            for contents in singleData['attributeGroups']:
                                if contents["title"] == "Inhoud":
                                    for content in contents["attributes"]:
                                        if content["key"] == "Binding":
                                            tempBinding = content["value"]
                                        if content["key"] == "Language":
                                            tempLanguage = content["value"]

                            # Generate the affiliate URL using the obtained product data
                            affiliateUrl = f"http://partner.bol.com/click/click?p=1&t=url&s={siteId}&url={tempUrl}&f=TXL&subid={subId}&name={name}"
                            print("Affiliate URL is -> ", affiliateUrl)

                            singleBookResponse["title"] = singleData["title"] if singleData["title"] else None
                            singleBookResponse["imgURL"] = tempImage if tempImage else None
                            singleBookResponse["binding"] = tempBinding if tempBinding else None
                            singleBookResponse["language"] = tempLanguage if tempLanguage else None
                            singleBookResponse["link"] = affiliateUrl if affiliateUrl else None

                            # Continue with your code...

                            responses[isbn] = singleBookResponse

                except Exception as e:
                    responses[isbn] = {"error": "Product API call error"}
        except Exception as e:
            responses[isbn] = {"error": "Authentication error"}

    if len(ISBNs) == 1:
        return responses[ISBN]

    return responses

# def getBookFromISBN_BOL(ISBN):
#     ISBNs = ISBN.split(',')
#     responses = {}
    
#     # Authentication Process
#     client_id = "c866b744-6084-4afc-b575-137d176c9be6"
#     client_secret = "a5MZZ10Yg!XFjCQDmecxU1hmtfwIQKJKZebB3WXoO?4CAsPyRVfs(zQ(pUON)q(8"
#     message = f"{client_id}:{client_secret}"
#     message_bytes = message.encode('ascii')
#     base64_bytes = base64.b64encode(message_bytes)
#     encoded_message = base64_bytes.decode('ascii')
#     authorization_header = f"Basic {encoded_message}"
    
#     for isbn in ISBNs:
#         singleBookResponse = {
#             "title":"",
#             "price":"",
#             "imgURL":"",
#             "link": "",
#             "binding": "",
#             "language": ""
#         }
        
#         bolURL = "https://api.bol.com/catalog/v4/search"
#         bolAuthenticateURL = "https://login.bol.com/token?grant_type=client_credentials"
#         headers = {"Authorization": authorization_header}
        
#         try:
#             response = requests.post(bolAuthenticateURL, headers=headers)
#             print(response)
            
#             if response.status_code == 200:
#                 access_token = response.json()["access_token"]
#                 bearer_token = f"Bearer {access_token}"
#                 headers = {"Authorization": bearer_token}
                
#                 try:
#                     response = requests.get(bolURL, headers=headers, params={
#                                     "includeattributes": "true", 
#                                     "q": isbn, 
#                                     "limit": 1})
                    
#                     if response.status_code == 200:
#                         data = response.json()
#                         singleData = data["products"][0]

#                         tempUrl = tempImage = tempBinding = tempLanguage = None
#                         for url in singleData['urls']:
#                             if url["key"] == "DESKTOP":
#                                 tempUrl = url["value"]
                                
#                         for images in singleData['images']:
#                             if images["key"] == "XL":
#                                 tempImage = images["url"]
                                
#                         for contents in singleData['attributeGroups']:
#                             if contents["title"] == "Inhoud":
#                                 for content in contents["attributes"]:
#                                     if content["key"] == "Binding":
#                                         tempBinding = content["value"]
#                                     if content["key"] == "Language":
#                                         tempLanguage = content["value"]
                                
#                         singleBookResponse["title"] = singleData["title"] if singleData["title"] else None
#                         singleBookResponse["price"] = singleData['offerData']['offers'][0]['price'] if singleData['offerData']['offers'][0]['price'] else None
#                         singleBookResponse["imgURL"] = tempImage if tempImage else None
#                         singleBookResponse["binding"] = tempBinding if tempBinding else None
#                         singleBookResponse["language"] = tempLanguage if tempLanguage else None
#                         singleBookResponse["link"] = tempUrl if tempUrl else None
#                         responses[isbn] = singleBookResponse
                        
#                 except Exception as e:
#                     responses[isbn] = {"error": "Book not found on bol.com - 1"}
#         except Exception as e:
#                     responses[isbn] = {"error": "Book not found on bol.com - 2"}
    
#     if len(ISBNs) == 1:
#         return responses[ISBN]
    
#     return responses


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
        return "Book not found on boekwinkeltjes.nl"


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

    try:
        url = "https://search2.abebooks.com/search?clientkey=e5d85298-dcc3-42b2-a9ab-9c3e63bce99d&isbn="+str(ISBN)
        r = requests.get(url)
        data =  xmltodict.parse(r.text)

        if len(data['searchResults']['Book']) != 0:

            eur = False
            for book in data['searchResults']['Book']:
                if book['vendorCurrency'] == 'EUR':
                    response = {
                        "title": book['title'],
                        "price": book['listingPrice'],
                        "imgURL": book['catalogImage'],
                        "link": 'https://'+book['listingUrl']
                    }
                    eur = True
                    break
            if eur == False:
                book = data['searchResults']['Book'][0]
                response = {
                    "title": book['title'],
                    "price": book['listingPrice'],
                    "imgURL": book['catalogImage'],
                    "link": 'https://'+book['listingUrl']
                }
            return response

        else:
            return "Book not found on abebooks.com"

    except Exception as e:
        return "Book not found on abebooks.com"

'''' AMAZON - NEW CODE '''
# @app.route("/amazon/<ISBN>")
# def getBookFromISBN_AMAZON(ISBN):
#     amazonURL = f"https://www.amazon.nl/s?k={ISBN}&i=stripbooks&sprefix={ISBN}%2Cstripbooks%2C196"
#     page = requests.get(amazonURL)
#     soup = BeautifulSoup(page.text, 'html.parser')
#     try:
#         response = {
#             "title": "",
#             "price": "",
#             "imgURL":"",
#             "link": amazonURL
#         }
#         # Title
#         response["title"] = soup.find('span', class_='a-size-medium a-color-base a-text-normal').text.strip()

#         # Price
#         productPrice = soup.find('span', class_='a-price-whole').text.strip()
#         productPriceSymbol = soup.find('span', class_='a-price-symbol').text.strip()
#         if productPriceSymbol == "€":
#             response["price"] = productPrice
            
#         # Image URL
#         productImage = soup.find('img', class_='s-image')
#         response["imgURL"] = productImage["src"]

#         # Link
#         productURL = soup.find('a', class_='a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal')
#         response["link"] = "https://amazon.nl" + productURL["href"]

#         return response
#     except Exception as e:
#         return "Book not found on amazon.nl"
        
'''' AMAZON - OLD CODE '''
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


'''' BOL - OLD CODE '''
# @app.route("/bol/<ISBN>")
# def getBookFromISBN_BOL(ISBN):

#     ISBNs = ISBN.split(',')

#     responses = {}

#     for isbn in ISBNs:

#         bolURL = "https://www.bol.com/nl/nl/s/?sort=price0&searchtext=" + \
#             str(isbn)
#         page = requests.get(bolURL)
#         soup = BeautifulSoup(page.text, "lxml")
#         try:
#             response = {
#                 "title": "",
#                 "price": "",
#                 "imgURL": "",
#                 "link": bolURL,
#                 "binding": ""
#             }
#             content = soup.find('div', class_='product-item__content')
#             bolTitleSection = content.find('a', class_='product-title')
#             bolTitle = bolTitleSection.get_text()

#             bolBookPage = bolTitleSection["href"]
#             bolBook = requests.get('https://www.bol.com' + bolBookPage)
#             bolPage = BeautifulSoup(bolBook.text, 'lxml')
#             bolImageContainer = bolPage.find('wsp-image-zoom').div.img
#             try:
#                 bolImage = bolImageContainer['data-zoom-image-url']
#             except:
#                 bolImage = bolImageContainer['src']

#             bolPriceSections = content.find_all('div', class_='product-prices')
#             if (len(bolPriceSections) > 1):
#                 bolUsedBook = content.find_all(
#                     'div', class_='product-prices')[1]
#                 bolURL = "https://www.bol.com" + \
#                     bolUsedBook.find_all('a')[1]["href"]
#                 bolPriceSplit = bolUsedBook.get_text().split()
#                 bolPrice = bolPriceSplit[-1].replace(',', '.')
#                 response["link"] = bolURL
#             else:
#                 bolPriceSection = bolPriceSections[0].find(
#                     'meta', attrs={"itemprop": "price"})
#                 if (bolPriceSection):
#                     bolPrice = bolPriceSection["content"]
#                 else:
#                     bolPrice = " ".join(bolPriceSections[0].get_text().split())

#             bolBinding = soup.find(
#                 'ul', class_='product-small-specs').findAll('li')[1].span.text
#             response["title"] = bolTitle
#             response["price"] = bolPrice
#             response["imgURL"] = bolImage
#             response["binding"] = bolBinding
#             responses[isbn] = response
#         except Exception as e:
#             responses[isbn] = {"error": "Book not found on bol.com"}

#     if len(ISBNs) == 1:
#         return responses[ISBN]

#     return responses


@app.route("/")
def index():
    return "<h1>Hello!</h1>"


if __name__ == '__main__':
    app.run()
