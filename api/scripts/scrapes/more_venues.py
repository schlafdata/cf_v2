import time
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import requests
import pandas as pd
import re



from bs4 import BeautifulSoup

def ball_scrape():
    
    ball = requests.get('https://www.ballarena.com/misc/all-events/')
    ball = BeautifulSoup(ball.text, 'html.parser')
    divs = ball.findAll('div', {"class":"item-box"})

    def try_href(x):
        try:
            link = x.find('a')['href']
            title = x.find('a').text.strip()
            img_url = x.find('a').find('img')['src']
            date = divs[0].find('p').text.strip()
            return (title, link, date, img_url)
        except:
            pass

    items = [try_href(x) for x in divs]
    df = pd.DataFrame(items)
    df = df.dropna()
    df.columns = ['Artist','Link','Date','img_url']
    df.Artist = df['Artist'].map(lambda x : x.lower())
    df = df[df.Artist.str.contains('tour')]

    def map_filters(row):
        return [x.strip() for x in re.split('-|:|hits back!|and|\+', row) if (x is not None) & (x != '')]

    df['FiltArtist'] = df.Artist.map(map_filters)
    df['Venue'] = 'Ball Arena'
    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]
    df.Date = df['Date'].map(lambda x : ','.join(x.split('•')[1].split()))
    return df

def dazzle():    
    dazzle = requests.get('https://dazzledenver.com/upcoming-events/')
    dazzle = BeautifulSoup(dazzle.text, 'html.parser')
    daz = dazzle.find('div', {"class":"row_grid"}).findAll('div')


    def get_attrs(row):
        try:
            month = row.find('span', {"class":"month"}).text.strip()
            day = row.find('span', {"class":"date"}).text.strip()
            img_url = re.split('\(|\)', row.find('div', {"class":"img_placeholder"})['style'])[1].strip("'")
            artist = row.find('div', {"class":"event_title"}).text
            link = row.find('a')['href']

            date = month + '-' + day + '-' + '2022'
            return (artist, date, link, img_url)
        except:
            pass

    df = pd.DataFrame([get_attrs(x) for x in daz]).dropna().drop_duplicates()
    df.columns = ['Artist','Date','Link','img_url']

    def map_filters(row):
        return [x.strip() for x in re.split('&|feat.|:|,', row) if (x is not None) & (x != '')]
    
    df['Venue'] = 'Dazzle'

    df['FiltArtist'] = df.Artist.map(map_filters)
    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]
    
    return df

def ophelias():
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Origin': 'https://opheliasdenver.com',
            'Referer': 'https://opheliasdenver.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }

        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("window-size=1280,800")

        ua = UserAgent()
        a = ua.random
        user_agent = ua.random
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        driver.get('https://opheliasdenver.com/listing/')
        time.sleep(3)

        for request in driver.requests:
            if 'apikey' in request.url:
                apikey = re.split('apikey=|&',request.url)[1]
                print(apikey)


        def venue_data(response):
            df = pd.DataFrame(response.json()['_embedded']['events'])
            df['img_url'] = df['images'].map(lambda x : x[0]['url'])
            df['Date'] = pd.json_normalize(df['dates'])['start.localDate']
            df = df[['name','url','img_url','Date']]
            df.columns = ['Artist','Link','img_url','Date']

            def map_filters(row):
                return [x.strip() for x in re.split(':|presents', row) if (x is not None) & (x != '')]

            df['Venue'] = 'Ophelias'
            df['FiltArtist'] = df.Artist.map(map_filters)
            df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]

            return df


        response = requests.get(f'https://app.ticketmaster.com/discovery-widgets/v2/events?apikey={apikey}&size=11&radius=24&venueId=KovZ917Aai0&city=Denver&countryCode=US&source=ticketmaster&postalCode=80202&startDateTime=2022-10-01T18:03:22Z&endDateTime=2023-10-01T18:03:22Z&latlong=&locale=*&sort=date,asc', headers=headers)

        df = venue_data(response)
        dfs = []
        dfs.append(df)

        for x in range(1, response.json()['page']['totalPages']):
                response = requests.get(f'https://app.ticketmaster.com/discovery-widgets/v2/events?apikey={apikey}&size=11&radius=24&page={x}&venueId=KovZ917Aai0&city=Denver&countryCode=US&source=ticketmaster&postalCode=80202&startDateTime=2022-10-01T18:03:22Z&endDateTime=2023-10-01T18:03:22Z&latlong=&locale=*&sort=date,asc', headers=headers)
                df = venue_data(response)
                dfs.append(df) 

        df = pd.concat(dfs)

        return df

