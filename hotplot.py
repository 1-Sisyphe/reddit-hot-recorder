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
        cmapage = []
        for age in ages:
            cmapage.append(cmap(norm(age)))
        return cmapage

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
    cmapage = make_colormap_age(maxage=maxage,ages=ages)
    maxposts = len(ups)
    rge = list(range(1,maxposts+1))

    #initiate plot
    plt.rcdefaults()
    plt.yticks(rge)
    fig = plt.figure(figsize = figsize)
    gs = gridspec.GridSpec(2, 3, width_ratios=[1,0.001,1], height_ratios=[1,5])
    #ax1,ax11,ax12 = plt.subplots(1, 3, sharey=True,gridspec_kw = {'width_ratios':[1,0.0001,1]})

    #top of the plot, where the timeline is plotted
    #if timeline:
    ax00 = plt.subplot(gs[0,:])

    #left side of the plot, where the karma is plotted
    ax10 = plt.subplot(gs[1,0])
    if maxups:
        ax10.set_xlim(0, maxups)
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

    #right side of the plot, where the comments are plotted
    ax12 = plt.subplot(gs[1,2], sharey=ax10)
    if maxcoms:
        ax12.set_xlim(0,maxcoms)
    ax12.barh(rge,coms, color = cmapage)
    ax12.set_xlabel('Comments')
    ax12.xaxis.set_label_position('bottom')
    ax12.xaxis.tick_bottom()
    ax12.xaxis.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.5)

    #center of the plot, for pictures
    ax11 = plt.subplot(gs[1,1], sharey=ax10)
    ax11.axis('off')
    for n in range(len(thumbs)):
        arr_img = crop_image(img=matplotlib.image.imread(thumbs[n]),imgheight=imgheight)
        imagebox = OffsetImage(arr_img, 0.7)
        ab = AnnotationBbox(imagebox, (0.5, n+1), frameon=False)
        ax11.add_artist(ab)

    plt.savefig('plots/'+filename, bbox_inches='tight')
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
