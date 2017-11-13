import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import random
base = datetime.today()
date_list = [base + timedelta(hours=x) for x in range(0, 24)]
spot = date_list[5]
test = random.sample(range(1, 100), len(date_list))
test2 = random.sample(range(1, 100), len(date_list))
idx = date_list.index(spot)
fig = plt.figure(figsize=(10,2))
ax = fig.add_subplot(111)
ax.plot(date_list[:idx+1],test[:idx+1],color='b')
ax.plot(date_list[idx:],test[idx:],color='b', alpha=0.2)
ax.plot(date_list[:idx+1],test2[:idx+1],color='r')
ax.plot(date_list[idx:],test2[idx:],color='r', alpha=0.2)
ax.plot([spot,spot],[0,max(test)],'k-', color ='grey')
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m\n%H:%M"))
plt.show()
