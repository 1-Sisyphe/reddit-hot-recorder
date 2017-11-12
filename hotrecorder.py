import praw
import urllib.request
import matplotlib.pyplot as plt
import matplotlib.colors
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from datetime import datetime
from time import sleep
import json

with open('reddit_credentials') as f:
    client_id = f.readline().strip('\n')
    client_secret = f.readline().strip('\n')
    user_agent = f.readline().strip('\n')

def get_data(sub='france', maxposts=10):
    reddit = praw.Reddit(client_id= client_id,
                         client_secret= client_secret,
                         user_agent= user_agent)

    limit_read = maxposts + 5
    #read 5 more than asked, to account for the eventual stickied (rarely more than 2 on r/france...)
    submissions = reddit.subreddit(sub).hot(limit=limit_read)

    data = {
    'ups':[],
    'coms':[],
    'thumbs':[],
    'ages':[],
    'titles':[],
    'subs':[]
    }

    for submission in submissions:
        if not submission.stickied:
            data['ups'].append(submission.ups)
            data['coms'].append(submission.num_comments)
            data['titles'].append(submission.title)
            age = datetime.now() - datetime.fromtimestamp(submission.created_utc)
            age = divmod(age.total_seconds(), 60)[0] #age is min
            data['ages'].append(age)
            try :
                image_name = submission.name+'.jpg'
                image_url = submission.preview['images'][0]['resolutions'][0]['url']
                urllib.request.urlretrieve(image_url, 'thumbs/'+image_name)
            except AttributeError:
                image_name = '_nopreview.png' #some posts dont have previews. Use _nopreview.png as backup.
            data['thumbs'].append('thumbs/'+image_name)
            data['subs'].append(submission.subreddit_name_prefixed) #useful for r/all

    #keep only maxposts nbr of posts
    for d in data:
        data[d] = data[d][:maxposts]

    data['timestamp'] = datetime.now().strftime("%b %d %Y %H:%M:%S")
    data['sub'] = sub
    return(data)

def collect_data(sub='france',maxposts=10,interval=60,ticks=1,feedback=True,savefile=None):
    datalist = []
    for n in range(ticks):
        data = get_data(sub,maxposts)
        datalist.append(data)
        if feedback:
            print('{}/{} snapshot recorded on {}'.format(n+1,ticks,data['timestamp']))
        if savefile:
            with open(savefile, 'w') as f:
                json.dump(datalist, f)
        if n!=ticks-1: #dont sleep if it's the last extract
            sleep(interval)
    return datalist

def plot_chart(data, filename='0001.png',maxups=None,maxcoms=None,maxage=None,show=False):
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

def read_json(jsonfile):
    with open(jsonfile) as json_data:
        datalist = json.load(json_data)
    return datalist

def plot_all_charts(datalist,maxups=None, maxage=None,maxcoms=None):
    if not maxups:
        maxups = max([max(d['ups']) for d in datalist])
    if not maxcoms:
        maxcoms = max([max(d['coms']) for d in datalist])
    if not maxage:
        maxage = max([max(d['ages']) for d in datalist])
    n=1
    for data in datalist:
        filename = str(n).zfill(4)+'.png'
        plot_chart(data,filename=filename,maxups=maxups, maxage=maxage,maxcoms=maxcoms,show=False)
        n+=1

def offset_timestamp(data,delta_hours):
    '''
    Add (or remove if negative) delta_hours hours to data['timestamp'].
    Useful if your extract timestamp is not in the viewer excepted local time.
    '''
    from datetime import timedelta
    timestamp = datetime.strptime(data['timestamp'],"%b %d %Y %H:%M:%S")
    timestamp = timestamp + timedelta(hours=delta_hours)
    data['timestamp'] = timestamp.strftime("%b %d %Y %H:%M:%S")
    return data

if __name__ == '__main__':
    pass
