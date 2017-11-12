import hotrecorder as hr
datalist = hr.read_json('datalist.json')

maxups = max([max(d['ups']) for d in datalist])
maxcoms = max([max(d['coms']) for d in datalist])
maxage = max([max(d['ages']) for d in datalist])
n=1
for data in datalist:
    hr.make_chart(data,show=False,increment=n,maxups=maxups, maxage=maxage,maxcoms=maxcoms)
    n+=1
