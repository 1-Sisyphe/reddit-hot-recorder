import hotcollect
import hotplot
import json

if True:
    with open('test.json') as j:
        data_collec = json.load(j)
    for data in data_collec:
        data = hotcollect.offset_timestamp(data, -7)
    hotplot.plot_collec(data_collec)

if False:
    data_collec = hotcollect.collect_data(sub='all',maxposts=10,interval_sec=20,duration_min=1,feedback=True,savefile='test.json')
    for data in data_collec:
        data = hotcollect.offset_timestamp(data, -7)
    hotplot.plot_collec(data_collec)
