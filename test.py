import hotrecorder as hr

if False:
    datalist = hr.read_json('datalist.json')
    for data in datalist:
        data = hr.offset_timestamp(data, -7)

    hr.plot_all_charts(datalist)

if True:
    datalist = hr.collect_data(sub='all',maxposts=10,interval=10,ticks=50,feedback=True)
    for data in datalist: data = hr.offset_timestamp(data, -7)
    hr.plot_all_charts(datalist)
