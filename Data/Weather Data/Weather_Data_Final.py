
# coding: utf-8

# In[2]:


# setup library imports
import io, time, json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
from datetime import timedelta


# In[37]:


def to_datetime(x):
    time_converted = datetime.strptime(x, '%B %d %Y %I:%M %p')
    return time_converted
def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))


# In[38]:


def one_day(url):

    day = requests.get(url)

    soup = BeautifulSoup(day.text, 'html.parser')

    a=soup.find_all('div', attrs={'class':'high-res'})

    date = soup.find_all('h2', attrs={'class':"history-date"})
    date = date[0]
    date = date.text

    a=a[0]
    rows=[]
    b = a.find_all('tr')

    for i in range(1,len(b)):
        c = b[i].find_all('td')
        rows.append(c)
    e = b[0].find_all('th')
    cols=[]
    for header in e:
        cols.append(header.text)

    weather = pd.DataFrame(columns = ['Time', 'Temp (F)', 'Humidity', 'Wind Speed', 'Condition'])

    data = []
    for k in rows:
        row={}
        time = k[0].text
        time = date+' '+time
        time = re.sub(r'.*day,', '', time)
        time = time.replace(',','')
        time = time[1:]
        try:
            temp = k[1].find('span', attrs={'class':'wx-value'}).text
        except:
            temp = None
        if len(cols)==13:    
            hum = k[4].text
            hum = hum[:-1]
            try:
                wind_spd = k[8].find('span', attrs={'class':'wx-value'}).text
            except:
                wind_spd = k[8].text
            
            cond = k[12].text
        if len(cols)==12:
            hum = k[3].text
            hum = hum[:-1]
            try:
                wind_spd = k[7].find('span', attrs={'class':'wx-value'}).text
            except:
                wind_spd = k[7].text

            cond = k[11].text
        row["Time"]=time
        row['Temp (F)']=temp
        row['Humidity']=hum
        row['Wind Speed']=wind_spd
        row["Condition"]=cond
        data.append(row)

    weather = weather.append(data,ignore_index=True)
    try:
        weather['Temp (F)'] = weather['Temp (F)'].astype('float64')
    except:
        pass
    try:
        weather['Humidity'] = weather['Humidity'].astype('float64')
    except:
        pass
    weather['Time'] = weather['Time'].apply(lambda x: hour_rounder((pd.to_datetime(to_datetime(x)))))
    weather = weather.replace(['N/A','\n -\n'], 50.0)
    weather1 = weather.copy()
    #weather1 = weather1.replace(['N/A','\n  -\n'], 0.0)
    weather1['Humidity'] = weather1['Humidity'].astype('float64')
    weather1 = weather1.set_index('Time', drop=True)
    weather1 = weather1.resample('H').mean()
    weather1 = weather1.reset_index()

    n = soup.find_all('div', attrs={'class':'next-link'})
    n=n[0]
    nxt_date = 'https://www.wunderground.com'+n.find('a').get('href')
    
    return weather, weather1, nxt_date


# In[105]:


result = one_day('https://www.wunderground.com/history/airport/KATT/2016/1/9/DailyHistory.html?req_city=&req_state=&req_statename=&reqdb.zip=&reqdb.magic=&reqdb.wmo=')
result


# In[43]:


def all_days(url, no_of_days):
    list1 = []
    list2= []
    result = one_day(url)
    list1.append(result[0])
    list2.append(result[1])
    for i in range(no_of_days -1):
        result = one_day(result[2])
        list1.append(result[0])
        list2.append(result[1])
        print(i+1, 'th day is done')
    weather1 = pd.concat(list1).reset_index(drop=True)
    weather2 = pd.concat(list2).reset_index(drop=True)
    return weather1, weather2
one, two = all_days('https://www.wunderground.com/history/airport/KATT/2016/2/1/DailyHistory.html?req_city=&req_state=&req_statename=&reqdb.zip=&reqdb.magic=&reqdb.wmo=',9)


# In[187]:


list1, list2 = all_day('https://www.wunderground.com/history/airport/KATT/2016/2/1/DailyHistory.html?req_city=&req_state=&req_statename=&reqdb.zip=&reqdb.magic=&reqdb.wmo=',29)


# In[188]:


list2


# In[189]:


#list2.to_csv('Dec 2017.csv')
list1.to_csv('Feb 2016_all.csv')


# In[227]:


months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
years = [2016, 2017]
all_years_1 = []
all_years_2 = []
for month in months:
    for year in years:
        one = pd.read_csv(str(month)+' '+str(year)+'.csv', sep=',', delimiter=None, header='infer')
        two = pd.read_csv(str(month)+' '+str(year)+'_all.csv', sep=',', delimiter=None, header='infer')
        all_years_1.append(one)
        all_years_2.append(two)
Weather_data_one = pd.concat(all_years_1).reset_index()
#Weather_data_one = Weather_data_one.drop(['index', 'Unnamed: 0'], axis=1)
Weather_data_two = pd.concat(all_years_2).reset_index()
#Weather_data_two = Weather_data_two.drop(['index', 'Unnamed: 0'], axis=1)


# In[30]:


#Weather_data_one['Time'] = Weather_data_one['Time'].apply(lambda x: pd.to_datetime(x))
# Weather_data_one = Weather_data_one.drop(['index', 'Unnamed: 0'], axis=1)
# Weather_data_two = Weather_data_two.drop(['index', 'Unnamed: 0'], axis=1)
Weather_data_one.to_csv('Weather data.csv')
Weather_data_two.to_csv('Weather data All.csv')


# In[31]:


X = pd.read_csv('Weather data All.csv').drop('Unnamed: 0', axis=1)


# In[32]:


y = X.Condition.unique().tolist()
y = sorted(y)
X['Condition'] = X['Condition'].apply(lambda x: y.index(x))
# y2=[]
# for i in range(len(X)):
    
#     try:
#         X['Wind Speed'][i]=float(X['Wind Speed'][i])
#     except:
#         X['Wind Speed'][i]=X['Wind Speed'][i]
# for x in X['Wind Speed']:
#     if type(x)==str:
#         y2.append(x)
# y2
def t_or_e(x):
    try:
        return float(x)
    except:
        if x=='Calm':
            return 3.0
        else:
            return 4.5
X['Wind Speed'] = X['Wind Speed'].apply(lambda x: t_or_e(x))


# In[33]:


X['Time'] = X['Time'].apply(lambda x: pd.to_datetime(x))


# In[34]:


X = X.set_index('Time', drop=True).resample('H').mean().reset_index()


# In[35]:


X['Humidity'] = X['Humidity'].apply(lambda x: x/100)
X.to_csv('Final Data.csv')

