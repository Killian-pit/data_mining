import bs4 
from requests import get
import pandas as pd 
import numpy as np 

from time import sleep
from random import randint,shuffle

class crawler:
    def __init__(self,url):
        self.url       = url
        self.headers   = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def get_front_page(self):
        """
        description :
        get the displayed category on the front page 
        
        params:
        url : url of the front page
        """
        page = get(self.url,headers=self.headers) # connect
        html_soup = bs4.BeautifulSoup(page.text, 'lxml')

        front_page   = html_soup.find_all(class_ = 'ars_hp_c_b')
        front_category = []
        print(f"Found {len(front_page)} category on the front page ")
        for i in front_page:
            front_category.append(i.text.replace("\n",''))

        return front_category


    def get_category(self):
        """
        desccription :
        from the main page get all the different categories 
        params:
        url : url of the main page 
        output :
        dataframe of the scanned products 
        """
        category_url = []
        page = get(self.url,headers=self.headers) # connect
        html_soup = bs4.BeautifulSoup(page.text, 'lxml')
        name_containers   = html_soup.find_all(class_ = 'newSubmenuList__link')
        
        for i in (name_containers):
            try:
                category_url.append(i["href"][1:])
            except:
                pass     

        found_cat = list(set(category_url))

        shuffle(found_cat)
        self.category = found_cat

    def get_articles_category(self,url_search):
        """
        desccription :
        crawler for the categories pages
        aggregate the information to a dataframe
        
        params:
        url : url of the category page 
        output :
        return dataframe
        """
            
        page = get(url_search) # connect
        html_soup=bs4.BeautifulSoup(page.text,"lxml")
        data = []
        
        # get all pages from a category
        paging = html_soup.findAll(class_='ajax-facet-value updateFacet')
        page_list = 0
        
        # count the number of pages 
        for i in (paging):
            try:
                if 'page=' in i['href']:
                    page_list = int(i['href'].split('=')[-1]) if int(i['href'].split('=')[-1])>page_list else page_list
            except:
                print('No usable URL on this page')     
        print(f" This category have {page_list} pages")

        # iterate over pages of the category 
        if (page_list>1) & (page_list<100) : 
            for i in range(1,page_list+1):
                print(f'   Start scanning page {i}')
                url_page  = url_search+"&page="+str(i)
                page = get(url_page) # connect
                html_soup=bs4.BeautifulSoup(page.text,"lxml")

                # class with product informations 
                fff = html_soup.findAll(class_="sm-category__item")
                for i in (fff):
                    try:
                        # basic product info (name,price ,id)
                        j=i.find(class_="js-compare-link")
                        
                        # get the info about delivery 
                        k = i.find(class_="b-freeShipping")
                        k = k['title'] if k is not None else "None"
                        
                        # display the amount of discount
                        l = i.find(class_='smTileOldpriceBlock__discount')
                        l = l.text if l is not None else "None"
                       
                        data.append([str(j['data-name']),
                                     int(j['data-id']),
                                     int(j['data-price']),
                                     str(k),
                                     str(l)])

                    except:
                        print('no url')

                #print(f"Article gathered {len(data)}")
                #sleep(randint(1,3))

            df=pd.DataFrame(data,columns=['Name','id','price','shipping','discount'])
            return df.drop_duplicates()
    
        # if only one page : stay on the current page 

        else:
            fff = html_soup.findAll(class_="sm-category__item")
           # print(f"Article on current page {len(fff)}")

            # add a condition for subcategory 
            if len(fff)==0:
                try:
                    f = html_soup.findAll(class_="sm-image-holder")

                    # do nothing and append the sub cat to the categories 
                    for i in f:
                        self.category.append(self.url[:-1]+i["href"]) 
                    #print(f'Found {len(f)} subcategories')

                    # unsure no doubles 
                    self.category = list(set(self.category))
                except:
                    #print("No subcategory")
                    pass


            for i in (fff):
                try:
                    for i in (fff):
                        # basic product info (name,price ,id)
                        j=i.find(class_="js-compare-link")
                        
                        # get the info about delivery 
                        k = i.find(class_="b-freeShipping")
                        k = k['title'] if k is not None else "None"
                        
                        # display the amount of discount
                        l = i.find(class_='smTileOldpriceBlock__discount')
                        l = l.text if l is not None else "None"
                       
                        data.append([str(j['data-name']),
                                     int(j['data-id']),
                                     int(j['data-price']),
                                     str(k),
                                     str(l)])
                except:
                    print('no url') 

            #print(f"Article gathered {len(data)}")
            df=pd.DataFrame(data,columns=['Name','id','price','shipping','discount'])
            #sleep(randint(1,3))
            return df.drop_duplicates()

    def get_all_articles(self):
        """
        description :
        get all the articles on the site 

        """
        df=pd.DataFrame()
        self.get_category()

        print(f"found {len(self.category)} categories ")

        for category in self.category:
            url_search = self.url + category + '?pageSize=120'
            #print(url_search)
            dftemp = self.get_articles_category(url_search) # connect
            #print(dftemp.shape)
            df = df.append(dftemp,ignore_index=True)
            print(f"Total Item gathered : {df.shape[0]}",end=\r)
        return df

