import hotcollect
import hotplot
import json

data_collec = hotcollect.collect_data(sub='all',maxposts=10,interval_sec=30,duration_min=5,feedback=True,savefile='example.json')

with open('example.json') as j:
    data_collec = json.load(j)
    for data in data_collec:
        data = hotcollect.offset_timestamp(data, -7)

hotplot.plot_collec(data_collec)
