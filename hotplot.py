import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.image
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from numpy import mean
from datetime import datetime

def plot_chart(data, filename='plot.png',maxups=None,maxcoms=None,maxage=None,show=False, timeline = None):
    '''
    Where the plotting magic happens.
    plot_chart works on a data point. It can be used directly after get_data.
    After collect_data, plot_collec should be preferred, to correctly handle the max... args.
    If max... args are None, plot_chart will freely adapt the chart and color.

    timeline contains specific data from plot_collec and is required to plot the upper timeline.
    Plotting the timeline requires a full knowledge of the data_collec and therefore
    doesnt work on a single data.
    '''
    def format_title(title,post_sub,analysed_sub,limit_title_len):
        '''reformat the title if too long and add the sub name if different from
        the analysed sub'''
        if post_sub != 'r/'+analysed_sub:
            f_title = post_sub + ' - ' + title
        else:
            f_title = title
        if len(f_title) > limit_title_len:
            f_title = f_title[:limit_title_len-3]+'...'
        return f_title

    def crop_image(img, imgheight):
        '''cut the thumbnail in the middle of the height'''
        topcut = round(len(img)/2) - round(imgheight/2)
        bottomcut = round(len(img)/2) + round(imgheight/2)
        img = img[topcut:bottomcut, :, :]
        return img

    def make_colormap_age(maxage,ages,cmapname='hot'):
        '''prepare the colormap'''
        cmap = plt.cm.get_cmap(cmapname)
        norm = matplotlib.colors.Normalize(vmin=0, vmax=1.05*maxage)
        #avoid that vmax matches the max of the color map, otherwise
        #it could be white with certain cmaps
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cmapage = []
        for age in ages:
            cmapage.append(cmap(norm(age)))
        return cmapage, sm

    imgheight = 50 #crop images at 50px high (108px width by default)
    limit_title_len = 70 #max nbr of characters in displayed title
    figsize = (16,9)
    ups = data['ups']
    coms = data['coms']
    thumbs = data['thumbs']
    ages = data['ages']
    titles = data['titles']
    subs = data['subs']
    if not maxage:
        maxage = max(ages)
    cmapage, sm = make_colormap_age(maxage=maxage,ages=ages)
    maxposts = len(ups)
    rge = list(range(1,maxposts+1))

    #initiate plot
    plt.rcdefaults()
    matplotlib.rcParams.update({'font.size': 11})
    plt.yticks(rge)
    fig = plt.figure(figsize = figsize)
    gs = gridspec.GridSpec(2, 4, width_ratios=[1,0.05,1,0.05], height_ratios=[1,5])
    #ax1,ax11,ax12 = plt.subplots(1, 3, sharey=True,gridspec_kw = {'width_ratios':[1,0.0001,1]})

    #top of the plot, where the timeline is plotted
    #if timeline:
    color_ups = '#549ED6'
    color_coms = '#33cc33'
    ax00 = plt.subplot(gs[0,:])
    tl_ups = timeline['ups']
    tl_coms = timeline['coms']
    tl_dates = timeline['dates']
    curr_date = datetime.strptime(data['timestamp'],"%b %d %Y %H:%M:%S")
    idx_curr_date = tl_dates.index(curr_date)
    ax00.plot(tl_dates[:idx_curr_date+1],tl_ups[:idx_curr_date+1],color=color_ups)
    ax00.plot(tl_dates[idx_curr_date:],tl_ups[idx_curr_date:],color=color_ups, alpha=0.1)
    #ax1.plot([spot,spot],[0,max(test)],'k-', color ='grey')
    ax00.set_ylabel('mean(Karma)', color=color_ups)
    ax00.tick_params('y', colors=color_ups)
    #ax00.yaxis.set_major_locator(mticker.MultipleLocator(5000))
    ax00.xaxis.set_major_locator(mdates.HourLocator())
    ax00.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M\n%d %b"))
    ax01 = ax00.twinx()
    ax01.plot(tl_dates[:idx_curr_date+1],tl_coms[:idx_curr_date+1],color=color_coms)
    ax01.plot(tl_dates[idx_curr_date:],tl_coms[idx_curr_date:],color=color_coms, alpha=0.1)
    ax01.set_ylabel('mean(comments)', color=color_coms)
    ax01.tick_params('y', colors=color_coms)
    #ax01.yaxis.set_major_locator(mticker.MultipleLocator(100))
    ax01.xaxis.set_major_locator(mdates.HourLocator())
    ax01.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    #left side of the plot, where the karma is plotted
    ax10 = plt.subplot(gs[1,0])
    if maxups:
        ax10.set_xlim(0, maxups)
    ax10.yaxis.set_major_locator(mticker.MultipleLocator(base=1.0))
    ax10.barh(rge,ups, color = cmapage)
    ax10.invert_xaxis()
    ax10.invert_yaxis()
    ax10.set_xlabel('Karma')
    ax10.xaxis.set_label_position('bottom')
    ax10.xaxis.tick_bottom()
    ax10.xaxis.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
    for n in range(len(titles)):
        title = format_title(titles[n],subs[n],data['sub'],limit_title_len)
        title_pos = ax10.get_xlim()[0]
        ax10.text(title_pos,n+1,' '+title)

    #center of the plot, for pictures
    ax11 = plt.subplot(gs[1,1], sharey=ax10)
    ax11.axis('off')
    for n in range(len(thumbs)):
        arr_img = crop_image(img=matplotlib.image.imread(thumbs[n]),imgheight=imgheight)
        imagebox = OffsetImage(arr_img, 0.7)
        ab = AnnotationBbox(imagebox, (0.5, n+1), frameon=False)
        ax11.add_artist(ab)

    #right side of the plot, where the comments are plotted
    ax12 = plt.subplot(gs[1,2], sharey=ax10)
    if maxcoms:
        ax12.set_xlim(0,maxcoms)
    ax12.barh(rge,coms, color = cmapage)
    ax12.set_xlabel('Comments')
    plt.setp(ax12.get_yticklabels(), visible=False)
    ax12.xaxis.set_label_position('bottom')
    ax12.xaxis.tick_bottom()
    ax12.xaxis.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.5)

    ax13 = plt.subplot(gs[1,3])
    cbar = plt.colorbar(sm, cax = ax13)
    cbar.set_label('age in minutes')
    plt.tight_layout()
    #plt.savefig('plots/'+filename, bbox_inches='tight')
    plt.savefig('plots/'+filename)
    if show: plt.show()
    plt.close()
    return

