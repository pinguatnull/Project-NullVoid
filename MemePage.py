from urllib import response
from flask import Flask, render_template, request, send_file
import requests
import json
import socket
import os
import time

app = Flask(__name__)

def get_meme():
    url ="https://meme-api.herokuapp.com/gimme/terriblefacebookmemes"
    response = json.loads(requests.request("GET",url).text)
    meme_large = response["preview"][-2]
    subreddit = response["subreddit"]
    return meme_large, subreddit
    return response

@app.route("/")
def index():
    meme_pic,subreddit = get_meme()
    return  render_template("meme_index.html", meme_pic=meme_pic, subreddit=subreddit)

@app.route('/download')
def download():
   return send_file('Meme.pyw', as_attachment=True)

app.run(host = "0.0.0.0", port=80)

      
