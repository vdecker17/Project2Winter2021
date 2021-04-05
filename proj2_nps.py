#################################
##### Name: Vanessa Decker
##### Uniqname: vdecker
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

map_key = secrets.MPAQUEST_API_KEY
map_secret = secrets.MAPQUEST_API_SECRET

CACHE_FILE_NAME = 'project_2.json'
CACHE_DICT = {}

class NationalSite():
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category.strip()
        self.name = name.strip()
        self.address = address.strip()
        self.zipcode = zipcode.strip()
        self.phone = phone.strip()
    
    def info(self):
        return f'{self.name} ({self.category}): {self.address} {self.zipcode}'

def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()


def make_url_request_using_cache(url):
    try:
        CACHE_DICT = load_cache()
        output = CACHE_DICT[url]
        print("using cache")
        return output
    except:
        request = requests.get(url).text
        print("fetching")
        CACHE_DICT[url] = request
        save_cache(CACHE_DICT)
        return CACHE_DICT[url]

def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    html = requests.get('https://www.nps.gov/index.htm').text
    soup = BeautifulSoup(html, 'html.parser')
    search_state = soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch')
    state_urls = {}
    for url in search_state.find_all('a', href=True):
        state_urls[url.text.lower()] = ('https://www.nps.gov'+url['href'])
    return state_urls


def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    html = make_url_request_using_cache(site_url)
    soup = BeautifulSoup(html, 'html.parser')
    search_name = soup.find('div', class_='Hero-titleContainer clearfix')
    name = search_name.find('a', href=True, class_='Hero-title').text
    category = soup.find('span', class_='Hero-designation').text
    city = soup.find('span', itemprop='addressLocality').text
    state = soup.find('span', itemprop='addressRegion').text
    address = f'{city}, {state}'
    zipcode = soup.find('span', class_='postal-code').text
    phone = soup.find('span', class_='tel').text
    return NationalSite(category, name, address, zipcode, phone)


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    nat_site_list = []
    html = make_url_request_using_cache(state_url)
    soup = BeautifulSoup(html, 'html.parser')
    all_parks = soup.find('ul', id='list_parks')
    all_links = all_parks.find_all('li', class_='clearfix')
    for l in all_links:
        header = l.find('h3')
        link = header.find('a', href=True)
        site_url = link['href']
        url = f'https://nps.gov{site_url}'
        nat_site_list.append(get_site_instance(url))
    return nat_site_list


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    origin = site_object.zipcode
    url = f'http://www.mapquestapi.com/search/v2/radius?key={map_key}&origin={origin}&radius=10&units=m&maxMatches=10&ambiguities=ignore&outFormat=json'
    response = json.loads(make_url_request_using_cache(url))
    for result in response['searchResults']:
        if result['fields']['name'] == "":
            name = 'no name'
        else:
            name = result['fields']['name']
        if result['fields']['group_sic_code_name'] == "":
            category = 'no category'
        else:
            category = result['fields']['group_sic_code_name']
        if result['fields']['address'] == "":
            address = 'no address'
        else:
            address = result['fields']['address']
        if result['fields']['city'] == "":
            city = 'no city'
        else:
            city = result['fields']['city']
        print(f"{name} ({category}): {address}, {city}")
    return response

if __name__ == "__main__":
    state_dict = build_state_url_dict()
    print()
    while True:
        state = input('Enter a state name (e.g. Michigan, michigan) or "exit": ').lower()
        if state == 'exit':
            break
        if state not in build_state_url_dict().keys():
            print('Please enter a valid state name')
        else:
            url = state_dict[state]
            count = 1
            print('----------------------------------')
            print('List of national sites in michigan')
            print('----------------------------------')
            sites = get_sites_for_state(url)
            for site in sites:
                print(f'[{count}] {site.info()}')
                count += 1
        selection = input('Choose a number from the list for details or "back" or "exit": ')
        if selection == 'exit':
            break
        if int(selection) < count-1:
            site = sites[int(selection)-1]
            get_nearby_places(site)
        if int(selection) > count-1:
            print("go back")
        if selection == 'back':
            continue