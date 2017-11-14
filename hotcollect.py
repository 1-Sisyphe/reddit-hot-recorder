import praw
import urllib.request
from datetime import datetime
from time import sleep
import json

def get_reddit(credfile = 'reddit_credentials.json'):
    '''
    Initiate the connexion to Reddit API by using the reddit_credentials
    stored in credfile (json file).
    Credentials should be stored as:
    {"client_id":"XX1234XXX",
    "client_secret":"xxx1234xxx",
    "user_agent":"linux:xxx (by /u/xxx)"}
    '''
    with open(credfile) as json_data:
        cred = json.load(json_data)
    reddit = praw.Reddit(client_id= cred['client_id'],
                         client_secret= cred ['client_secret'],
                         user_agent= cred['user_agent'])
    return reddit

def get_data(reddit=None,sub='france', maxposts=10):
    '''
    Extract one datapoint consisting of maxposts posts, from the targeted sub.
    For each post, extract:
    -number of ups (=karma)
    -number of Comments
    -thumbnail
    -age in minutes
    -title
    -subreddit where the post was posted (useful for r/all)
    In addition, the datapoint carries two metadata: timestamp of the record and targeted sub.
    '''
    if not reddit:
        reddit = get_reddit()

    limit_read = maxposts + 2 #read two more posts than asked, in case of stickies
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
            age = divmod(age.total_seconds(), 60)[0] #age is in minutes
            data['ages'].append(age)
            try : #some posts dont have previews. Use _nopreview.png as backup.
                image_name = submission.name+'.jpg'
                image_url = submission.preview['images'][0]['resolutions'][0]['url']
                urllib.request.urlretrieve(image_url, 'thumbs/'+image_name)
            except AttributeError:
                image_name = '_nopreview.png'
            data['thumbs'].append('thumbs/'+image_name)
            data['subs'].append(submission.subreddit_name_prefixed) #useful for r/all

    #keep only maxposts nbr of posts, so remove the stickies if any
    for d in data:
        data[d] = data[d][:maxposts]

    data['timestamp'] = datetime.now().strftime("%b %d %Y %H:%M:%S")
    data['sub'] = sub
    return data

def collect_data(sub='france',maxposts=10,interval=10,size=10,feedback=True,savefile=None):
    '''
    This module repeats the get_data function as many times as specified by size, at every interval in seconds.
    feedback = True will print out a progress information.
    savefile must be a json file name to dump the data in. Data is dumped at each loop.
    Returns data_collec, a list of data from get_data.
    '''
    reddit = get_reddit()
    data_collec = []
    for n in range(size):
        data = get_data(reddit,sub,maxposts)
        data_collec.append(data)
        if feedback:
            print('{}/{} snapshot recorded on {}'.format(n+1,size,data['timestamp']))
        if savefile:
            with open(savefile, 'w') as f:
                json.dump(data_collec, f)
        if n!=size-1: #dont sleep if it's the last extract
            sleep(interval)
    return data_collec

def offset_timestamp(data,delta_hours):
    '''
    Add (or remove if negative) delta_hours hours to data['timestamp'].
    Useful if your extract timestamp is not in the viewer excepted local time.
    Return one data point.
    '''
    from datetime import timedelta
    timestamp = datetime.strptime(data['timestamp'],"%b %d %Y %H:%M:%S")
    timestamp = timestamp + timedelta(hours=delta_hours)
    data['timestamp'] = timestamp.strftime("%b %d %Y %H:%M:%S")
    return data

if __name__ == '__main__':
    pass
