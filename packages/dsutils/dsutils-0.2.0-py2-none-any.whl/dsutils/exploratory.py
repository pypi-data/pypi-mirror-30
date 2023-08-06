# author: Shichao (Richard Ji), jshichao@vt.edu
from __future__ import division, print_function
import pandas as pd
from time import time
import scipy

import matplotlib.pyplot as plt
import seaborn as sns
#sns.set_style('whitegrid')
#plt.rcParams['figure.figsize']=[10,6]

import numpy as np
import math
import warnings
warnings.filterwarnings("ignore") 

#from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
#import plotly.graph_objs as go
#init_notebook_mode(connected=True)



class TimeAggDis(object):
    """
    groupby agg level: 'day', 'dayofweek','dayofyear', 'days_in_month', 'hour', 'minute', 'month','quarter','second','week','weekday','weekday_name','weekofyear','year' etc.
    """
    def __init__(self, df, date_col='lpep_pickup_datetime', num_col='Trip_distance', groupby='hour'):
        self.data=df[[date_col,num_col]]
        exec('self.data[groupby]=df[date_col].dt.'+groupby)
        self.aggv=self.data.groupby(groupby)
        self.groupby=groupby
        self.num_col=num_col
        
        self.mean = self.aggv[num_col].mean()
        self.median = self.aggv[num_col].median()   
        self.report = pd.DataFrame([self.mean, self.median]).transpose()
        self.report.columns = ['Mean_'+num_col, 'Median_'+num_col]        
        
        
    def getDF(self):
        return self.data
    def getReport(self):
        return self.report
    
    def plotReport(self, plotkind='Bar', figsize=[20,8]):
        #plt.style.use('seaborn-notebook')
        plt.style.use('seaborn')
        
        ax = self.report.plot(kind = plotkind, figsize=figsize, fontsize=14, alpha=0.8)
        yname= self.num_col+'(miles)' if self.num_col=='Trip_distance' else self.num_col
        ax.set_xlabel(self.groupby, fontdict={'size':20})
        ax.set_ylabel(yname, fontdict={'size':20})
        
        _ = plt.xticks(rotation=0)
        text2 = self.groupby+' of the day' if self.groupby=='hour' else self.groupby
        _ = plt.title('{} chart of mean and median of {} by {} '.format(plotkind,self.num_col, text2), fontsize=20)
        plt.legend( prop={'size': 20})

        
        
        
class PlotHist(object):
    """Class helps plot multiple histogram of selected column of Pandas DataFrame
    Remove upper outliers by specified standard deviation"""
    def __init__(self, df, col='Trip_distance', upper_std=3):
        self.data = df[col]
        self.col=col
        self.upper_std=upper_std
        self.upper_limit = self.data.mean()+self.upper_std*self.data.std()
        self.n=self.data.shape[0]
        self.outlier_n=self.data[self.data>self.upper_limit].shape[0]
        print('{} of {} outliers detected {:.2f}% remain of feature {} at {} std'\
              .format(self.outlier_n, self.n, (self.n-self.outlier_n)/self.n*100, self.col, self.upper_std))
        
    def update_upper_limit(self, std):
        self.upper_limit = self.data.mean()+std*self.data.std()
        
    def get_percentile(self, pct_list):
        return self.data.quantile(pct_list)
    
    def plot_helper(self, *arr):

        plt.style.use('seaborn')


        fig = plt.figure(figsize=[20,15])
        n=len(arr)
        row = math.ceil(n/2)
        for i in range(n):
            plt.subplot(row,2, i+1)
            log = True if i%2==1 else False
                
            ax = arr[i](log)
            ax.tick_params(labelsize=14)
            ax.xaxis.label.set_size(16)
            ax.yaxis.label.set_size(16)
            ax.title.set_size(18)

        fig.subplots_adjust(hspace=0.5)    
        fig.suptitle('histogram of '+self.col, fontsize=30)


    def hist(self, log=False):
        
        ax=self.data.hist(bins=50, edgecolor='w', alpha=0.7)
        text = self.col+'(miles)' if self.col=='Trip_distance' else self.col
        ax.set_xlabel(text)
        
        if log:
            ax.set_ylabel('count (log scale)')
            ax.set_title('full dataset with log scale of y')     
            ax.set_yscale('log')
            
        else:    
            ax.set_ylabel('count')
            ax.set_title('full dataset')
        return ax
    
    def hist_rm_outlier(self, log=False):
        
        text = self.col+'(miles)' if self.col=='Trip_distance' else self.col
        
        ax=self.data[self.data < self.upper_limit].hist(bins=50, edgecolor='w', alpha=0.4, color='g')        

        if log:
            ax.set_xlabel(text)
            ax.set_ylabel('count (log scale)')
            ax.set_title('data without outlier with log scale of y axis')
            ax.set_yscale('log')       
        else:
            ax.set_xlabel(text)
            ax.set_title('data without outliers')
            ax.set_ylabel('count')         
            
        return ax

    def plot(self):
        
        self.plot_helper(self.hist, self.hist, self.hist_rm_outlier, self.hist_rm_outlier)

        
        
        
