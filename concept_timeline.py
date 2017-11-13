import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import random
from numpy import cumsum
base = datetime.today()
date_list = [base + timedelta(minutes=x) for x in range(0, 1000)]
spot = date_list[200]
test = [random.randint(-100,100) for n in range(len(date_list))]
test2 = [random.randint(-1000,1500) for n in range(len(date_list))]
test = cumsum(test)
test2 = cumsum(test2)
idx = date_list.index(spot)
fig,ax1 = plt.subplots(figsize=(15,2))

ax1.plot(date_list[:idx+1],test[:idx+1],color='b')
ax1.plot(date_list[idx:],test[idx:],color='b', alpha=0.1)
#ax1.plot([spot,spot],[0,max(test)],'k-', color ='grey')
ax1.set_ylabel('test', color='b')
ax1.tick_params('y', colors='b')


ax2 = ax1.twinx()
ax2.plot(date_list[:idx+1],test2[:idx+1],color='r')
ax2.plot(date_list[idx:],test2[idx:],color='r', alpha=0.1)
ax2.set_ylabel('test', color='r')
ax2.tick_params('y', colors='r')

ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M"))
ax2.xaxis.set_major_locator(mdates.HourLocator()) 

plt.show()
