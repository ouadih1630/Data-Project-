import os
from pickletools import int4 
import re 
import time 
from bs4 import BeautifulSoup 
import pandas as pd 
from selenium import webdriver  
from selenium.webdriver.firefox import options as firefox_options 

def get_page(count=1):
  driver=webdriver.Firefox()
  pages= []
  for page_nb in range(1,count+1):
    page_url=f"https://www.logic-immo.com/appartement-paris/location-appartement-paris-75-100_1-{page_nb}.html"
    driver.get(page_url)
    time.sleep(10)
    pages.append(driver.page_source.encode("utf-8"))  
  return pages 

def save_pages(pages):
    os.makedirs("data",exist_ok=True)
    for page_nb, page in enumerate(pages) :
        with open(f"data/page_{page_nb}.html","wb") as f_out:
            f_out.write(page)

def parse_pages():
  results= pd.DataFrame()

  pages_path = os.listdir("data")
  for page_path in pages_path:
        with open("data/"+ page_path,"rb") as f_in:
            page = f_in.read().decode("utf-8")
            result= parse_page(page)
            results=results.append(result)
  return results

def parse_page(page):
  result= pd.DataFrame()
  soup = BeautifulSoup(page,"html.parser")
  areas=soup.find_all(attrs={"class": "announceDtlInfos announceDtlInfosArea"})
  prices=soup.find_all(attrs={"class": "announceDtlPrice"})
  nb_pieces=soup.find_all(attrs={"class":"announceDtlInfos announceDtlInfosNbRooms"})
  types=soup.find_all(attrs={"class": "announceDtlInfosPropertyType"})
  Descriptions=soup.find_all(attrs={"class":"announceDtlDescription"})
  emplacements=soup.find_all(attrs={"class":"announcePropertyLocation"})
  result["description"]=[tag.text.strip() for tag in Descriptions]
  result["emplacement"]=[clean_codepostal(tag) for tag in emplacements]
  result["type"]=[clean_type(tag) for tag in types]
  result["Surface m²"]=[clean_surface(tag) for tag in areas]
  result["Price €"]=[clean_price(tag) for tag in prices]
  result["nb_piece"]=[clean_piece(tag) for tag in nb_pieces]
  result
  return result
def clean_codepostal(tag):
  text=tag.text.strip().replace("PARIS","").replace(" ","")
  return (re.match(".*\(([0-9]+)\.*",text)).groups()[0]
  
def clean_type(tag):
  text=tag.text.strip()
  return text.replace("Location","")

def clean_piece(tag):
  text=tag.text.strip()
  return int(text.replace("pièces","").replace("pièce",""))

def clean_surface(tag):
  text=tag.text.strip()
  return int(text.replace("m²",""))

def clean_price(tag):
  text=tag.text.strip()
  text=text.replace("€","").strip()
  return int("".join(text.split()))


def main():
  # pages=get_page()
  # save_pages(pages)
  result=parse_pages()
  print(result)
  
if __name__ == "__main__":
  main()