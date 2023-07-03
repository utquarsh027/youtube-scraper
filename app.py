import pandas as pd
from flask import Flask, render_template, request
from flask_cors import CORS,cross_origin
import logging
import sys
import pymongo
import requests
from pymongo.mongo_client import MongoClient

application = Flask(__name__)
app=application

logging.basicConfig(filename='YTWebScrapper.log',level=logging.DEBUG,format= '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/scrapping',methods=['POST','GET']) # route to show the youtube scraped data in a web UI
@cross_origin()
def get_yt_data():
    if request.method == 'POST':
        try: 

            # My Lambda API Url below 
            api_url = ' https://dnfd3opnia.execute-api.us-east-1.amazonaws.com/default/youtube-api'
            searchString = request.form['content']
            # Keeping the url in dictionary format as below for API purpose
            content = 'https://www.youtube.com/'+searchString+'/videos' 
            print(content)                      
            url_json = {'url':content}

            # Getting Response from Lambda API
            response = requests.post(api_url,json=url_json)

            if response.ok:
                dct = response.json()
                channelName = dct['channel_title']
                df = pd.DataFrame(dct['output'])
                logging.info('Successfull Response from API 200')  
                lst=list(dct['output'].values())
                mydict=[{'Title':x,'PostingTime':y,'VideoUrl':a,'ThumbnailURL':b,'Views':z} for x,y,z,a,b in zip(*lst)] 
                print(mydict)           
                # Saving to pymongo
                uri = "mongodb+srv://jutkarsh027:Zj1KGWZ1h9hmXIfJ@cluster0.uk56ygo.mongodb.net/?retryWrites=true&w=majority"
                client = MongoClient(uri)
                db = client['yt_aws_scrapper']
                collection = db['yt_data']
                collection.insert_one(dct)
                return render_template('results.html',scrapping=mydict)
            else:
                print('Error Occured Please check URL')
                logging.info('Response not recieved from API')
                return 'Please check URL'
            
        except Exception as e:
            print('Exception Occured : ',e)
            logging.error(f'Error occured :{e}')
            return f'Exception Occured : {e}'        
        
    else:
        return render_template('index.html') 

   
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)