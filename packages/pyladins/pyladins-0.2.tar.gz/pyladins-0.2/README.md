# Paladins

![](https://github.com/shubhstiws/paladins/blob/master/logo.png)

## Python implementation of the Paladins and Smite APIs

I have created python equivalent of functions offered by Hi Rez paladins and smite API. GitHub cannot render the jupyter notebook correctly, please make sure to read the python file if facing any errors

## How to use

Make sure you have all these functions installed 

```python
import requests #for url requests
import time #for timestamps
import datetime #for parsing timestamps
import json #for parsing json data
import hashlib #for calculating MD5 hash
```

Check if the package installation worked correctly by calling the function 

```python 
jenos()
```

If you get the output 

```python 
'Step into the light!'
``` 

the installation is good!

Call the function keys(DevId, AuthenticationKey) and pass your devid and authentication keys which can be obtained by submitting a request to HiRez Dev team. This sets up the keys in the global variables to be used by other functions

For now I have ensured that you do not have to take care of your current timezone while making API calls, but if you still get timestamp errors then check the timestamp of the server and adjust your timestamp accordingly. I also create a new session automatically if the current session expires but have not tested this throughly

## Paladins functions

All functions are not available, only a handful of the most useful functions are available, I will be adding all of them soon.

```python
ping() #check connection
testsession() #get session information
gethirezserverstatus() #check server status
getdataused() #get stats on current session usage
getfriends(ign) #get all friends of a in game paladins name
```

## Smite functions

Firstly the `urlPrefix` has to be changed to the smite API link. Secondly the smite functions have to be referenced from the documentation and then used. Same session can be used to access those functions. I will be adding them later and an option to switch between all of them soon 

## Next steps:

* [x] Remove time zone hardcoding
* [x] Automate new session creation when current session expires
* [ ] Complete code for all functions
* [ ] Write function for choosing Xbox, PS4 and PC
* [ ] Extract and build database for top players and teams
* [ ] Parse data into csv to be used in R for analysis and visualization

## Featured Art

![](https://github.com/shubhstiws/paladins/blob/master/jenos.jpg)