def herbs():    
    herbs = requests.get('http://www.herbsbar.com/live-music-calendar-1')

    herbs = BeautifulSoup(herbs.text, 'html.parser')
    herbs = herbs.findAll('article', {"class":"eventlist-event eventlist-event--upcoming eventlist-event--multiday"})

    def get_attrs(row):
        try:
            artist = row.find('h1', {"class":"eventlist-title"}).text
            date = row.find('time', {"class":"event-date"}).text
            link = 'herbsbar.com' + row.find('h1', {"class":"eventlist-title"}).find('a')['href']
            img_url ='sorry no image at this time'
            venue = 'Herbs'

            return [artist,date,link,venue,img_url]
        except:
            pass



    df = pd.DataFrame([get_attrs(x) for x in herbs])
    df.columns = ['Artist','Date','Link','Venue','img_url']

    def map_filters(row):
        return [x.strip() for x in re.split('with|Special Guest', row) if (x is not None) & (x != '')]

    df['FiltArtist'] = df.Artist.map(map_filters)
    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]
    
    return df

def paramount():
    headers = {
        'authority': 'alttix.ksehq.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://www.paramountdenver.com',
        'referer': 'https://www.paramountdenver.com/',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }

    response = requests.get('https://alttix.ksehq.com/api/tm/venue/KovZpZAFa1nA', headers=headers)
    df = pd.DataFrame(response.json())
    df['img_url'] = pd.json_normalize(pd.json_normalize(df['images'])[0])['url']
    df = df[['name','calendar_start_datetime','url','img_url']]
    df.columns = ['Artist','Date','Link','img_url']
    df['Venue'] = 'Paramount Thatre'

    def map_filters(row):
        return [x.strip() for x in re.split(':|presents|-', row) if (x is not None) & (x != '')]

    df['FiltArtist'] = df.Artist.map(map_filters)
    
    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]
    
    return df

def roxy():    
    roxy = requests.get('https://www.theroxydenver.com/')

    roxy = BeautifulSoup(roxy.text, 'html.parser')

    roxy = roxy.find('div',{"class":"hmt_cl"})

    roxy = roxy.select('div[class*="event_wrap"]')

    def get_attrs(row):
        try:
            date = row.find('div', {"class":"event_date"}).text
            artist = row.find('div',{"class":"event_name"}).text
            link = 'https://www.theroxydenver.com' + row.find('div',{"class":"event_name"}).find('a')['href']
            img_url = row.find('div', {"class":"flyer_wrapper"}).find('a')['href']

            return (artist, date, link, img_url)
        except:
            pass

    df = pd.DataFrame([get_attrs(x) for x in roxy])

    df = df.dropna()

    df.columns = ['Artist','Date','Link', 'img_url']
    df['Venue'] = 'Roxy'

    df['FiltArtist'] = df.Artist.map(lambda x : [x])

    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]

    return df

def lion():    
    lion = requests.get('http://lionslairco.com/')
    lion = BeautifulSoup(lion.text, 'html.parser')
    lion = lion.find('div', {"class":"eventlist eventlist--upcoming"})
    lions = lion.select('article[class*="eventlist-event"]')

    def get_attrs(row):    
        try:   
            date = row.find('time', {"class":"event-date"})['datetime']
            artist = row.find('h1').find('a').text
            link = 'http://lionslairco.com' + row.find('h1').find('a')['href']
            img_url = row.find('img')['data-image']

            return (artist, date, link, img_url)
        except:
            pass


    df = pd.DataFrame([get_attrs(x) for x in lions])
    df.columns = ['Artist','Date','Link','img_url']
    df['Venue'] = 'Lions Lair'
    def map_filters(row):
        return [x.strip() for x in re.split('\/|:|With|Guest', row) if (x is not None) & (x != '')]

    df['FiltArtist'] = df.Artist.map(map_filters)

    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]
    
    return df

