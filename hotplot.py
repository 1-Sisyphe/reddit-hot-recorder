import os
import matplotlib
#Allow headless use
if os.environ.get('DISPLAY') is None:
    print("Falling back to Agg engine")
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.image
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from numpy import mean
from datetime import datetime

def plot_data(data, filename='plot.png',maxups=None,maxcoms=None,maxage=None,show=False, timeline = None):
    '''
    Where the plotting magic happens.
    plot_data works on a data point. It can be used directly after get_data.
    After collect_data, plot_collec should be preferred, to correctly handle the max... args.
    If max... args are None, plot_data will freely adapt the chart and color.

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

    def make_colormap_age(maxage,ages,cmapname='GnBu'):
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

    def rm_frames(ax):
        '''shortcut to remove all frames of a subplot'''
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

    imgheight = 48 #crop images at 50px high (108px width by default)
    limit_title_len = 60 #max nbr of characters in displayed title
    figsize = (18,10)
    ups = data['ups']
    coms = data['coms']
    thumbs = data['thumbs']
    ages = [age/60 for age in data['ages']]
    titles = data['titles']
    subs = data['subs']
    if not maxage:
        maxage = max(ages)
    maxage = maxage/60
    cmapage, sm = make_colormap_age(maxage=maxage,ages=ages)
    maxposts = len(ups)
    list_yticks = list(range(1,maxposts+1))

    #initiate plot
    plt.rcdefaults()
    matplotlib.rcParams.update({'font.size': 15})
    plt.yticks(list_yticks)
    fig = plt.figure(figsize = figsize)
    gs = gridspec.GridSpec(2, 5, width_ratios=[0.2,1.5,0.3,1.5,0.05], height_ratios=[1,5])
    #Grid is 2 rows * 4 columns
    #Top row is for the timeline
    #Bottom row is for karma bars / thumbnails / comments bars / colormap legend

    #top of the plot, where the timeline is plotted
    if timeline:
        color_ups = '#549ED6'
        color_coms = '#33cc33'
        ax_tl = plt.subplot(gs[0,1:5])
        rm_frames(ax_tl)
        ax_tl.spines['bottom'].set_visible(True)
        tl_ups = timeline['ups']
        tl_coms = timeline['coms']
        tl_ages = [age/60 for age in timeline['ages']]
        tl_dates = timeline['dates']
        curr_date = datetime.strptime(data['timestamp'],"%b %d %Y %H:%M:%S")
        idx_curr_date = tl_dates.index(curr_date)
        ax_tl.plot(tl_dates[:idx_curr_date+1],tl_ups[:idx_curr_date+1],color=color_ups)
        ax_tl.plot(tl_dates[idx_curr_date:],tl_ups[idx_curr_date:],color=color_ups, alpha=0.1)
        ax_tl.set_ylabel('mean(Karma)', color=color_ups)
        ax_tl.tick_params('y', colors=color_ups)
        ax_tl.yaxis.set_major_locator(mticker.LinearLocator(3))
        ax_tl.yaxis.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
        ax_tltwin = ax_tl.twinx()
        rm_frames(ax_tltwin)
        ax_tltwin.plot(tl_dates[:idx_curr_date+1],tl_ages[:idx_curr_date+1],color=color_coms)
        ax_tltwin.plot(tl_dates[idx_curr_date:],tl_ages[idx_curr_date:],color=color_coms, alpha=0.1)
        ax_tltwin.set_ylabel('mean(ages in hour)', color=color_coms)
        ax_tltwin.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.1f'))
        ax_tltwin.tick_params('y', colors=color_coms)
        ax_tltwin.yaxis.set_major_locator(mticker.LinearLocator(3))
        #ax_tltwin.xaxis.set_major_locator(mdates.HourLocator())
        ax_tltwin.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    else: #if no timeline, when plot_data is used on a single data point, fill
          #the empty space with a title.
          #TODO: improve that part to make better use of the space...
        ax_tl = plt.subplot(gs[0,1:])
        ax_tl.axis('off')
        text_title = 'r/' + data['sub'] + ' - ' + data['timestamp']
        ax_tl.text(0.4,0.5,text_title,fontsize=16, fontweight='bold')

    #left side of the plot, where the karma is plotted
    ax_ups = plt.subplot(gs[1,:2])
    rm_frames(ax_ups)
    if maxups:
        ax_ups.set_xlim(0, maxups)
    ax_ups.barh(list_yticks,ups, color = cmapage)
    ax_ups.invert_xaxis()
    ax_ups.invert_yaxis()
    ax_ups.set_xlabel('Karma')
    ax_ups.xaxis.set_label_position('bottom')
    ax_ups.xaxis.tick_bottom()
    ax_ups.set_yticks([])
    plt.setp(ax_ups.get_yticklabels(), visible=False)
    ax_ups.xaxis.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
    for n in range(len(titles)):
        title = format_title(titles[n],subs[n],data['sub'],limit_title_len)
        title_pos = ax_ups.get_xlim()[0]
        ax_ups.text(title_pos,n+1,' '+title, verticalalignment='center')

    #center of the plot, for pictures
    ax_thumbs = plt.subplot(gs[1,2], sharey=ax_ups)
    ax_thumbs.set_yticklabels([])
    ax_thumbs.axis('off')
    for n in range(len(thumbs)):
        arr_img = crop_image(img=matplotlib.image.imread(thumbs[n]),imgheight=imgheight)
        imagebox = OffsetImage(arr_img, 0.7)
        ab = AnnotationBbox(imagebox, (0.5, n+1), frameon=False)
        ax_thumbs.add_artist(ab)

    #right side of the plot, where the comments are plotted
    ax_coms = plt.subplot(gs[1,3], sharey=ax_ups)
    rm_frames(ax_coms)
    if maxcoms:
        ax_coms.set_xlim(0,maxcoms)
    ax_coms.barh(list_yticks,coms, color = cmapage)
    ax_coms.set_xlabel('Comments')
    plt.setp(ax_coms.get_yticklabels(), visible=False)
    ax_coms.xaxis.set_label_position('bottom')
    ax_coms.xaxis.tick_bottom()
    ax_coms.xaxis.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.5)

    #colormap legend
    ax_cbar = plt.subplot(gs[1,4])
    cbar = plt.colorbar(sm, cax = ax_cbar)
    cbar.set_label('age in hours')
    plt.subplots_adjust(wspace=0.05, hspace=0.2)
    #Check existence of plots directory
    if not os.path.exists("plots/"):
        os.makedirs("plots/")
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
       'dates':[datetime.strptime(data['timestamp'],"%b %d %Y %H:%M:%S") for data in data_collec],
       'ages': [mean(data['ages']) for data in data_collec]
       }

    n=1
    for data in data_collec:
        filename = str(n).zfill(nbr_zfill)+'.png'
        plot_data(data,filename=filename,maxups=maxups, maxage=maxage,maxcoms=maxcoms,show=False, timeline = timeline)
        n+=1

if __name__ == '__main__':
    pass
