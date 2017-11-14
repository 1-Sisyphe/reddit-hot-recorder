import matplotlib.pyplot as plt
import matplotlib.colors
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg

def plot_chart(data, filename='plot.png',maxups=None,maxcoms=None,maxage=None,show=False):
    def format_title(title,post_sub,analysed_sub,limit_title_len):
        if post_sub != 'r/'+analysed_sub:
            f_title = post_sub + ' - ' + title
        else:
            f_title = title
        if len(f_title) > limit_title_len:
            f_title = f_title[:limit_title_len-3]+'...'
        return f_title

    def crop_image(img, imgheight): #cut the thumbnail in the middle of the height
        topcut = round(len(img)/2) - round(imgheight/2)
        bottomcut = round(len(img)/2) + round(imgheight/2)
        img = img[topcut:bottomcut, :, :]
        return img

    def make_colormap_age(maxage,ages,cmapname='hot'):
        cmap = plt.cm.get_cmap(cmapname)
        norm = matplotlib.colors.Normalize(vmin=0, vmax=maxage)
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
    maxage += 60 #increase maxage to compensate for some colormap giving white on max value
    cmapage = make_colormap_age(maxage=maxage,ages=ages)
    maxposts = len(ups)
    rge = list(range(1,maxposts+1))

    #initiate plot
    plt.rcdefaults()
    f, (ax1,ax2,ax3) = plt.subplots(1, 3, sharey=True, figsize = figsize, gridspec_kw = {'width_ratios':[1,0.0001,1]})

    #left side of the plot, where the karma is plotted
    if maxups:
        ax1.set_xlim(0, maxups)
    ax1.barh(rge,ups, color = cmapage)
    ax1.invert_xaxis()
    ax1.invert_yaxis()
    ax1.set_xlabel('Karma')
    ax1.xaxis.set_label_position('top')
    ax1.xaxis.tick_top()
    ax1.xaxis.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
    for n in range(len(titles)):
        title = format_title(titles[n],subs[n],data['sub'],limit_title_len)
        title_pos = ax1.get_xlim()[0]
        ax1.text(title_pos,n+1,' '+title)

    #right side of the plot, where the comments are plotted
    if maxcoms:
        ax3.set_xlim(0,maxcoms)
    ax3.barh(rge,coms, color = cmapage)
    ax3.set_xlabel('Comments')
    ax3.xaxis.set_label_position('top')
    ax3.xaxis.tick_top()
    ax3.xaxis.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.5)

    #center of the plot, for pictures
    ax2.axis('off')
    for n in range(len(thumbs)):
        arr_img = crop_image(img=mpimg.imread(thumbs[n]),imgheight=imgheight)
        imagebox = OffsetImage(arr_img, 0.7)
        ab = AnnotationBbox(imagebox, (0.5, n+1), frameon=False)
        ax2.add_artist(ab)

    charttitle = 'r/{} - {}'.format(data['sub'],data['timestamp'])
    plt.suptitle(charttitle)
    plt.yticks(rge)

    plt.savefig('plots/'+filename, bbox_inches='tight')
    if show: plt.show()
    plt.close()
    return

def plot_collec(data_collec,maxups=None, maxage=None,maxcoms=None):
    if not maxups:
        maxups = max([max(d['ups']) for d in data_collec])
    if not maxcoms:
        maxcoms = max([max(d['coms']) for d in data_collec])
    if not maxage:
        maxage = max([max(d['ages']) for d in data_collec])
    nbr_zfill = len(str(len(data_collec)))
    n=1
    for data in data_collec:
        filename = str(n).zfill(nbr_zfill)+'.png'
        plot_chart(data,filename=filename,maxups=maxups, maxage=maxage,maxcoms=maxcoms,show=False)
        n+=1
