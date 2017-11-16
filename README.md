# reddit-hot-recorder

### What is it?
- My first published python project :)
- A script that collects metadata from a Reddit's subreddit hot section, at regular intervals, and turns it into a serie of charts, to be animated.

Here is a result, after recording xx hours of activity on the top of r/all:

### How does it work?
- The hotcollect module takes care of collecting the data and can save it into a json.  
- The hotplot module uses the collected data to generate a serie of charts.  
- The final step requires a software to turn the serie of charts (.png files) into a movie or a .gif.  

##### required:
- matplotlib
- numpy
- [PRAW](https://praw.readthedocs.io/en/latest/)

### Examples:
```python
from hotcollect import collect_data
from hotplot import plot_collec
data_collec = collect_data(sub='france',maxposts=10,interval_sec=30,
duration_min=5,feedback=True,savefile='france.json')
plot_collec(data_collec)
```
- This script will watch the top 10 posts of r/france during 5 minutes, every 30 seconds.  
*note: You should not go bellow `interval_sec=10` as it takes a couple of seconds for the API to collect the data.*  
- It will save the collected data in france.json.  
- It will print the following feedback:  
```shell
1/10 snapshot recorded on Nov 16 2017 11:37:37
2/10 snapshot recorded on Nov 16 2017 11:38:09
```
- `plot_collec(data_collec)` will generate 10 .png to be turned into a .mp4.  
On linux, I use ffmepg to turns the serie of .png into a .mp4, as follow:  
```shell
ffmpeg -start_number 1 -framerate 24 -i %04d.png output.mp4
```  

If your local time doesn't match the local time of your viewers, you can correct the timestamp of your collected data by using `offset_timestamp(data_collec, delta_hours)`.

For example, if I live in Europe and want to plot for american viewers (-7 hours compared to my local time):
```python
from hotcollect import collect_data, offset_timestamp
from hotplot import plot_collec
data_collec = collect_data(sub='all',maxposts=10,interval_sec=30,
duration_min=5,feedback=False)
for data in data_collec:
    data = offset_timestamp(data, -7)
plot_collec(data_collec)
```

### And finally:
- feel free to comment my code, declare issues, propose changes, etc.  
It was a learning exercise for me, both on Python and on using GitHub.  
- it's under MIT licence which mean that you can do whatever you want with it, if I understood correctly.  
