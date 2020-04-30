# This script was created in order to work easier with internal company documentation.
# Some parts are rewritten/deleted and that is causing this code to throw errors.
# This script is supposed to demonstrate the level of my programming skills
# and to serve the purpose of potential hiring process.


from markdown import markdown
import re
import string
import requests
import os
import getauth # is not part of this repo due to security reasons
import time

'''

INSTRUCTIONS:
-------------
known bugs:
    - splogs (Kibana) + some DataDog links
    - emedded markdown files
    - pictures: need to mention the file/folder in `exclude` list

1. Do not forget to change `wiki_path` when switching to another wiki!

2. Upload your onw cookies to the `getauth.py` file.
    - go to all the mentioned pages (such as gitlab, slack, etc. - you 
    can possibly add some if necessary for your wiki) when having the dev
    tool active
    - copy the request as CURL and transpose it in HTTP request with
    the first converter you find on google
    - copy the generated reques to `getauth.py` under corresponding key

* There is one cookie in this file as well -> `kiwi.wiki` - change this too

3. `cd` to the root of your wiki repo

4. Run lynx checker with `python lynx-checker.py` (or similar, according 
to the path where you have downoladed your lynx-checker.py and getauth.py
files)

'''
wiki_path = 'https://kiwi.wiki/autobooking/handbook/'

def get_files():
    '''
    get the list of files in the entire directory/repository including
    all files in subdirectories
    '''
    current_path = os.getcwd()

    files = []

    exclude = [
        '.DS_Store',
        '.config',
        '.git',
        '.coafile',
        '.gitignore',
        '.gitlab-ci.yml',
        '.nojekyll',
        'css.css',
        'img',
        'favicon.png',
        'index.html'
    ]

    for root, dirnames, filenames in os.walk(current_path):
        if not root in exclude:
            #print(root)
            dirnames[:] = [d for d in dirnames if d not in exclude]
            #print(dirnames)
            filenames[:] = [f for f in filenames if f not in exclude]
            #print(filenames)
            for i in filenames:
                files.append('{}/{}'.format(root, i))
    return files

def parse_links(content):
    '''
    parse links from html page based on given regex
    '''
    pattern = 'href=".*?"'
    links_obj = re.findall(pattern, content)
    links = []
    for link in links_obj:
        link = link[6:int(len(link))-1]
        links.append(link)
    return links

def make_request(links):
    '''
    use links to make requests
    get requests status codes
    stdout: links with status codes
    '''

    for link in links:
        if 'kiwi.wiki' in link and 'https://' in link:
            headers = {
                'hidden part of code'
            }
            r = requests.get(
                link,
                headers=headers,
            )
            status = r.status_code
            print('\nChecking {}: {}\n'.format(link, status))
            time.sleep(1)
        elif 'https://' in link or 'http://' in link:
            auth_item = getauth.get_headers(link)
            if auth_item is dict:
                if auth_item['authority']:
                    headers = auth_item
                    r = requests.get(
                        link,
                        headers=headers,
                    )
                    status = r.status_code
                    print('\nChecking {}: {} \n'.format(link, status))
                    time.sleep(1)
                else:
                    cookies = auth_item
                    r = requests.get(
                        link,
                        cookies=cookies,
                    )
                    status = r.status_code
                    print('\nChecking {}: {} \n'.format(link, status))
                    time.sleep(1)
            elif auth_item is list:
                try:
                    headers = auth_item[0]['headers']
                    cookies = auth_item[1]['cookies']
                    r = requests.get(
                        link,
                        headers=headers,
                        cookies=cookies,
                    )
                    status = r.status_code
                    print('\nChecking {}: {} \n'.format(link, status))
                    time.sleep(1)
                except IndexError:
                    print('{}: Could not authenticate. \n'.format(link))
            else:
                print('{}: Could not authenticate. \n'.format(link))
                # print(auth_item)
        else:
            headers = {
                'hidden part of code'
            }
            response = requests.get(
                '{}{}'.format(wiki_path, link),
                headers=headers
            )
            status = response.status_code
            print('\nChecking {}: {} \n'.format(link, status))
            time.sleep(1)
            if status == 404:
                try:
                    link_split = link.split('#')
                    link = '{}?id={}'.format(link_split[0], link_split[1])
                    response = requests.get(
                        '{}{}'.format(wiki_path, link),
                        headers=headers
                    )
                    status = response.status_code
                    print('\t Did not succeed, checking:\n\t {}: {}\n'.format(link, status))
                    if status == 404:
                        try:
                            link_split = link.split('.md')
                            link = '{}.md{}'.format(link_split[0], link_split[1])
                        except (AttributeError, IndexError):
                            link_split = link.split('?id=')
                            link = '{}.md?id={}'.format(link_split[0], link_split[1])
                        response = requests.get('{}{}'.format(wiki_path, link), headers=headers)
                        status = response.status_code
                        print('\t Did not succeed, checking:\n\t {}: {}\n'.format(link, status))
                except (AttributeError, IndexError):
                    response = requests.get('{}{}{}'.format(wiki_path, link, '.md'), headers=headers)
                    status = response.status_code
                    print('\t Did not succeed, checking:\n\t {}{}: {}\n'.format(link, '.md', status))

def main():
    files = get_files()
    for i in files:
        with open(i, 'rb') as f:
            md_content = markdown(f.read())
            links = parse_links(md_content)
            print(
                '---------------------------------------------\n',
                'IN FILE: ',
                i,
                '\n--------'
            )
            make_request(links)


if __name__ == "__main__":
    main()
