#import web
import urllib
import urllib.error
import urllib.request
import urllib.parse
import requests
from bs4 import BeautifulSoup
#from selenium import webdriver
import time
import sys
import multiprocessing
#import pandas
import string
import json
import pickle
import os
import shutil


"""item = pandas.DataFrame({
    'first': 1,
    'second': 2,
    'third': [3, 2, 1]
})
item.to_csv('index_csv.txt', mode='a', index=False, header=False)
print(item)"""
#exit()


def lzip(*args):
    return list(zip(args))


def url_removed_protocol(url):
    return ''.join(url.split('/')[2:])


def index_url(url, html, soup):
    # Index a webpage into my database, which is currently index_csv.txt
    robots = soup.find('meta', attrs={'name': 'robots'})
    # There are other things the webpage can specify in the <meta name="robots"> tag that are not included here
    return_dict = {'noindex': False, 'nofollow': False, 'nosnippet': False}
    if robots:
        return_dict = get_disallowed_actions_from_string(robots['content'])
    if return_dict['noindex']:
        return return_dict
    html_files = next(os.walk('htmls'))[2]
    file_id = len(html_files) + 1
    with open('htmls/' + str(file_id), 'w+') as outfile:
        outfile.write(html)
    with open('html_number_key.txt', 'a') as outfile:
        outfile.write(url + '\n')
    """
    title = soup.find('title')
    if not title:
        title = soup.find('meta', attrs={'name': 'og:title'})
    if title:
        title = title.text
    else:
        main_header = ''
        # Find the largest heading tag
        for i in range(6):
            main_header = soup.find('h' + str(i))
            if main_header:
                break
        if main_header:
            title = main_header.text
        else:
            title = '\0'
    content_tag = soup.find('meta', attrs={'name': 'description'})
    if not content_tag:
        content_tag = soup.find('meta', attrs={'name': 'og:description'})
    content = '\0'
    if content_tag:
        content = content_tag['content']
    else:
        content_tag = soup.find('meta', attrs={'property': 'og:description'})
        if content_tag:
            content = content_tag['content']
    keywords = get_key_words(html, soup)
    data_to_store = {
        'url': [url],
        'title': [title],
        'content': [content],
        'keywords': keywords
    }
    #print("DAT: ", data_to_store)
    with open('index_csv.txt', 'a') as outfile:
        json.dump(data_to_store, outfile)
    #dataframe = pandas.DataFrame(data_to_store)
    #dataframe.to_csv('index_csv.txt', mode='a', index=False, header=False)"""
    return return_dict


def sort_dict_by_value(dictionary):
    return dict(sorted(dictionary.items(), key=lambda pair: pair[1], reverse=True))


def winerror10054_retryloop(url, user_agent):
    delay = 1
    max_retries = 3
    for i in range(max_retries):
        time.sleep(delay)
        try:
            try_url_get_code_block(url, user_agent)
            return True
        except Exception as e:
            delay *= 2
            print(e)
    return False


def html_to_ui_text(html):
    soup = BeautifulSoup(html, features='html.parser')
    text = ''
    for paragraph in soup.find_all('p'):
        text += ' ' + paragraph.get_text()
    for header in soup.find_all('h'):
        text += ' ' + header.get_text()
    for pre in soup.find_all('pre'):
        text += ' ' + pre.get_text()
    for span in soup.find_all('span'):
        text += ' ' + span.get_text()
    for line in soup.find_all('code'):
        text += ' ' + line.get_text()
    return text


def count_words(text):
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    words = text.split(' ')
    return_dict = dict()
    for word in words:
        if not word:
            continue
        number = return_dict.get(word)
        if number:
            return_dict[word] += 1
        else:
            return_dict[word] = 1
    return_dict = sort_dict_by_value(return_dict)
    return return_dict


def get_string_byte_size(string):
    return len(string.encode('utf-8'))


def http_headers_to_dict(headers):
    return_dict = dict()
    for header in headers:
        return_dict[header[0]] = header[1]
    return return_dict