def plot_coordinates(df, limit=True, xlimit = [-74.10, -73.70], ylimit = [40.55, 40.95], 
                     figsize= [20, 20] ,frame=False, 
                     include_pickup=True, include_dropoff=True,
                     xy_eq_scale=True,
                     JFK = [-73.7851, 40.6463],
                     LGA = [-73.8685, 40.7720],
                     EWR = [-74.1815, 40.6895]):
    """scatter plot coordinates"""

    
    # xlim = [-74.10, -73.70]; ylim = [40.55, 40.95]
    
    #JFK = [-73.7851, 40.6463]
    #LGA = [-73.8685, 40.7720]
    #EWR = [-74.1815, 40.6895]
    
    
    
    figsize= figsize
    
    plt.style.use('dark_background')
    
    

    
    #sns.set_style('darkgrid')

    #start=time()
    
    pickup_sx = df['Pickup_longitude']
    pickup_sy = df['Pickup_latitude']
    dropoff_sx = df['Dropoff_longitude']
    dropoff_sy = df['Dropoff_latitude']

    pickup_x  = pickup_sx.values
    pickup_y  = pickup_sy.values
    dropoff_x = dropoff_sx.values
    dropoff_y = dropoff_sy.values
    
    # find boundry of given coordinates, ignore error "0"
    
    #rm_zero = lambda x: set(x)-set([0])
    #px,py,dx,dy = rm_zero(pickup_x),rm_zero(pickup_y),rm_zero(dropoff_x),rm_zero(dropoff_y)
    #xlim=[min(min(px), min(dx)), max(max(px),max(dx))]
    #ylim=[min(min(py), min(dy)), max(max(py),max(dy))]
    
    #print (xlim, ylim)

    #sns.set_style('white')
    
    
    xlim=pickup_sx.quantile([0.002,0.997]).values
    ylim=pickup_sy.quantile([0.002,0.997]).values

    fig, ax = plt.subplots(figsize=figsize)
    
    
    if include_pickup:
        blue = ax.scatter(pickup_x, pickup_y, s=0.05, color='c', alpha=0.6)
    if include_dropoff:
        red = ax.scatter(dropoff_x, dropoff_y, s=0.05, color='red', alpha=0.15)

    
    if limit:
        xlim=xlimit
        ylim=ylimit
        
    if xy_eq_scale:
        plt.axis('equal')
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    ax.set_title('coordinates')
    ax.title.set_size(20)



    circle1 = plt.Circle(JFK, 0.01,  fill=False, color='w', linewidth=1)
    circle2 = plt.Circle(LGA, 0.01,  fill=False, color='w', linewidth=1)
    circle3 = plt.Circle(EWR, 0.01,  fill=False, color='w', linewidth=1)
    ax.add_artist(circle1)
    ax.add_artist(circle2)
    ax.add_artist(circle3)
    plt.text(JFK[0]+0.01, JFK[1], 'JFK', fontdict={'size':13})
    plt.text(LGA[0], LGA[1]+0.01, 'LGA', fontdict={'size':13})
    plt.text(EWR[0]+0.01, EWR[1], 'EWR', fontdict={'size':13})

    
    import matplotlib.patches as patches
    
    red_patch = patches.Patch(color='red', label='Dropoff')
    blue_patch = patches.Patch(color='cyan', label='Pickup')




    plt.legend(handles=[blue_patch, red_patch], loc='upper left', prop={'size': 16})
    
    # add a square to illustrate the range of airport captures by coordinates
    ax.add_patch(
    patches.Rectangle(
        JFK,
        0.01,
        0.01,
        color='g',
        linewidth =2,
        fill=False     
    ))
    if not frame:
        plt.axis('off')
        
    ax.grid(False)
    
    return ax



    