def plot_collec(data_collec,maxups=None, maxage=None,maxcoms=None):
    '''
    Prepares the max... args to make sure that the highest value of the axis
    and the max color of the color map covers all the data_collec.
    Prepares the timeline_data required for plotting the timeline.
    Then, launch the loop to plot each data point.
    '''
    if not maxups:
        maxups = max([max(d['ups']) for d in data_collec])
    if not maxcoms:
        maxcoms = max([max(d['coms']) for d in data_collec])
    if not maxage:
        maxage = max([max(d['ages']) for d in data_collec])
    nbr_zfill = len(str(len(data_collec)))

    timeline = {
       'ups':[mean(data['ups']) for data in data_collec],
       'coms':[mean(data['coms']) for data in data_collec],
       'dates':[datetime.strptime(data['timestamp'],"%b %d %Y %H:%M:%S") for data in data_collec]
       }

    n=1
    for data in data_collec:
        filename = str(n).zfill(nbr_zfill)+'.png'
        plot_chart(data,filename=filename,maxups=maxups, maxage=maxage,maxcoms=maxcoms,show=False, timeline = timeline)
        n+=1

if __name__ == '__main__':
    import json
    import hotcollect
    if True:
        with open('test.json') as j:
            data_collec = json.load(j)
        for data in data_collec:
            data = hotcollect.offset_timestamp(data, -7)
        plot_collec(data_collec)
