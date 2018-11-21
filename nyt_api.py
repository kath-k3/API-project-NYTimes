import json
import sys
import os
import requests
import topstory
import mysql.connector as mc
from config import api_key

class MyApp:

    def open_db(self):
        mydb = mc.connect(
            host='localhost',
            user='root',
            password=os.environ.get("MYSQL_PASSWORD"),
            database='nyt_articles'
        )
        return mydb

    def close_db(self, mydb):
        mydb.close()

    def dispatch(self, environ):
        query = environ['QUERY_STRING']
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']

        if method == 'GET' and path == "/stories":
            return json.dumps(self.get_results())
            # do something
        elif method == 'GET' and path == "/load":
            return json.dumps(self.retrieve_top_stories())

        return "Your request is invalid, please try new URL"


    def retrieve_top_stories(self):
        r = requests.get("http://api.nytimes.com/svc/topstories/v2/home.json?api-key=api_key",
            json = True)

        data_dict = r.json()

        list_of_results = data_dict['results']
        list_of_custom_top_stories = []

        for article_dict in list_of_results:
            title = article_dict['title']
            abstract = article_dict['abstract']
            published_date = article_dict['published_date']
            short_url = article_dict['short_url']
            #image_url = article_dict['multimedia'][0]['url']

            width = 0
            image_url = ''
            for image in article_dict['multimedia']:
                if image['width'] > width:
                    image_url = image['url']
                    width = image['width']

            obj = topstory.TopStory(title, abstract, published_date, short_url, image_url)
            self.data_insert(obj)
            list_of_custom_top_stories.append(obj)

        return data_dict


    def data_insert(self, topstory):
        mydb = self.open_db()
        mycursor = mydb.cursor()

        try:

            insert = 'INSERT INTO topstories (title, abstract, published_date, short_url, image_url) VALUES (%s, %s, %s, %s, %s)'
            _tuple_of_values = (topstory.title, topstory.abstract, topstory.published_date, topstory.short_url, topstory.image_url)
            mycursor.execute(insert, _tuple_of_values)

            mydb.commit()
        except Exception as exc:
            print(exc)
        finally:
            mycursor.close()
            self.close_db(mydb)

    def get_results(self):
        mydb = self.open_db()
        mycursor = mydb.cursor()

        try:
            mycursor.execute("SELECT * FROM topstories")

            myresult = mycursor.fetchall()

            return myresult
        except Exception as exc:
            print(exc)

        finally:
            mycursor.close()
            self.close_db(mydb)
        return myresult