def try_url_get_code_block(url, user_agent):
    headers = {
        'User-Agent': user_agent,
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept': 'text/html',
        'Accept-Language': 'en-US,en;q=0.8'
    }
    if url.split('/')[-1] == 'robots.txt':
        # Some sites don't have html for robots.txt,
        # they just return a text file.
        # Some give a 406 error if asked for text/html
        headers['Accept'] = 'text'
    request = urllib.request.Request(url, headers=headers, method='GET')
    with urllib.request.urlopen(request, timeout=10) as response:
        html = str(response.read())
        headers = http_headers_to_dict(response.getheaders())
        code = response.getcode()
    return {'html': html, 'headers': headers, 'code': code}


def url_get(url, user_agent):
    print("HTTP GET: ", url)
    # response = requests.get(url, headers=headers)
    # html = response.text
    return_dict = {'code': 9999}
    max_tries = 3
    for get_try in range(max_tries):
        # HTTP: 300-399 → Redirect
        # This loop keeps redirecting the site until it finds the correct site,
        # just in case the site redirect is incorrect
        try:
            return try_url_get_code_block(url, user_agent)
        except Exception as ERROR:
            print("ERROR: HTTP GET")
            if ERROR.__class__.__name__ == 'HTTPError':
                print("ERROR CODE: ", ERROR.code)
                if ERROR.code == 404:
                    return {'code': 404}
                elif ERROR.code == 406:
                    return_dict['code'] = 406
                    print("Retrying Error 406")
                    delay = 1
                    max_retries = 3
                    for i in range(max_retries):
                        time.sleep(delay)
                        try:
                            return try_url_get_code_block(url, user_agent)
                        except Exception as e:
                            delay *= 2
                            print(e)
                    return {'code': 406}
                elif ERROR.code == 400:
                    return_dict['code'] = 400
                    print("ERROR 400: ", ERROR.reason)
                    if str(ERROR.reason) == 'Bad Request':
                        return {'code': 400}
                elif ERROR.code == 302 or ERROR.code == 308 or ERROR.code == 301:
                    # HTTP 302 and HTTP 308 are redirect errors
                    return_dict['code'] = ERROR.code
                    response_headers = http_headers_to_dict(ERROR.headers)
                    oldurl = url
                    if response_headers.get('Location'):
                        url = response_headers['Location']
                    print(response_headers)
                    print("HTTP code " + str(ERROR.code) + ": Redirect from:", oldurl, "to:", url)
                    continue
                elif ERROR.code == 403:
                    # Forbidden
                    return {'code': 403}
                elif ERROR.code == 999:
                    # Request denied
                    return {'code': 999}
            elif ERROR.__class__.__name__ == 'URLError':
                print("URLError: ", ERROR.reason)
                if str(ERROR.reason) == '[WinError 10054] An existing connection was forcibly closed by the remote host':
                    return winerror10054_retryloop(url, user_agent)
                elif str(ERROR.reason)[:107] == '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: Hostname mismatch, certificate is not valid for':
                    # The site is not secure
                    print("ERROR: SSL: CERTIFICATE_VERIFY_FAILED")
                    return False
                elif str(ERROR.reason) == 'timed out':
                    return False
            elif ERROR.__class__.__name__ == 'RemoteDisconnected':
                print('ERROR: RemoteDisconnected')
                return False
            elif ERROR.__class__.__name__ == 'TimeoutError':
                print('ERROR: Timeout')
                return False
            # elif ERROR.__class__.__name__ == 'ConnectionResetError':
            #     print('ERROR: ConnectionResetError')
            #     if str(ERROR.reason) == '[WinError 10054] An existing connection was forcibly closed by the remote host':
            #         return winerror10054_retryloop(url, user_agent)
            elif ERROR.__class__.__name__ == 'urllib.error.URLError':
                print('ERROR: urllib.error.URLERROR: ' + str(ERROR))
                return False
            print("ERROR NAME: ", ERROR.__class__.__name__)
            raise ERROR
    return False
    """try:
        #response = requests.get(url, headers=headers)
        #html = response.text
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read()
        return str(html)
    except Exception as ex:
        #  urllib.error.HTTPError or urllib.error.URLError or ConnectionResetError
        name = ex.__class__.__name__
        print("ERRRRRRRRRRRRRrrrrr: ", name, url)
        if name != 'HTTPError' and name != 'URLError':
            raise Exception(ex)
        if name == 'URLError':
            print("URL: ", url)
        if name == 'HTTPError':
            time.sleep(0.1)
        return False"""


def get_site_url(url):
    splits = url.split('/')
    main_url = splits[0] + '//' + splits[2]  # This keeps the 'http' or 'https' beginning
    return main_url


