import yaml
import json     
import requests       


class client:
    url = " "
    
    
    @classmethod
    def seturl(cls,url):
            cls.url = url
            return cls.url

   