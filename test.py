import hotcollect
import hotplot

if False:
    data_collec = hotcollect.read_json('data_collec.json')
    for data in data_collec:
        data = hotcollect.offset_timestamp(data, -7)

    hotplot.plot_all_charts(data_collec)

if True:
    data_collec = hotcollect.collect_data(sub='all',maxposts=10,interval=10,ticks=2,feedback=True)
    for data in data_collec: data = hotcollect.offset_timestamp(data, -7)
    hotplot.plot_collec(data_collec)
