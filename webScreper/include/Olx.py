from bs4 import BeautifulSoup
from codecs import open
import pprint
import requests
import json
import os
import re


class OlxProduct:
    def __init__(self, link="https://www.olx.ro/oferta/masina-renault-megane-IDbEIBo.html"):
        self.title = ""
        self.link = link.split("#")[0] if len(link.split("#")) else link
        self.price = 0
        self.details = {}
        self.description = []
        self.images = []
        self.pageCounter = 0

        print(f"(OlxProduct contructor) Link is {self.link}\n")

    def __repr__(self):
        details_pretty = {}
        for key in self.details:
            details_pretty[key.ljust(16)] = self.details[key]

        return (
            ("Title:".ljust(15) + " {}\n" +
             "Link:".ljust(15) + " {}\n" +
             "Description:".ljust(15) + " {}\n" +
             "Page count:".ljust(15) + " {}\n\n" +

             "Details:".ljust(15) + "\n{}\n\n" +
             "Images:".ljust(15) + "\n{}\n" +
             "\n").format(pprint.pformat(self.title, indent=4), pprint.pformat(self.link, indent=4), pprint.pformat(self.description, indent=4),
                          pprint.pformat(self.pageCounter, indent=4),
                          pprint.pformat(details_pretty, indent=4), pprint.pformat(self.images, indent=4)))

    def load_page(self):

        if re.search(r'https?://www.olx.ro/oferta', self.link):
            headers = {'User-Agent': 'Mozilla 5.10'}
            content = requests.get(self.link, data=headers).text
            soup = BeautifulSoup(content, "lxml")

            # self.title
            if soup.find("div", {"class": "offer-titlebox"}):
                self.title = soup.find("div", {"class": "offer-titlebox"}).h1.text.strip()
            else:
                self.title = "n/a"
            # self.price
            if soup.find("div", {"class": "price-label"}):
                self.price = soup.find("div", {"class": "price-label"}).strong.text
            elif soup.find("div", {"class": "pricelabel"}):
                self.price = soup.find("div", {"class": "pricelabel"}).strong.text
            else:
                self.price = "n/a"
            # self.description
            self.description = soup.find("div", {"id": "textContent"}).text.strip()

            # self.images
            for div in soup.findAll("div", {"class": "photo-glow"}):
                if div.img:
                    self.images.append(div.img['src'])

            # self.details
            for table in soup.findAll("table", {"class": "item"}):
                if table.find('a'):
                    self.details[table.th.string] = table.strong.a.text.strip()
                else:
                    if table.strong:
                        self.details[table.th.string] = table.strong.text.strip()

            # self.pageCounter
            if soup.find("div", {"id": "offerbottombar"}):
                self.pageCounter = soup.find("div", {"id": "offerbottombar"}).strong.text
            else:
                self.pageCounter = "n/a"

        else:
            print("(OlxProduct) Error: Not an olx link!\n")

    def to_htmldiv(self):
        if re.search(r'https?://www.olx.ro/oferta', self.link):
            div = [u"<div class='olx-product'>\n"]
            title = u"<h3><a href='" + self.link + u"' >" + self.price + u" - " + self.title + u"</a></h3>\n\n"

            # paragraph e singurul care foloseste metoda text in loc de string "Adus\xc4\x83 din Germania" -> "Adus\u0103 din Germania"
            description = u"<p>" + self.description + u"</p>\n"
            details = u"<p>An de fabricatie: {} - Rulaj: {} - Capacitate: {}".format(self.details.get('An de fabricatie', "n/a"),
                                                                                     self.details.get('Rulaj', "n/a"),
                                                                                     self.details.get('Capacitate motor', "n/a"))
            images = (u"<div class='image-gallery'>\n" +
                      u"\n".join([u"<img src ='" + x + "' height='300' ></img>" for x in self.images]) +
                      u"</div>")

            div.append(title)
            div.append(details)
            div.append(description)

            div.append(images)
            div.append(u"</div>")
            return u"\n".join(div)
        else:
            return u"<p>-Page empty-\n\n"


