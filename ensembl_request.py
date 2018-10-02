
import json
import sys
import os
import requests
from ensembl_object import EnsemblObject
import mysql.connector as mc

# https://rest.ensembl.org/documentation/info/lookup

class MyApp:

    def open_db(self):
        mydb = mc.connect(
            host='localhost',
            user='root',
            password=os.environ.get("MySqlpassword"),
            database='ensembl'
        )
        return mydb

    def close_db(self, mydb):
        mydb.close()

    def dispatch(self, environ):
        query = environ['QUERY_STRING']
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']

        if method == 'GET' and path == "/ensebml":
            return json.dumps(self.get_results())
            # do something
        elif method == 'GET' and path == "/load":
            return json.dumps(self.retrieve_ensmbl_lookup())

        return "Your request is invalid, please try new URL"


    def retrieve_ensmbl_lookup(self):
        '''Find the species and database for a single identifier (gene, transcript or protein) '''
        server = "https://rest.ensembl.org"
        ext = "/lookup/id/ENSG00000157764?expand=1"
        r = requests.get(server+ext, headers={ "Content-Type" : "application/json"})

        data_dict = r.json()
        list_of_results = data_dict['Transcript']
        print(len(list_of_results))
        print(type(list_of_results))

        try:
            for _dict in list_of_results: # every item is a list of 21 dictionaries.
                _id = _dict['id']
                species = _dict['species']
                _end = _dict['end']
                _start = _dict['start']
                obj = EnsemblObject(_id, species, _end, _start)
                print(type(obj))
                try:
                    self.data_insert(obj)
                except Exception as exc:
                    print(exc)
        except Exception as exc:
            print(exc)

        return data_dict


    def data_insert(self, ensemblobject):
        mydb = self.open_db()
        mycursor = mydb.cursor()
        print("inserting")

        try:
            print("inserting")
            insert = 'INSERT INTO ensembl_lookup (_id, species, _end, _start) VALUES (%s, %s, %s, %s)'
            try:

                _tuple_of_values = (ensemblobject._id, ensemblobject.species, ensemblobject._end, ensemblobject._start)
                mycursor.execute(insert, _tuple_of_values)

            #mysql connector sth statement
                mydb.commit()
            except Exception as exc:
                print(exc)
        except Exception as exc:
            print("Not now")
        finally:
            mycursor.close()
            self.close_db(mydb)

    def get_results(self):
        mydb = self.open_db()
        mycursor = mydb.cursor()

        try:
            mycursor.execute("SELECT * FROM ensembl_lookup")

            myresult = mycursor.fetchall()

            return myresult
        except Exception as exc:
            print(exc)

        finally:
            mycursor.close()
            self.close_db(mydb)
        return myresult


    def get_sequence_location(self):
        mydb = self.open_db()
        mycursor = mydb.cursor()

        try:
            mycursor.execute("SELECT _start FROM ensembl_lookup")

            pos_start = mycursor.fetchall()

            return pos_start
        except Exception as exc:
            print(exc)

        finally:
            mycursor.close()
            self.close_db(mydb)
        #return pos_start


        #my_data = self.get_results()
        #return(my_data)