def get_site_name(url):
    splits = url.split('/')
    main_name = splits[2]
    return main_name


def get_idx_of_string_in_string_list(item, string_list):
    top = len(string_list) - 1
    bottom = 0
    middle = int(top + bottom / 2)
    while top != bottom:
        if item > string_list[middle]:
            top = middle
        elif item < string_list[middle]:
            bottom = middle
        elif item == string_list[middle]:
            return middle
        middle = int(top + bottom / 2)
    if item == string_list[middle]:
        return middle
    else:
        return False


def load_pickled_item(file_name):
    if not os.path.exists(file_name):
        return False
    with open(file_name, 'rb') as infile:
        item = pickle.load(infile)
    return item


def save_item_as_pickled(item, file_name):
    with open(file_name, 'wb') as outfile:
        pickle.dump(item, outfile)


def get_key_words(html, soup):
    # Find keywords in <meta> tag
    keywords = soup.find('meta', attrs={'name': 'keywords'})
    if keywords and keywords.get('content'):
        content = keywords['content'].strip()
        # DO NOT remove whitespace inside the list of words.
        # Some keywords found this way are multiple words put together in a though, i.e. "Data Structure"
        keywords = content.split(',')
    else:
        ui_text = html_to_ui_text(html)
        if not ui_text.strip():
            title = soup.find('title')
            if not title:
                return []
            text = title.text
            keywords = text.translate(str.maketrans('', '', string.punctuation)).split(' ')
            return keywords
        word_dict = count_words(ui_text)
        keys = word_dict.keys()
        common_word_list = ['the', 'a']
        if len(keys) > len(common_word_list):
            for common_word in common_word_list:
                if common_word in word_dict:
                    word_dict.pop(common_word)
        else:
            for word in keys:
                if word in common_word_list:
                    word_dict.pop(word)
        keyword_count = 1 + int(len(ui_text) / (list(word_dict.values())[0] * len(word_dict)))
        keywords = list(word_dict.keys())[:keyword_count]
    return keywords


def get_disallowed_actions_from_string(info):
    return_dict = {'noindex': False, 'nofollow': False, 'nosnippet': False}
    if info:
        if 'none' in info:
            return_dict = {'noindex': True, 'nofollow': True, 'nosnippet': True}
        else:
            return_dict['noindex'] = 'noindex' in info
            return_dict['nofollow'] = 'nofollow' in info
            return_dict['nosnippet'] = 'nosnippet' in info
    return return_dict


