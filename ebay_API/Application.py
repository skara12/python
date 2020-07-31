#!/usr/bin/env python3
import webbrowser
import datetime
import os
import sys
import yaml
import json
from ebaysdk.trading import Connection

def GetSessionID():
 api = Connection(config_file='ebay.yaml', domain="api.ebay.com")

 with open("config.yaml") as file:
  cfg = yaml.load(file)
  runam = cfg['runame']

 request = { 'RuName': runam

	    }

 response = api.execute('GetSessionID',request)
 webbrowser.open("https://signin.ebay.com/ws/eBayISAPI.dll?SignIn&runame=" + runam  + "&SessID=" + response.reply.SessionID)
 return response.reply.SessionID

def FetchToken(SessionID):
 api = Connection(config_file='ebay.yaml', domain="api.ebay.com")

 request = { 'SessionID':SessionID}

 response = api.execute('FetchToken',request)

 with open("ebay.yaml") as file:
  cfg = yaml.load(file)
  dict_file = {'name': 'ebay_api_config' , 'api.ebay.com' :  {'compatability': cfg["api.ebay.com"]["compatability"] , 'appid': cfg["api.ebay.com"]["appid"] , 'certid': cfg["api.ebay.com"]["certid"] , 'devid' : cfg["api.ebay.com"]["devid"] , 'token': response.reply.eBayAuthToken}}

 with open ('user.yaml','w') as file:
  documents = yaml.dump(dict_file, file,default_flow_style=False)
 return response.reply.eBayAuthToken

def CreateUser(user,token):
 with open('profiles.json') as json_file:
  data = json.load(json_file)
  temp = data['profiles']
  y = {"user": user,
       "token": token}
  temp.append(y)

 with open("profiles.json", "w") as f:
  json.dump(data,f,indent=4)


def LoadUser(user):
 check_user = False
 with open("profiles.json") as json_file:
  data = json.load(json_file)
  temp = data['profiles']
  for pro in temp:
   if(user == pro['user']):
    check_user = True
    with open("ebay.yaml") as yaml_file:
     cfg = yaml.load(yaml_file)
     dict_file = {'name': 'ebay_api_config' , 'api.ebay.com' :  {'compatability': cfg["api.ebay.com"]["compatability"] , 'appid': cfg["api.ebay.com"]["appid"] , 'certid': cfg["api.ebay.com"]["certid"] , 'devid' : cfg["api.ebay.com"]["devid"] , 'token': pro['token'] }}
 if(check_user == True):
  with open ('user.yaml','w') as file:
   documents = yaml.dump(dict_file, file,default_flow_style=False)


def GetActiveItems():

 api = Connection(config_file='user.yaml', domain="api.ebay.com")

 currentDT = datetime.datetime.now()
 a_bool = True
 pgnum = 1
 #print(currentDT.strftime("%Y-%m-%dT%H:%M:%S"))

 while a_bool:
  request = { 'ErrorLanguage':'en_US',
             'WarningLevel':"High",
             'StartTimeFrom':"2020-05-01T00:00:00",
             'StartTimeTo':currentDT.strftime("%Y-%m-%dT%H:%M:%S"),
             'GranularityLevel':'Medium',
             'Pagination':{
                'EntriesPerPage':200,
	        'PageNumber':pgnum,
            }
  }

  response = api.execute('GetSellerList',request)
  if(pgnum < int(response.reply.PaginationResult.TotalNumberOfPages)):
   pgnum  = pgnum + 1
  else:
   a_bool = False

  if(int(response.reply.ReturnedItemCountActual) > 1):
   for Item in response.reply.ItemArray.Item:
    if(Item.SellingStatus.ListingStatus == "Active"):
     print(f"Title:{Item.Title}, Price:{Item.SellingStatus.CurrentPrice}, Status:{Item.SellingStatus.ListingStatus},ID:{Item.ItemID}, Quantity:: {Item.Quantity}\n") 
  else:
    if(response.reply.ItemArray.Item.SellingStatus.ListingStatus == "Active"):
     print(f"Title:{Item.Title}, Price:{Item.SellingStatus.CurrentPrice}, Status:{Item.SellingStatus.ListingStatus}, ID:{Item.ItemID}, Quantity: : {Item.Quantity}\n") 

