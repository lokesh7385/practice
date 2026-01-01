from bs4 import BeautifulSoup
import pandas as pd
import requests

url = "https://www.scrapethissite.com/pages/simple/"

page = requests.get(url)

soup = BeautifulSoup(page.text,features="html.parser")

#below are all the column names found through inspect
country_name = soup.find_all("h3",class_="country-name")

country_capital = soup.find_all("span",class_="country-capital")

country_population = soup.find_all("span",class_="country-population")

country_area = soup.find_all("span",class_="country-area")

#clean data if not used this then insted if text we will copy list meaning ex like this :- [abudabi]

country_name = [i.text.strip() for i in country_name]

country_capital = [i.text.strip() for i in country_capital]

country_population = [i.text.strip() for i in country_population]

country_area = [i.text.strip() for i in country_area]

#new_data is a dataframe

new_data = pd.DataFrame({"country_name":country_name,"country_capital":country_capital,"country_population":country_population,"country_area":country_area})

new_data['country_capital'] = new_data['country_capital']

new_data['country_population'] = new_data['country_population']

new_data['country_area'] = new_data['country_area']

print(new_data)

new_data.to_csv(r"E:\python\python\practice\web_scraper\country_data.csv",index=False)

print(new_data.head())