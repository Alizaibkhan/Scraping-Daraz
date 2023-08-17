from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup as bs
import time
import os
import csv


class WebScraping:

    def __init__(self, product_name):
        self.product_name = product_name
        self.error = False
        self.running = True
        self.html = None
        self.page = ''
        self.page_no = 1
        self.written = False
        self.get_html(self.product_name)

    def get_html(self, product_name, sleep=5, retries=3):
        for i in range(1, retries + 1):
            # we can't scrap without taking break
            time.sleep(sleep * i)  # first pause 5 sec secomd, 2nd puase 10 sec, 3rd try after 15 second
            try:
                with sync_playwright() as p:
                    # browser run headless = true by default, to see browser do false
                    browser = p.chromium.launch(headless=True)
                    self.page = browser.new_page()
                    self.page.goto('https://www.daraz.pk/', timeout = 0)  # opening link and disabling waiting time
                    print(self.page.title())
                    # input represent tag where #input-user-name represent id
                    self.page.fill('input#q', self.product_name)  # (css selector, value to fill)
                    self.page.click('button.search-box__button--1oH7')
                    while self.running:
                        self.page.wait_for_selector('div.ant-col-20.ant-col-push-4.side-right--Tyehf')
                        self.html = self.page.inner_html('div.ant-col-20.ant-col-push-4.side-right--Tyehf')
                        self.product_box(self.html)
                        if self.running:
                            self.pagination(self.html)

            except PlaywrightTimeout:
                print(f"Timeout error on {url}")
                self.html = None
                continue  # go back on top of the loop
            else:
                break      # if successful break-out no more retries needed

    def product_box(self, html):
        # checking if product exist for search query
        soup = bs(html, features='html.parser')
        products = soup.find('div', attrs={'class': 'title--sUZjQ'})
        if products:
            print(f'product {self.product_name} Does not exist on daraz.pk')
            self.running = False
        else:
            # extracting product box html which contain information like title, name, image, link of the product
            print(f'Extracting data from page{self.page_no}')
            titles = soup.find_all('div', attrs={"class": "gridItem--Yd0sa"}) # saving all product boxes in a list
            # each title contain each product from the current page
            for title in titles:
                if not self.error:
                    self.saving_csv(title)

    def pagination(self, html):
        souping = bs(html, 'html.parser')
        continued = souping.find('li', attrs={'class': 'ant-pagination-next'})['aria-disabled']
        if continued == 'true':
            self.running = False
        else:
            self.page_no += 1
            self.page.click('li.ant-pagination-next')
            time.sleep(2)

    # only extracting product link, title, price, image link from product box
    def saving_csv(self, html):
        product_title_elem = html.find('a', title=True)
        if product_title_elem:
            product_title = product_title_elem['title']
        else:
            product_title = 'N/A'

        product_link_elem = html.find('a', title=True)
        if product_link_elem:
            product_link = product_link_elem['href']
        else:
            product_link = 'N/A'

        product_price_elem = html.find('span', class_='currency--GVKjl')
        if product_price_elem:
            product_price = product_price_elem.text
        else:
            product_price = 'N/A'

        product_image_elem = html.find('img')
        if product_image_elem:
            product_image = product_image_elem['src']
        else:
            product_image = 'N/A'

        if not self.written:
            with open(f'{self.product_name}.csv', mode='w+', newline='') as fp:
                writer = csv.writer(fp)
                writer.writerow(['Product Title', 'Product Price', 'Product Image', 'Product Link', 'Page No:'])
            self.written = True

        try:
            with open(f'{self.product_name}.csv', mode='a', newline='',  encoding="utf-8") as fp:
                writer = csv.writer(fp)
                writer.writerow([product_title, product_price, product_image, product_link, self.page_no])
        except PermissionError:
            self.error = True
            print('Please close already open csv file and try again')


if __name__ == '__main__':
    user_product = input('Enter a product name: ')
    WebScraping(user_product)





