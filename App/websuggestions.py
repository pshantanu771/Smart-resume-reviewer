import requests
import urllib.request
from bs4 import BeautifulSoup

keywords = ['web development', 'Front-end development', 'Backend', 'Data science']
for keyword in keywords:
    url = f'https://www.naukri.com/{keyword}-jobs'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    job_links = soup.select('.jobTuple > .info > .title > a')
    for link in job_links:
        job_url = link['href']
        # print(job_url)


keywords = ['web development', 'Machine learning', 'Data science']

for keyword in keywords:
    url = 'https://www.youtube.com/results?search_query=' + keyword

    response = urllib.request.urlopen(url)
    html = response.read()

    soup = BeautifulSoup(html, 'html.parser')

    video_links = soup.find_all('a', {'class': 'yt-uix-tile-link'})

    # print('Videos related to ' + keyword + ':')
    

