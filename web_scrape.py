import requests
import BeautifulSoup

req = requests.request('GET','https://web.expasy.org/cellosaurus/CVCL_1058')
doc = BeautifulSoup.BeautifulSoup(req.content)

print doc

