import praw
import matplotlib.pyplot as plt
import matplotlib
import urllib.request
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
import matplotlib.image as mpimg
from datetime import datetime
from time import sleep

with open('reddit_credentials') as f:
    client_id = f.readline().strip('\n')
    client_secret = f.readline().strip('\n')
    user_agent = f.readline().strip('\n')

def get_data(sub='france', maxposts=10):
    limit_read = maxposts + 5
    #read 5 more than asked, to account for the eventual stickied (rarely more than 2 on r/france...)

    reddit = praw.Reddit(client_id= client_id,
                         client_secret= client_secret,
                         user_agent= user_agent)

    submissions = reddit.subreddit('france').hot(limit=limit_read)
    ups=[]
    coms=[]
    thumbs=[]
    ages = []
    titles = []
    for submission in submissions:
        if not submission.stickied:
            ups.append(submission.ups)
            coms.append(submission.num_comments)
            title = submission.title
            if len(title)>30:
                title = title[:27]+'...'
            titles.append(title)
            age = datetime.now() - datetime.fromtimestamp(submission.created_utc)
            age = divmod(age.total_seconds(), 60*60)[0]
            ages.append(age)
            try :
                image_name = submission.name+'.jpg'
                image_url = submission.preview['images'][0]['resolutions'][0]['url']
                urllib.request.urlretrieve(image_url, 'thumbs/'+image_name)
            except AttributeError:
                image_name = '_nopreview.png' #some posts dont have previews. Use _nopreview.png as backup.
            thumbs.append('thumbs/'+image_name)

    data = {
    'ups':ups,
    'coms':coms,
    'thumbs':thumbs,
    'ages':ages,
    'titles':titles
    }

    for d in data:
        data[d] = data[d][:maxposts]
    return(data)

def collect_data(sub='france',maxposts=10,interval=60,ticks=1,feedback=True):
    datalist = []
    prev_sum_ups = 0
    prev_sum_coms = 0

    for n in range(ticks):
        tstp = datetime.now()
        data = get_data(sub,maxposts)

        if n==0:
            data['delta_ups'] = 0
            data['delta_coms'] = 0
        else:
            data['delta_ups'] = sum(data['ups']) - prev_sum_ups
            data['delta_coms'] = sum(data['coms']) - prev_sum_coms
        prev_sum_ups = sum(data['ups'])
        prev_sum_coms = sum(data['coms'])

        data['timestamp'] = tstp
        datalist.append(data)
        if feedback:
            print('{}/{} snapshot recorded on {}'.format(n+1,ticks,tstp.strftime('%c')))
        if n!=ticks-1:
            sleep(interval)
    return datalist


def make_chart(data, increment=1,show=False):
    now = datetime.now()
    ups = data['ups']
    coms = data['coms']
    thumbs = data['thumbs']
    ages = data['ages']
    titles = data['titles']
    
    maxposts = len(ups)
    rge = list(range(1,maxposts+1))
    cmap = plt.cm.get_cmap('Spectral')
    norm = matplotlib.colors.Normalize(vmin=0, vmax=24)
    cmapage = []
    for age in ages:
        cmapage.append(cmap(norm(age)))

    maxkarma = 1000
    
    plt.rcdefaults()
    f, (ax1,ax2,ax3) = plt.subplots(1, 3, sharey=True, figsize = (16,9), gridspec_kw = {'width_ratios':[1,0.02,1]})

    ax1.set_xlim(0, maxkarma)
    ax1.barh(rge,ups, color = cmapage)
    ax1.invert_xaxis()
    ax1.invert_yaxis()
    ax1.set_xlabel('Karma')
    ax1.xaxis.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.5)
    for n in range(len(titles)):
        ax1.text(maxkarma-10,n+1,titles[n])

    ax3.barh(rge,coms, color = cmapage)
    ax3.set_xlabel('Comments')
    ax3.xaxis.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.5)

    ax2.axis('off')
    for n in range(len(thumbs)):
        arr_img = mpimg.imread(thumbs[n])
        imagebox = OffsetImage(arr_img, 0.7)
        ab = AnnotationBbox(imagebox, (0.5, n+1), frameon=False)
        ax2.add_artist(ab)

    plt.suptitle(now.strftime('%c'))
    plt.yticks(rge)
    plotname = 'plots/'+str(increment).zfill(4)+'.png'
    plt.savefig(plotname)
    if show: plt.show()
    plt.close()
    return plotname


if __name__ == '__main__':
    datalist = collect_data(interval=10,ticks=4)

    for n in range(len(datalist)):
        make_chart(datalist[n],increment=n+1)
