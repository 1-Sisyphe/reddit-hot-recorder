import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import random
from numpy import cumsum, mean
import hotcollect as hr
import json

with open('test.json') as jfile:
    data_collec = json.load(jfile)

date_list = [datetime.strptime(data['timestamp'],"%b %d %Y %H:%M:%S") for data in data_collec]

spot = date_list[10]

ups = [mean(data['ups']) for data in data_collec]
coms = [mean(data['coms']) for data in data_collec]

idx = date_list.index(spot)
fig,ax1 = plt.subplots(figsize=(15,2))

ax1.plot(date_list[:idx+1],ups[:idx+1],color='#375869')
ax1.plot(date_list[idx:],ups[idx:],color='#375869', alpha=0.1)
#ax1.plot([spot,spot],[0,max(test)],'k-', color ='grey')
ax1.set_ylabel('ups', color='#375869')
ax1.tick_params('y', colors='#375869')
ax1.yaxis.set_major_locator(mticker.MultipleLocator(5000))


ax2 = ax1.twinx()
ax2.plot(date_list[:idx+1],coms[:idx+1],color='#e1694e')
ax2.plot(date_list[idx:],coms[idx:],color='#e1694e', alpha=0.1)
ax2.set_ylabel('coms', color='#e1694e')
ax2.tick_params('y', colors='#e1694e')

ax2.xaxis.set_major_locator(mdates.HourLocator())
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%d %b"))

#plt.show()
plt.savefig('plots/1_test.png', bbox_inches='tight')
