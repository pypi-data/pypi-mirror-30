from lxml import html
import argparse
import requests
import re
import shutil
import os


class Manga:
    def __init__(self,url,date,name,chapter,title):
        self.url=url
        self.name=name
        self.chapter=chapter
        self.title=title
        self.date=date

    def __str__(self):
        return self.name+'-Chapter '+self.chapter+' '+self.title


HOST = 'https://readms.net'
NEW_RELEASES_XPATH = '//div[@class="side-nav hidden-xs"]/ul[@class="new-list"]/li[@class="active"]/a'
MANGA_PAGES_XPATH = '//div[@class="btn-group btn-reader-page"]/ul[@class="dropdown-menu"]/li'
IMG_PAGE_XPATH = '//*[@id="manga-page"]'


def get_new_releases():
    page=requests.get(HOST)
    tree=html.fromstring(page.content)
    results = tree.xpath(NEW_RELEASES_XPATH)
    new_releases=[]
    for r in results:
        details=[t.strip() for t in r.itertext()]
        manga=Manga(r.get('href'),details[0],details[1],details[2],details[3])
        new_releases.append(manga)
    return new_releases


def get_manga_image(url):
    page=requests.get(url)
    tree=html.fromstring(page.content)
    img_xpath=tree.xpath(IMG_PAGE_XPATH)
    img_url=img_xpath[0].get("src")
    print("Downloading image "+img_url)
    response=requests.get('https:'+img_url, stream=True)
    url=url.split('/')
    name=url[4]
    chapter=url[5]
    page=url[-1]
    #create directory for manga images if not exist
    directory=name+'/'+chapter
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_name=url[4]+'_'+url[-1]+'.png'
    with open(directory+'/'+file_name, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


def download_manga(name):
    page=requests.get(HOST)
    tree=html.fromstring(page.content)
    results=tree.xpath(NEW_RELEASES_XPATH+'[contains(text(),"'+name+'")]')
    if len(results)==1:
        manga=results[0]
        manga_url=HOST+manga.get('href')

        #Load first page
        page=requests.get(manga_url)
        tree=html.fromstring(page.content)
        page_elements=tree.xpath(MANGA_PAGES_XPATH)
        max_page=int(re.sub('[^0-9]','',page_elements[-1].text_content()))
        for i in range(1,max_page+1):
            manga_url=manga_url.rsplit('/',1)[0]+'/'+str(i)
            get_manga_image(manga_url)
    else:
        print("No latest chapter for that manga")


def display(mangas):
    print('**********Latest Release**********')
    for manga in mangas:
        print(manga.name.ljust(25)+' Chapter-'+manga.chapter.ljust(3)+(' ('+manga.title+')'))


def main():
    parser=argparse.ArgumentParser(description='CLI tool to check and download latest manga on readms.net',
                                     formatter_class=argparse.RawTextHelpFormatter)
    help_desc="latest".ljust(24)+"- Get latest manga in readms"+"\ndownload ${manga_name}".ljust(24)+" - Will download the latest chapter manga. Run first the python readms.py latest to s" \
                                                                                                     "see available manga"
    parser.add_argument('command', help=help_desc, nargs='+')
    args=parser.parse_args()

    command=args.command
    if command[0] == "latest" and len(command) == 1:
        new_releases=get_new_releases()
        display(new_releases)
    elif command[0] == "download" and len(command) == 2:
        download_manga(command[1])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

