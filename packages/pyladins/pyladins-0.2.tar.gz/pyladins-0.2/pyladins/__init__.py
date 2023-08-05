
# coding: utf-8

# # Paladins API python implementation

# MIT License
# 
# Copyright (c) [2018] [Shubhankar Tiwari]
# 
# <!-- Place this tag where you want the button to render. -->
# <a class="github-button" href="https://github.com/shubhstiws" aria-label="Follow @shubhstiws on GitHub">Follow @shubhstiws</a>
# <!-- Place this tag in your head or just before your close body tag. -->
# <script async defer src="https://buttons.github.io/buttons.js"></script>
# 
# [Paladins API Documentation](https://docs.google.com/document/d/1OFS-3ocSx-1Rvg4afAnEHlT3917MAK_6eJTR6rzr-BM/edit) 

# #### Load libraries

# In[100]:


import requests
import time
import datetime
import json
#import calendar
import hashlib


# In[143]:


def jenos():
    print ('Step into the light!')


# #### Setting global variables

# In[101]:


devId=''
authKey=''
temp=''
pal=''
smite=''
loc_time = ''
session = ''


# #### Setup DevId and authentication Key

# In[102]:


def keys(d,a):
    global devId 
    devId = str(d)
    global authKey 
    authKey = str(a)


# In[107]:


#keys('****','**')


# #### Load URL

# In[103]:


def loadUrl(url):
    return json.loads(requests.get(url).content)


# #### Create Atlanta, Georgia timestamp

# In[104]:


def tsgen():
    #setting signature with local_timestamp
    local_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
    global loc_time 
    loc_time = local_time
    signature = str(devId)+str('createsession')+str(authKey)+str(local_time)
    signature = hashlib.md5(signature.encode('utf-8')).hexdigest()
    
    #attempting to create session with local_timestamp
    url = str(pal)+'/'+'createsessionJson'+'/'+str(devId)+'/'+str(signature)+'/'+str(local_time)
    sess = loadUrl(url)
    server_time = sess['timestamp']
    parsed_server_time = datetime.datetime.strptime(server_time, '%m/%d/%Y %I:%M:%S %p')
    local_time = datetime.datetime.fromtimestamp(time.time())
    
    #getting the wrong timestamp from server to correct our local timestamp
    if local_time > parsed_server_time: diff = local_time - (local_time - parsed_server_time)
    if local_time < parsed_server_time: diff = local_time + (parsed_server_time - local_time)
    else: diff = local_time
    return diff.strftime('%Y%m%d%H%M%S')


# #### Create Signature

# In[105]:


def signature_id(method):
    signature = str(devId)+str(method)+str(authKey)+str(temp)
    signature = hashlib.md5(signature.encode('utf-8')).hexdigest()
    return signature


# #### Create session

# In[106]:


def session_id(urlPrefix):
    
    signature = signature_id('createsession')

    url = str(urlPrefix)+'/'+'createsessionJson'+'/'+str(devId)+'/'+str(signature)+'/'+str(temp)
    sess = loadUrl(url)['session_id']
    return sess


# #### Setup or Refresh API, session

# In[108]:


def setup():
    global pal
    pal ='http://api.paladins.com/paladinsapi.svc'
    global smite 
    smite = 'http://api.smitegame.com/smiteapi.svc'
    global temp 
    temp = tsgen()
    global session
    session = session_id(pal)


# In[120]:


#setup()


# #### Check if session valid, create new if not

# In[109]:


def check():
    diff = datetime.datetime.fromtimestamp(time.time())-datetime.datetime.strptime(loc_time,'%Y%m%d%H%M%S')
    if diff.seconds > 899:
        setup()


# #### Generate URL

# In[110]:


def genUrl(method):
    return pal+'/'+str(method)+'json'+'/'+devId+'/'+signature_id(method)+'/'+session+'/'+temp


# ### If you get timestamp exception manually run <font color='red'> setup() </font>

# ### APIs Connectivity:

# #### <font color='red'>Python ping</font>

# In[144]:


def ping():
    check()
    method = 'pingjson'
    url = pal+'/'+method
    return loadUrl(url)


# In[145]:


#ping()


# #### <font color='red'>Python testsession</font>

# In[130]:


def testsession():
    check()
    url=genUrl('testsession')
    return loadUrl(url)


# In[125]:


#testsession()


# #### <font color='red'>Python getplayer()</font>

# In[131]:


def getplayer(ign):
    check()
    url = genUrl('getplayer')+'/'+str(ign)
    return loadUrl(url)


# #### <font color='red'> Python gethirezserverstatus() </font>

# In[132]:


def gethirezserverstatus():
    check()
    url=genUrl('gethirezserverstatus')
    return loadUrl(url)


# In[133]:


#gethirezserverstatus()


# ### APIs

# #### <font color = 'red' > Python getdataused() </font>

# In[134]:


def getdataused():
    check()
    url=genUrl('getdataused')
    return loadUrl(url)


# In[135]:


#getdataused()


# #### <font color = 'red' > Python getdemodetails() </font>

# In[136]:


def getdemodetails(matchid):
    check()
    url=genUrl('getdemodetails')+'/'+str(matchid)
    return loadUrl(url)


# #### <font color = 'red' > Python getesportsproleaguedetails() </font> 

# In[137]:


def getesportsproleaguedetails():
    check()
    url=genUrl('getesportsproleaguedetails')
    return loadUrl(url)


# #### <font color = 'red' > Python getfriends() </font> 

# In[138]:


def getfriends(ign):
    check()
    url=genUrl('getfriends')+'/'+str(ign)
    return loadUrl(url)


# #### <font color = 'red' > Python getchampionranks() </font> 

# In[139]:


def getchampionranks(ign):
    check()
    url=genUrl('getchampionranks')+'/'+str(ign)
    return loadUrl(url)


# #### <font color = 'red' > Python getmatchhistory() </font> 

# In[140]:


def getmatchhistory(ign):
    check()
    url=genUrl('getmatchhistory')+'/'+str(ign)
    return loadUrl(url)


# #### <font color = 'red' > Python getplayerachievements() </font> 

# In[141]:


def getplayerachievements(ign):
    check()
    id = getplayer(ign)[0]['Id']
    url=genUrl('getplayerachievements')+'/'+str(id)
    return loadUrl(url)