def add_airport(df, sep=True):
    "add airport columns to DataFrame based on coordinations"
    
    def add_single_airport(df, label, sep=True):
        "helper function, find and add one airport to two DataFrame column, Airport_pickup, Airport_dropoff"
        
        df=df.copy()
        c=['Pickup_longitude','Pickup_latitude','Dropoff_longitude','Dropoff_latitude']
        dic={
        'JFK' : [-73.7851, 40.6463],
        'LGA' : [-73.8685, 40.7720],
        'EWR' : [-74.1815, 40.6895]}

        boundary = lambda x: [x-0.01, x+0.01] 
        boundry_helper = lambda x, y: True if (x>y[0] and x<y[1]) else False

        index_coll=[]
        for i in c:
            if 'long' in i: 
                index_coll.append(set(df['VendorID'][df[i].apply(boundry_helper, y=map(boundary, dic[label])[0])].index))
            else:
                index_coll.append(set(df['VendorID'][df[i].apply(boundry_helper, y=map(boundary, dic[label])[1])].index))


        pickup = list(reduce(lambda x, y: x&y, index_coll[:2]))
        dropoff = list(reduce(lambda x, y: x&y, index_coll[2:]))

        if sep:
            df.loc[pickup,'Airport_pickup']=label
            df.loc[dropoff,'Airport_dropoff']=label

        mutual_index= list(set(pickup)|set(dropoff))
        df.loc[mutual_index,'Airport']=label
        return df    
    
    
    # add 3 single airports
    df = add_single_airport(df, 'JFK', sep=sep)
    df = add_single_airport(df, 'LGA', sep=sep)
    df = add_single_airport(df, 'EWR', sep=sep)
    
    
    if sep:
        df['Airport_pickup']=df['Airport_pickup'].fillna('Non_Airport')
        df['Airport_dropoff']=df['Airport_dropoff'].fillna('Non_Airport')
        
    df['Airport'] = df['Airport'].fillna('Non_Airport')
    return df


def plot_hr_cat(df, colname='Airport', agg='hour of the day', numeric='Trip_distance', airport=True):
#     plt.figure(figsize = (20, 8))
    for i in df[colname].unique():
        if 'Non' in i:
            plt.plot(df.groupby(df[df[colname]==i][agg])[numeric].mean(), ':', label=i)
        else:
            plt.plot(df.groupby(df[df[colname]==i][agg])[numeric].mean(), label=i)
        
    if airport:
        plt.plot(df.groupby(df[df[colname]!='Non_Airport'][agg])[numeric].mean(), '--', label='All Airport')
        
        plt.xticks(range(0,24,2))
    
    plt.xlabel(agg)
    plt.ylabel(numeric)
    plt.title(numeric+' by '+agg)
    plt.legend()    

def add_duration(df, min_sec='m'):
    if min_sec=='m':
        df['duration_min'] = (df['Lpep_dropoff_datetime'] - df['lpep_pickup_datetime']).dt.seconds/60
    else:
        df['duration_sec'] = (df['Lpep_dropoff_datetime'] - df['lpep_pickup_datetime']).dt.seconds
        
    return df

def add_speed(df):
    "average miles/hour"
    df['speed']=df['Trip_distance']/(df['duration_min']/60)
    return df



def test_ANOVA(df, value, category, cutoff=0.05):
    print('perform ANOVA test on Value: {} by Category: {}'.format(value, category))
    print('return True if groups of value are statistically the same otherwise False')
    print()
    data_by_group=[]
    for group in df[category].unique():
        print(category,':',str(group).ljust(9), end=' ')    
        data_by_group.append(df[df[category]==group][value].values)
        print('has',len(data_by_group[-1]),'instances')
    
    print()
    result = scipy.stats.f_oneway(*data_by_group)
    _ ,p = result
    print (result)
    print()
    if p > cutoff:
        print('average values of {} by different categories :{} are statistically the SAME on significant level {}'\
             .format(value, category, cutoff))
        return True
    else:
        print('Average values of {} by different categories :{} are statistically DIFFERENT on significant level {}'\
             .format(value, category, cutoff))
        return False        