def lost_lake():
    cookies = {
        '_ga': 'GA1.2.1263942177.1664652760',
        '_gid': 'GA1.2.1367907763.1664652760',
        '_gat_gtag_UA_207043591_1': '1',
    }

    headers = {
        'authority': 'lost-lake.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        # Requests sorts cookies= alphabetically
        # 'cookie': '_ga=GA1.2.1263942177.1664652760; _gid=GA1.2.1367907763.1664652760; _gat_gtag_UA_207043591_1=1',
        'referer': 'https://www.google.com/',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }

    lost = requests.get('https://lost-lake.com/events/', cookies=cookies, headers=headers)
    lost = BeautifulSoup(lost.text, 'html.parser')
    lost = lost.findAll('div', {"class":"col-12 eventWrapper rhpSingleEvent py-4 px-0"})


    def get_attrs(row):
        try:
            link = row.find('a', {"class":"url"})['href']
            artist = row.find('a', {"class":"url"})['title']
            img_url = row.find('img')['src']
            date = row.find('div', {"id":"eventDate"}).text.strip()

            return (artist, date, link, img_url)
        except:
            pass

    df = pd.DataFrame([get_attrs(x) for x in lost])

    df.columns = ['Artist','Date','Link','img_url']

    df['Venue'] = 'Lost Lake'

    def map_filters(row):
        return [x.strip() for x in re.split('w/|W/|\+|:|Presents', row) if (x is not None) & (x != '')]

    df['FiltArtist'] = df.Artist.map(map_filters)

    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]
    
    return df

def levitt():    
    levitt = requests.get('http://www.levittdenver.org/summer-concert-series')

    lev = BeautifulSoup(levitt.text, 'html.parser')

    lev = lev.select('div[class*="summary-item"]')


    def get_attrs(row):
        try:
            artist = row.find('img')['alt']
            img_url = row.find('img', {"class":"summary-thumbnail-image"})['data-image']
            date = row.find('time', {"class":"summary-metadata-item summary-metadata-item--date"}).text
            link = 'https://www.levittdenver.org/' + row.find('a', {"class":"summary-thumbnail-container sqs-gallery-image-container"})['href']
            return (artist, date, link, img_url)
        except:
            pass

    df = pd.DataFrame([get_attrs(x) for x in lev])

    df = df.drop_duplicates()

    df.columns = ['Artist', 'Date','Link','img_url']

    def map_filters(row):
        return [x.strip() for x in re.split('with|Featuring|:|,|;', row) if (x is not None) & (x != '')]

    df['Venue'] = 'Levitt Pavillion'
    df['FiltArtist'] = df.Artist.map(map_filters)

    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]
    
    return df

def mile10():    
    cookies = {
        '_fbp': 'fb.1.1664654531574.1363621523',
    }

    headers = {
        'authority': '10milemusic.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        # 'cookie': '_fbp=fb.1.1664654531574.1363621523',
        'referer': 'http://10milemusic.com/',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }

    mile_10 = requests.get('https://10milemusic.com/shows/', cookies=cookies, headers=headers)
    mile_10 = BeautifulSoup(mile_10.text, 'html.parser')

    miles = mile_10.select('div[class*="tribe-events-calendar-list__event-details"]')


    def get_attrs(row):
        try:
            date = row.find('time', {"class":"tribe-events-calendar-list__event-datetime"})['datetime']
            link = row.find('a')['href']
            artist = row.find('a')['title']
            img_url = 'No image at this time.'

            return (artist, date, link, img_url)
        except:
            pass


    df = pd.DataFrame([get_attrs(x) for x in miles])

    df.columns = ['Artist','Date','Link','img_url']

    df['Venue'] = '10 Mile'

    def map_filters(row):
        return [x.strip() for x in re.split('w/|-|\(|\)|:', row) if (x is not None) & (x != '')]

    df['FiltArtist'] = df.Artist.map(map_filters)

    df = df[['Artist','Date','Link','Venue','FiltArtist','img_url']]
    
    
    return df
