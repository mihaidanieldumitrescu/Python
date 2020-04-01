from bs4 import BeautifulSoup
from codecs import open
from include.globals import *

import pprint
import requests
import json
import os
import re
import locale

locale.setlocale(locale.LC_ALL, '')

link_index = 1
bootstrap_head_header = """\
<head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">

    <title>Olx-Cars Report</title>
  </head>
"""

bootstap_footer = '''\
<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
'''


class OlxProduct:

    def __init__(self, link="https://www.olx.ro/oferta/masina-renault-megane-IDbEIBo.html"):
        self.isDeactivated = False
        self.title = ""
        self.link = link.split("#")[0] if len(link.split("#")) else link
        self.price = 0
        self.details = {}
        self.location = ""
        self.description = []
        self.images = []
        self.pageCounter = 0

        print(f"(OlxProduct contructor) Link is {self.link}")

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

            try:
                self.description = soup.find("div", {"id": "textContent"}).text.strip()
            except AttributeError as e:
                self.isDeactivated = True
                self.description = "No description available for this page! Page is deactivated"
                print(f"{e} -> Page is deactivated!")

            # self.title
            if soup.find("div", {"class": "offer-titlebox"}):
                self.title = soup.find("div", {"class": "offer-titlebox"}).h1.text.strip()
            else:
                self.title = None
            # self.price
            if soup.find("div", {"class": "price-label"}):
                self.price = soup.find("div", {"class": "price-label"}).strong.text
            elif soup.find("div", {"class": "pricelabel"}):
                self.price = soup.find("div", {"class": "pricelabel"}).strong.text
            else:
                self.price = None

            if soup.find('div', {'class': "offer-titlebox__details"}):
                self.location = soup.find('div', {'class': "offer-titlebox__details"}).a.strong.text
            else:
                self.location = None

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
                self.pageCounter = None
        else:
            print("(OlxProduct) Error: Not an olx link!\n")

    def to_htmldiv(self):
        global link_index

        if self.isDeactivated:
            return ""
        elif re.search(r'https?://www.olx.ro/oferta', self.link):
            div = [u"<div class='row'>\n"
                   u"<div class='col col-lg'>"]
            title = u"<h3>" \
                    u"<a href='" + self.link + u"' >" + self.price + u" - " + self.title + u"</a>" \
                                                                                           u"</h3>\n\n"
            try:
                substituted_price_string = re.sub(r"€|lei|\s+", "", self.price)
                price_to_int = int(substituted_price_string)
            except ValueError as e:
                print(f"{e}: \n")
                print(f"\t-> Link: {self.link}")
                print("\n\n")
                price_to_int = -999

            # paragraph e singurul care foloseste metoda text in loc de string "Adus\xc4\x83 din Germania" -> "Adus\u0103 din Germania"

            details_button = '''\
<p><button class="btn btn-primary" type="button" data-toggle="collapse" data-target="#details''' + f"_{link_index}" +\
                             '''" aria-expanded="false" aria-controls="details''' + f"_{link_index}" + '''"> Description details
</button></p>
'''

            description = '''\
<p><div class="collapse" id="details''' + f"_{link_index}" + '''">
  <div class="card card-body">
<pre style='white-space: pre-wrap; word-wrap: break-word;'>"''' + self.description + '''</pre>
  </div>
</div></p>
'''

            to_lei = price_to_int * 4.75
            in_local_currency = f"<p>Conversie: {locale.currency(to_lei, grouping = True)} - Locatie: {self.location}</p>"
            details = u"<p>An de fabricatie: {} - Rulaj: {} - Capacitate: {}</p>".format(self.details.get('An de fabricatie', "n/a"),
                                                                                                       self.details.get('Rulaj', "n/a"),
                                                                                                       self.details.get('Capacitate motor', "n/a"))
            images = (u"<div class='row'>"
                      u"\n" +
                      u"\n".join([u"<div class='col-md-4'>"
                                  u"  <p><div class='card md-4 box-shadow' style='width: 22rem;'>"
                                  u"    <img class='card-img-top' src='" + img_link + u"'>"
                                  u"    </img>"
                                  u"  </div></p>"
                                  u"</div>" for img_link in self.images]) +
                      u"</div>")

            div.append(title)
            div.append(in_local_currency)

            div.append(details)
            div.append(details_button)
            div.append(description)

            div.append(images)
            div.append(u"</div></div><hr>")

            link_index += 1

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
        global url_olx_cars
        # sortByDesc = "?search%5Border%5D=filter_float_price%3Adesc"
        # url = sortByDesc
        fail = 0
        pages = 0
        url = "https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme/bucuresti-ilfov-judet/?search%5Bfilter_float_price%3Afrom%5D=1800&search%5Bfilter_float_price%3Ato%5D=5000&search%5Bfilter_float_year%3Afrom%5D=2006&search%5Bfilter_float_rulaj_pana%3Ato%5D=130000"
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

                try:
                    raw_price = priceArr[0].strong.string
                    product_price = int(float(raw_price.replace(",", ".").replace(" ", "")[:-1]))
                except ValueError as e:
                    product_price = -1
                    print(f"\tError: {e}:\n\t-> Link '{link}' Price: '{priceArr[0]}'\n\n")

                self.products.append([product_title, product_price, product_link])
                self.products = sorted(self.products, key=lambda x: x[1])

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
            with open("fail.html", "w") as f:
                f.write(soup.text)

    def get_next_page(self, lastPage):
        pass

    def printResults(self):

        for product in self.products:
            print(f"{product['price'].ljust(10)}, {product['desc']}")

        # print str ( linkNextPage )