class Crawler:
    # Maybey add multiprocessing???
    def __init__(self, start_urls, useragent, crawl_site=''):
        """if is_multiprocessing:
            self.manager = multiprocessing.Manager()
            self.urls = self.manager.list(start_urls)
            self.site_data = self.manager.dict()
            self.already_looked_at = self.manager.list()
            self.multiprocessing = is_multiprocessing  # Uses multiple cores or not
            self.to_be_indexed = self.manager.list()
            self.useragent = self.manager.list([useragent])
        else:"""
        self.current_urls = dict()
        for url in start_urls:
            site_url = get_site_url(url)
            if self.current_urls.get(site_url):
                self.current_urls[site_url].add({url})
            else:
                self.current_urls[site_url] = {url}
        print(self.current_urls)
        self.new_urls = dict()
        self.site_data = dict()
        self.already_looked_at = dict()
        #self.multiprocessing = is_multiprocessing  # Uses multiple cores or not
        self.to_be_indexed = []
        self.useragent = [useragent]
        self.crawl_site = crawl_site
        return

    def get_user_agent(self):
        return self.useragent[0]

    def get_site_data(self, url):
        site_url = get_site_url(url)
        site_data = self.site_data.get(site_url)
        if site_data:
            return site_data
        else:
            return False

    def store_site_data(self, url):
        user_agent = self.get_user_agent()
        return_dict = {'disallowed': [], 'crawl_delay': 0, 'noindex': False, 'nofollow': False, 'nosnippet': False}
        site_url = get_site_url(url)
        robots_url = site_url + '/robots.txt'
        robots_response = url_get(robots_url, self.get_user_agent())
        return_dict['last_visit'] = time.time()
        if not robots_response or robots_response['code'] >= 400:
            return False
        robots_html = robots_response['html']
        if robots_response['headers'].get('X-Robots-Tag'):
            disallowed_actions = get_disallowed_actions_from_string(robots_response['headers']['X-Robots-Tag'])
            for action in disallowed_actions.keys():
                return_dict[action] = disallowed_actions[action]
        # ↓ Get the disallowed for this crawler only, not other big-company crawlers
        user_agents = robots_html.split('User-agent: ')
        my_disallowed_text = ''
        for agent in user_agents:
            if '*' == agent[0]:
                my_disallowed_text += agent + '\\n'
            if user_agent in agent:
                my_disallowed_text += agent + '\\n'
        if not my_disallowed_text:
            my_disallowed_text = robots_html
        items = my_disallowed_text.split('\\n')
        for item in items:
            possible_bad_url = item[10:-1]
            if not possible_bad_url:
                continue
            if 'Disallow: ' == item[0:10] and possible_bad_url not in return_dict['disallowed']:
                if '/' == possible_bad_url[0]:
                    possible_bad_url = url + possible_bad_url
                return_dict['disallowed'].append(possible_bad_url)
            elif 'Crawl-delay: ' == item[0:13]:
                return_dict['crawl_delay'] = int(item[13:])
        if '/' in return_dict['disallowed']:
            return_dict['disallowed'] = ['/']
        self.site_data[site_url] = return_dict
        return return_dict

    def save_all_site_data(self):
        with open('site_data.txt', 'w') as outfile:
            json.dump(self.site_data, outfile)

    def load_all_site_data(self):
        with open('site_data.txt', 'r') as infile:
            content = infile.read()
            self.site_data = json.loads(content)

    def get_possible_urls(self, url, html, disallowed):
        #print("get_possible_urls")
        site_url = get_site_url(url)
        soup = BeautifulSoup(html, features='html.parser')
        page_a_tags = soup.find_all('a')
        hrefs = []
        for a_tag in page_a_tags:
            try:
                new_href = a_tag['href']
            except KeyError:
                #print("========================================KeyError")
                continue
            # Crawler not allowed to follow the link
            nofollow = a_tag.get('rel') and 'nofollow' in a_tag.get('rel')
            if nofollow or not new_href or self.crawl_site not in new_href:
                continue
            if '/' == new_href[0]:
                new_href = get_site_url(url) + new_href
            if self.new_urls.get(site_url):
                if new_href in self.new_urls[site_url]:
                    continue
            if len(new_href) < 11 or new_href in self.already_looked_at or '#' in new_href or \
                    'javascript:void(0)' in new_href or '?' == new_href[0] or 'https://' != new_href[0:8]:
                continue
            if not disallowed:
                hrefs.append(new_href)
                continue
            # ↓ Don't add url if the url is in the disallowed list
            is_bad_href = False
            for bad in disallowed:
                if new_href in bad:
                    is_bad_href = True
                    break
                if '*' in bad:
                    # '*' represents a wildcard, so we need to account for that
                    site_url = get_site_url(new_href)
                    url_to_check = new_href[len(site_url):]
                    my_splits = url_to_check.split('/')
                    bad_splits = bad.split('/')
                    if len(bad_splits) < len(my_splits):
                        splits_are_same = True
                        for i, bad_split in enumerate(bad_splits):
                            if my_splits[i] != bad_split and bad_split != '*':
                                splits_are_same = False
                        if splits_are_same:
                            # If href and disallowed URL have the same start, then the href must be disallowed
                            is_bad_href = True
                            break
            if is_bad_href:
                continue
            hrefs.append(new_href)
        return hrefs

    """def check_if_html_has_keyword(self, html):
        soup = BeautifulSoup(html, features='html.parser')
        text = ''
        for paragraph in soup.find_all('p'):
            text += paragraph.get_text()
        for header in soup.find_all('h'):
            text += header.get_text()
        for pre in soup.find_all('pre'):
            text += pre.get_text()
        for span in soup.find_all('span'):
            text += span.get_text()
        if not self.case_sensitive:
            text = text.lower()
        for keyword in self.keywords:
            if keyword in text:
                return True
        return False"""

    def crawl_url(self, url):
        site_url = get_site_url(url)
        site_data = self.get_site_data(url)
        if site_data == False:
            site_data = {'disallowed': [], 'crawl_delay': 0}
        if site_data.get('nofollow'):
            return False
        """if self.multiprocessing:
            if site_data['crawl_delay'] != 0:
                while time.time() - site_data['last_visit'] < site_data['crawl_delay']:
                    time.sleep(time.time() - site_data['last_visit'])
                self.site_data[site_url]['last_visit'] = time.time()
        else:"""
        if site_data['crawl_delay'] != 0:
            if time.time() - site_data['last_visit'] < site_data['crawl_delay']:
                self.current_urls[site_url].add(url)
                return False
        response = url_get(url, self.get_user_agent())
        if not response or response['code'] >= 400:  # The server blocks the bot from accessing {url}
            return False
        html = response['html']
        soup = BeautifulSoup(html, 'html.parser')
        robot_info = index_url(url, html, soup)
        if robot_info['nofollow']:
            return False
        possible_urls = self.get_possible_urls(url, html, site_data['disallowed'])
        if possible_urls:
            for new_url in possible_urls:
                new_site_url = get_site_url(new_url)
                if self.new_urls.get(new_site_url):
                    self.new_urls[new_site_url].add(new_url)
                else:
                    self.new_urls[new_site_url] = {new_url}

    def iter(self):
        start_time = time.time()
        print("-----------------ITERATING-----------------")
        processes = []
        keys = list(self.current_urls.keys())
        for key in keys:
            if not self.store_site_data(key):
                # The site probably doesn't exist
                self.current_urls.pop(key)
                keys.remove(key)
        i = -1
        while len(self.current_urls) > 0:
            i += 1
            if i > len(keys) - 1:
                i = 0
            if not self.current_urls.get(keys[i]):
                if self.current_urls.get(keys[i], None) is None:
                    keys = list(self.current_urls.keys())
                else:
                    self.current_urls.pop(keys[i])
                print("RESET KEYS")
                #print(self.current_urls)
                #time.sleep(1)
                continue
            url = self.current_urls[keys[i]].pop()
            print(len(self.current_urls), "sites remaining. URL: ", url)
            site_url = get_site_url(url)
            if self.already_looked_at.get(site_url):
                if url not in self.already_looked_at.get(site_url):
                    self.already_looked_at[site_url].append(url)
            else:
                self.already_looked_at[site_url] = [url]
            """if self.multiprocessing:
                new_process = multiprocessing.Process(target=self.crawl_url, args=url)
                processes.append(new_process)
                new_process.start()
            else:"""
            self.crawl_url(url)
        """if self.multiprocessing:
            for process in processes:
                process.join()"""
        self.current_urls = self.new_urls.copy()
        self.new_urls = dict()
        print(self.current_urls)
        print("SITES: ", len(self.current_urls))
        print("URLS: ", sum(len(url_list) for url_list in self.current_urls.values()))
        print("LOOKED_AT length: ", sum(len(url_list) for url_list in self.already_looked_at.values()))
        print("ELAPSED: ", time.time() - start_time)

    def run_indefinitely(self):
        while True:
            self.iter()
            save_item_as_pickled(self, 'crawler.pkl')
            time.sleep(3)

    def add_url(self, url):
        site_url = get_site_url(url)
        if self.current_urls.get(site_url):
            self.current_urls[site_url].append(url)
        else:
            self.current_urls[site_url] = [url]

    def clear(self):
        self.current_urls = dict()
        self.new_urls = dict()
        self.already_looked_at = dict()
        self.to_be_indexed[:] = []


def restart_database():
    os.remove('crawler.pkl')
    os.remove('html_number_key.txt')
    shutil.rmtree('htmls')
    os.mkdir('htmls')


def main():
    #multiprocessing.set_start_method('spawn')
    """driver = webdriver.Chrome()
    useragent = driver.execute_script("return navigator.userAgent")
    driver.quit()"""
    """print(count_words(
        html_to_ui_text(
            url_get('https://stackoverflow.com/questions/2132718/best-way-to-handle-list-indexmight-not-exist-in-python',
                     useragent)
        )
    ))"""
    useragent = "SuperTickler-500"
    print("USER_AGENT: ", useragent)
    mycrawler = load_pickled_item('crawler.pkl')
    if not mycrawler:
        start_urls = ['https://mowthatdirtylawn.blogspot.com/', 'https://www.w3schools.com/python/ref_set_pop.asp']
        mycrawler = Crawler(
            start_urls,
            useragent
        )
    mycrawler.run_indefinitely()
    exit()


if __name__ == "__main__":
    print("start")
    main()
