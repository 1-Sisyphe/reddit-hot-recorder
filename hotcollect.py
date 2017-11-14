import praw
import urllib.request
from datetime import datetime
from time import sleep
import json

def get_reddit(credfile = 'reddit_credentials.json'):
    with open(credfile) as json_data:
        cred = json.load(json_data)
    reddit = praw.Reddit(client_id= cred['client_id'],
                         client_secret= cred ['client_secret'],
                         user_agent= cred['user_agent'])
    return reddit

def get_data(reddit=None,sub='france', maxposts=10):

    if not reddit:
        reddit = get_reddit()

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
    return data

def collect_data(sub='france',maxposts=10,interval=10,ticks=10,feedback=True,savefile=None):
    reddit = get_reddit()
    data_collec = []
    for n in range(ticks):
        data = get_data(reddit,sub,maxposts)
        data_collec.append(data)
        if feedback:
            print('{}/{} snapshot recorded on {}'.format(n+1,ticks,data['timestamp']))
        if savefile:
            with open(savefile, 'w') as f:
                json.dump(data_collec, f)
        if n!=ticks-1: #dont sleep if it's the last extract
            sleep(interval)
    return data_collec

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