def GetActiveItemsbyDay(ddays):
 api = Connection(config_file='user.yaml', domain="api.ebay.com")

 currentDT = datetime.datetime.now()
 startDT= datetime.datetime.now() - datetime.timedelta(days=100) 
 a_bool = True
 pgnum = 1
 EndItemStr = []
 while a_bool:
  request = { 'ErrorLanguage':'en_US',
             'WarningLevel':"High",
             #'StartTimeFrom':"2020-05-01T00:00:00",
             'StartTimeFrom':startDT.strftime("%Y-%m-%dT%H:%M:%S"),
             'StartTimeTo':currentDT.strftime("%Y-%m-%dT%H:%M:%S"),
             'GranularityLevel':'Medium',
             'Pagination':{
                'EntriesPerPage':200,
	        'PageNumber':pgnum,
            }
  }

  response = api.execute('GetSellerList',request)
  if(pgnum < int(response.reply.PaginationResult.TotalNumberOfPages)):
   pgnum  = pgnum + 1
  else:
   a_bool = False

  if(int(response.reply.ReturnedItemCountActual) > 1):
   for Item in response.reply.ItemArray.Item:
    if(Item.SellingStatus.ListingStatus == "Active" and (currentDT - Item.ListingDetails.StartTime).days >= int(ddays)):
     print(f"Title:{Item.Title}, Price:{Item.SellingStatus.CurrentPrice}, Status:{Item.SellingStatus.ListingStatus},ID:{Item.ItemID}\n")
     EndItemStr.append(Item.ItemID)
  elif(int(response.reply.ReturnedItemCountActual) > 0):
    if(response.reply.ItemArray.Item.SellingStatus.ListingStatus == "Active" and (currentDT - Item.ListingDetails.StartTime).days >= int(ddays)):
     print(f"Title:{Item.Title}, Price:{Item.SellingStatus.CurrentPrice}, Status:{Item.SellingStatus.ListingStatus},ID:{Item.ItemID}\n")
     EndItemStr.append(Item.ItemID)

  if(a_bool == False):
   return EndItemStr

def EndItems(Items):
 api = Connection(config_file='user.yaml', domain="api.ebay.com")

 temp_data = '{"EndItemRequestContainer":['
 #request =json.loads("{}")

 #res = Items.split(",")
 i = 1

 for iid in Items:
  temp_data = temp_data + '{"MessageID":' + "\""  + str(i)  + "\""  +  ',"EndingReason":"NotAvailable","ItemID": \"' + iid + '\" }'
  if(len(Items)>i):
   temp_data = temp_data + ','
  i = i + 1

 temp_data = temp_data + ']}'
 #print(temp_data)
 #request = eval(temp_data)
 request = json.loads(temp_data)
 print(request)
 response = api.execute('EndItems',request)

 print(f"{response.reply.Ack}")

def Menu():
 print("-------Multi User Management System------\n")
 print("1.      Login to the System\n")
 print("2.      Print Active Items\n")
 print("3.      Filter Active Items\n")
 print("4.      End Items\n")
 print("5.      Load User from File\n")
 print("6.      Exit Program\n")

if __name__ == '__main__':
 action = '0'
 EndItemStrs = []
 while (action != '6'):
  Menu()
  action=input()

  if(action == '1' ):
   SessionID = GetSessionID()
   print("Press any Key after Login Process\n")
   input()
   token = FetchToken(SessionID)
   print("Create User:\n")
   user = input()
   CreateUser(user,token)
  elif(action == '2'):
   if os.path.isfile('user.yaml'):
    GetActiveItems()
   else:
    print("Load User or Login")
  elif(action=='3'):
   if os.path.isfile('user.yaml'):
    print("Input Last Days Unsold:")
    day = input()
    EndItemStrs = GetActiveItemsbyDay(day)
    print(EndItemStrs)
   else:
    print("Load User or Login")
  elif(action=='4'):
   if(EndItemStrs):
    EndItems(EndItemStrs)
    EndItemStrs = []
   else:
    print("Filter Items First")
  elif(action == '5'):
   print("Load User:")
   user = input()
   LoadUser(user)
  else:
   print("Goodbye!")

