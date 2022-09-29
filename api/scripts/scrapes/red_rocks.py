
import requests
import pandas as pd
import re
from bs4 import BeautifulSoup


def redRocksScrape():    
    resp = requests.get('https://www.redrocksonline.com/events/')

    resp_soup = BeautifulSoup(resp.text, 'html.parser')
    section = resp_soup.find('section',{"id":"event-listing"})
    date = [x.find('div', {"class":"date"}).text.strip() for x in section.findAll('div',{"class":"card card-event event-month-active event-filter-active"})]
    images = [x.find('img')['data-image'] for x in section.findAll('div',{"class":"card card-event event-month-active event-filter-active"})]
    artist = [x.find('h3', {"class":"card-title"}).text.strip() for x in section.findAll('div',{"class":"card card-event event-month-active event-filter-active"})]

    def try_aria(x):
        try:
            return x['aria-label']
        except:
            return

    sub_artists = [try_aria(x.find('p')) for x in section.findAll('div',{"class":"card card-event event-month-active event-filter-active"})]
    ticket_links = [x.find('a')['href'] for x in section.findAll('div',{"class":"card card-event event-month-active event-filter-active"})]

    df = pd.DataFrame(list(zip(date, images, artist, sub_artists, ticket_links)))

    df.columns = ['Date','img_url','Artist','SubArtist','Link']

    df['Artist'] = df['Artist'] + ' featuring ' + df['SubArtist']

    df['Artist'] = df['Artist'].map(str)

    def splitArtists(row):
        return [x.strip() for x in re.split(';|:|,|,with|/|special guest|with|-| \d+|presents|featuring', row) if x != '']

    df['FiltArtist'] = df['Artist'].map(splitArtists)
    df['Venue'] = 'Red Rocks'
    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]
    
    return df