class Olx(object):
    def __init__(self, search_str, limit=1):
        self.products = []
        self.limitPages = limit
        self.pagesIndex = 1

    # [ {}, {}, {}]

    # self.loadDebug()

    def load_debug(self):
        with open("olxCarsResults.json", "r") as f:
            self.products = json.load(f)

        for product in self.products:
            print(f"{product[0].ljust(20)} {str(product[1]).rjust(5)}")

    def load_products(self):

        # sortByDesc = "?search%5Border%5D=filter_float_price%3Adesc"
        # url = sortByDesc
        fail = 0
        pages = 0
        url = "https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme/?search%5Bfilter_float_price%3Afrom%5D=2000&search%5Bfilter_float_price%3Ato%5D=7000"
        # url = "https://www.olx.ro/oferte/q-asus-transformer/"
        while url != "":

            print(f"Attempting to open the following url: '{url}' \n\n")

            # Add your headers
            headers = {'User-Agent': 'Mozilla 5.10'}
            content = requests.get(url, data=headers).text

            soup = BeautifulSoup(content, "lxml")
            url = ""

            frames = soup.find_all('tr', {"class": "wrap"})
            if len(frames) == 0:
                fail = 1
                with open("dump_{}.html".format(pages), "w", encoding='utf-8') as f:
                    f.write(str(soup))
                pages += 1

            for link in frames:
                product_link = link.a['href'].split("#")[0] if len(link.a['href'].split("#")) else link.a['href']
                product_title = link.strong.string
                priceArr = (link.find_all('p', {"class": "price"}))

                if re.search(r'www.autovit.ro', product_link):
                    print("Skipping autovit link {} \n".format(product_link))
                    continue

                if len(priceArr):
                    print(priceArr[0].strong.string.replace(" ", "")[:-1])
                    product_price = int(priceArr[0].strong.string.replace(" ", "")[:-1])

                else:
                    product_price = -1
                self.products.append([product_title, product_price, product_link])

            last_page = soup.find_all("div", {"class": "pager rel clr"})

            for link in last_page:

                if self.limitPages == 0:
                    break

                link_next_page = link.find("span", {"class": "fbold next abs large"})

                try:
                    if link_next_page.a:
                        url = link_next_page.a['href']
                        self.pagesIndex += 1
                    else:
                        url = ""
                except ValueError:
                    print("Error in link next page\n\n {link_next_page} \n")
                    print(ValueError)
                self.limitPages -= 1
            print("Done extracting ...\n\n Found a number of {} pages and a total of {} items ".format(self.pagesIndex, len(self.products)))
        if fail:
            print("Error: Either link is wrong or something changed in page structure!\n\n")

    def get_next_page(self, lastPage):
        pass

    def printResults(self):

        for product in self.products:
            print(f"{product['price'].ljust(10)}, {product['desc']}")

        # print str ( linkNextPage )


class OlxCars(Olx):

    def __init__(self):
        searchlink = "https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme/?search%5Bfilter_float_price%3Afrom%5D=600&search%5Bfilter_float_price%3Ato%5D=1400"
        Olx.__init__(self, searchlink, 1)
        self.pp = pprint.PrettyPrinter(indent=4)
        self.statistics = {"otherCars": {"prices": [], "occurences": 0}}
        self.productDetailsArr = []
        self.load_products()
        self.filterWordsCarsModels = json.load(open(os.path.join(os.environ['OneDrive'], "PythonData", "config", "olx_cars.json")))
        self.sort_by_model()
        self.read_product_details()
        self.write_results()

    def sort_by_model(self):
        # filterWords = {"opel": ['vectra', 'astra'], 'peugeot': '206' }
        sorted_list = []
        other_cars = []
        for carBuilder in self.filterWordsCarsModels[0]:
            for carModel in self.filterWordsCarsModels[0][carBuilder]:
                print(f"Looking for {carModel} ...")
                self.statistics[carModel] = {"occurences": 0, "prices": []}
                for productDesc in self.products:
                    if carModel in productDesc[0].lower():
                        sorted_list.append([self.filter_desc(productDesc[0]), productDesc[1]])
                        self.statistics[carModel]['prices'].append(productDesc[1])
                        self.statistics[carModel]['prices'] = sorted(self.statistics[carModel]['prices'])
                        self.statistics[carModel]['occurences'] += 1
                    else:
                        other_cars.append([self.filter_desc(productDesc[0]), productDesc[1]])
                        self.statistics['other_cars'].update({self.filter_desc(productDesc[0]): productDesc[1]})
                        self.statistics['other_cars']['occurences'] += 1
                tmp_sum = 0
                for price in self.statistics[carModel]['prices']:
                    tmp_sum += int(price)
                if len(self.statistics[carModel]['prices']):
                    self.statistics[carModel]['average'] = tmp_sum / len(self.statistics[carModel]['prices'])
        sorted_list.append(other_cars)

    def read_product_details(self):
        for productArr in self.products:
            if productArr[2]:
                obj = OlxProduct(productArr[2])
                obj.load_page()
                self.productDetailsArr.append(obj)

    def write_results(self):
        with open("olxCarsResults.json", "w") as f:
            f.write(json.dumps(self.products, sort_keys=True, indent=4))
        with open("olxCarStatistics.json", "w") as f:
            f.write(json.dumps(self.statistics, sort_keys=True, indent=4))
        with open("reportCars.html", "w", encoding='utf-8') as f:
            f.write("<html>")
            f.write("<head>\n\t<meta charset='UTF-8'> \n\t <title>Olx-Cars Report</title>\n</head>\n<body>\n\n")
            f.write("\n\n".join([x.to_htmldiv() for x in self.productDetailsArr]))
            f.write("</body></html>")

        print("OBS: Where are the Other car category?\n\n")

    def filter_desc(self, description):
        filter_words = ['vind', 'vand', 'cumpar', 'schimb', 'masina', 'cu', 'oferta', 'pret', 'sau']
        final_string = ""
        for word in description.lower().split(' '):
            if not word.lower() in filter_words:
                final_string += word + " "
        return final_string
