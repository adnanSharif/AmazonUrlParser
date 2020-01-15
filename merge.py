
from lxml import html
# from bs4 import BeautifulSoup as bs 
import csv
import os
import json
from furl import furl
import requests
import random
from time import sleep

def ReadAsin():
    f=open("input.txt", "r")
    AsinList = list(f)
    # print(AsinList)
    f.close()
    lista = []
    for i in AsinList:
        if( os.path.exists('data/'+i.strip()+'.json')):
            f=open('data/'+i.strip()+'.json', "r")
            data = json.load(f)
            f.close()
            lista.append(data)
    
    f = open("output_json.txt", "w")
    json.dump(lista, f, indent=4)
    f.close()
if __name__ == "__main__":
    ReadAsin()