class OlxCars(Olx):

    def __init__(self):

        # this is only a debug link
        searchlink = "https://www.olx.ro/auto-masini-moto-ambarcatiuni/autoturisme/?search%5Bfilter_float_price%3Afrom%5D=600&search%5Bfilter_float_price%3Ato%5D=1400"
        Olx.__init__(self, searchlink, 30)
        self.statistics = {"otherCars": {"prices": [], "occurences": 0}}
        self.productDetailsArr = []
        self.load_products()
        self.filterWordsCarsModels = json.load(open(os.path.join(os.environ['OneDrive'], "PythonData", "config", "olx_cars.json")))
        self.allModels = []
        self.sort_by_model()
        self.read_product_details()
        self.write_results()

    def sort_by_model(self):
        # filterWords = {"opel": ['vectra', 'astra'], 'peugeot': '206' }
        sorted_list = []
        other_cars = []
        for carBuilder in self.filterWordsCarsModels[0]:
            for carModel in self.filterWordsCarsModels[0][carBuilder]:
                self.allModels.append(carModel)
                for productDesc in self.products:
                    if carModel.lower() in productDesc[0].lower():
                        sorted_list.append([self.filter_desc(productDesc[0]), productDesc[1]])
                        if carModel not in self.statistics:
                            self.statistics[carModel] = {"occurences": 0, "prices": [], "description": []}
                        self.statistics[carModel]['prices'].append(productDesc[1])
                        self.statistics[carModel]['description'].append(productDesc[0])

                        self.statistics[carModel]['occurences'] += 1
                    else:
                        other_cars.append([self.filter_desc(productDesc[0]), productDesc[1]])
                        if 'other_cars' not in self.statistics:
                            self.statistics['other_cars'] = {}
                            self.statistics['other_cars']['occurences'] = 0
                        else:
                            self.statistics['other_cars'].update({self.filter_desc(productDesc[0]): productDesc[1]})
                            self.statistics['other_cars']['occurences'] += 1


                if carModel in self.statistics:
                    self.statistics[carModel]['average'] = sum(self.statistics[carModel]['prices']) / len(self.statistics[carModel]['prices'])


        # THIS IS NOT GLOBAL
        sorted_list.append(other_cars)

    def read_product_details(self):

        print(f"selected models: {pprint.pformat(self.allModels)}\n")

        for productArr in self.products:

            title_tokens = productArr[0].lower().split()
            matches_dict = {token: token in self.allModels for token in title_tokens}

            matches_defined_models = any(matches_dict.values())

            if productArr[2] and matches_defined_models:
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
            f.write(bootstrap_head_header + "\n<body>\n\n")
            f.write("<div class='container'>")
            f.write("\n\n".join([x.to_htmldiv() for x in self.productDetailsArr]))
            f.write("</div>" + bootstap_footer + "</body></html>")

        print("OBS: Where are the Other car category?\n\n")

    @staticmethod
    def filter_desc(description):
        filter_words = ['vind', 'vand', 'cumpar', 'schimb', 'masina', 'cu', 'oferta', 'pret', 'sau']
        final_string = ""
        for word in description.lower().split(' '):
            if not word.lower() in filter_words:
                final_string += word + " "
        return final_string
