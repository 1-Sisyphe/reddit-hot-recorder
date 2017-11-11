import hotrecorder as hr
datalist = hr.collect_data(sub='france',interval=10,ticks=1,maxposts=10)

for n in range(len(datalist)):
    hr.make_chart(datalist[n],increment=n+1,maxage=12,show=True)