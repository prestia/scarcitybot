import os #needed to read and write to the ledger
import hashlib #needed to compute the md5 hash
import urllib.request #needed to scrape the web
from datetime import datetime #needed to update ledger with the date

debug = False #if True it will print a bunch of garbage for debugging
publish = True #if True it will tweet

if publish:
  from twython import Twython
  from keys import *

def main():
  path = os.path.dirname(os.path.abspath(__file__)) #gets the path of the generator.py file
  
  if debug:
    f = open(path + '/devledger', 'r+') #opens devledger for reading and writing at the beginning of the file
  else:
    f = open(path + '/ledger', 'r+') #opens ledger for reading and writing at the beginning of the file
  
  last_line = f.readlines()[-1] #get the last line of the file
  last_url = "http://stfj.net/scarcity/"+last_line.split()[0] #get the last known good url
  
  if not is_page_alive(last_url): #check to see if the page is still live
    update_ledger(f,last_line)

  f.close()

def is_page_alive(u):
  if debug: print(u)
  page_content = urllib.request.urlopen(u).read().decode('utf-8') #read the content of the page
  if debug: print(page_content)
  if "Not Found" in page_content: #if the old page is gone
    return False
  else:
    return True
  
def generate_key(key_file):
  keystring = ""
  last_modified = ""
  
  key_file.seek(0,0) #restart at the beginning of the file
  
  for line in key_file: #iterates over each line in the file
    if len(line.split()) > 1: #checks to see if the most recent line has a last modified date
      keystring += line[0]
      if debug: print(keystring)
      last_modified = line.split()[1]
      if debug: print(last_modified)

  return hashlib.md5((keystring+last_modified).encode('utf-8')).hexdigest()
  
def update_ledger(key_file,end_line):
  if not len(end_line.split()) > 1: #skips writing the date if one already exists
    datetime.today().strftime('%Y-%m-%d')
    key_file.write(" "+ datetime.today().strftime('%m%d%Y'))

  key_file.write("\n"+generate_key(key_file))
  new_url="http://stfj.net/scarcity/"+generate_key(key_file)

  if publish:
  	tweet(new_url)
  if debug: print(new_url)
  
def tweet(msg):
  t = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
  t.update_status(status=msg)

if __name__ == "__main__":
  main()
