from datetime import datetime
import requests
import re
from bs4 import BeautifulSoup

def get_adds_on_page_no(page_no):
    urls = []
    request_url = 'http://www.blocket.se/annonser/hela_sverige?page=' + str(page_no)
    resp = requests.get(request_url)
    soup = BeautifulSoup(resp.content, features='html.parser')

    #find all links and reformat them so they are searchable, store in list
    elements = soup.find_all('a', class_=lambda val: val.startswith('Link-sc-139ww1j-0 styled__StyledTitleLink-sc-1kpvi4z-8'))
    for url in elements:
        url = 'http://www.blocket.se' + str(url['href'])
        urls.append(url)
    return urls

def get_item_info(blocket_link):
    item_info = {}
    #store whole link
    item_info['link'] = blocket_link

    #get all things between slashes to extract info from links
    splitted_link = blocket_link.split('/')
    region = splitted_link[4]
    title = splitted_link[5]

    #store in info
    item_info['title'] = title
    item_info['region'] = region

    #get info from webpage
    item_page = requests.get(blocket_link)
    soup = BeautifulSoup(item_page.content, features='html.parser')

    #price, item and time description
    try:
        item_info['price'] = soup.find('div', class_=re.compile('TextHeadline1__TextHeadline1Wrapper-sc-18mtyla-0(.*)Price__StyledPrice-crp2x0-0(.*)')).text
        unformated_description = soup.find('div', class_=re.compile('TextBody__TextBodyWrapper-sc-17pzx5f-0(.*)BodyCard__DescriptionPart-sc-15r463q-2(.*)')).text
        item_info['description'] = unformated_description.replace('\n', ' ').strip().lower()
        unformated_time = soup.find('div', class_=re.compile('PublishedTime__Wrapper-pjprkp-2(.*)')).text
        item_info['time'] = datetime.today().strftime('%Y-%m-%d') + " " + unformated_time[-5:]

        #Ad category breakdown
        item_info['categories'] = []
        categories = soup.find('ol', class_=lambda val: val.startswith('Breadcrumbs__BreadcrumbList-lcntoj-0'))
        all_categories = categories.find_all('div', itemprop='title')

        #Create array with parent category
        for category in all_categories:
            item_info['categories'].append(category.text)

        return item_info

    except Exception as e:
        print("No price or description information.")
        print(e)
        return
