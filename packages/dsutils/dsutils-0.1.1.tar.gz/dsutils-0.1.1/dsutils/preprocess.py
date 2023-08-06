from __future__ import division, print_function

import pandas as pd
import numpy as np
from time import time
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA


class PreprocessDataFrame(object):
    def __init__(self, traindf, testdf = None):
        
        self.train = traindf.copy()
        self.train.columns = map(lambda x: x.strip(), self.train.columns)
        
        print(self.train.shape)
        self.stdnorm={}
        self.lbencode={}
        self.del_cols=[]
        self.dummies=[]
        self.pca={}
        self.cluster={}
        
        try:
            testdf.shape
            self.test.columns = map(lambda x: x.strip(), self.test.columns)
        except:
            self.test=testdf
        
    def add_testDataFrame(self, testdf):
        self.test=testdf.copy()
        self.test.columns = map(lambda x: x.strip(), self.test.columns)
        
        print (self.test.shape)
        
    def rm_null(self, threshold=0.995):
        print('before',self.train.shape)
        n=self.train.shape[0]
        for i in self.train:
            if self.train[i].isnull().sum()>n*threshold:
                print('remove column '+i)
                _ = self.train.pop(i)
                self.del_cols.append(i)
        print('after ',self.train.shape)


    def imput_missing(self, kind='mode', test=False):
        """kind = 'mean'/'mode' or 'value'"""
        
        def imput(df):
            df=df.copy()
            for i in df:
                n = df[i].isnull().sum()
                if n>0:
                    print (i, 'null counts :',n)
                    if kind=='mean':
                        df[i] = df[i].fillna(df[i].mean())
                    elif kind=='mode':
                        md = df[i].mode()
                        if len(md)<1:print(i,'no mode')
                        else: df[i] = df[i].fillna(md[0])
                    else:
                        df[i] = df[i].fillna(kind)
            return df
        
        if not test:
            print('training data')
            try:
                self.train.shape
                self.train = imput(self.train)
            except:
                print('no train data')
        else:
            try:
                self.test.shape
                print('testing data')
                self.test = imput(self.test)
            except:
                print('no test data')
                
                
    def parse_date(self, cols, test=False):
        
        print ('parse date cols')
        if not test:
            try:
                self.train.shape
                for i in cols:
                    self.train[i]=pd.to_datetime(self.train[i])
            except:
                print ('no train data')
        else:    
            try:
                self.test.shape
                for j in cols:
                    self.test[j]=pd.to_datetime(self.test[j])
            except:
                print('no test data')                
        
    def rm_common(self, threshold=0.999):
        print('before',self.train.shape)
        n=self.train.shape[0]
        for i in self.train:
            if self.train[i].value_counts().max()>n*threshold:
                print('remove column '+i)
                _ = self.train.pop(i)
                self.del_cols.append(i)
        print('after ',self.train.shape)

    def dummy_train(self, cols, rmOne=False):
        print('before',self.train.shape)
        flag=1 if rmOne else 0
        for i in cols:
            self.train = pd.concat([self.train, pd.get_dummies(self.train[i], prefix=i.strip()).iloc[:,flag:]], axis=1)
            _ = self.train.pop(i)
            print('processing '+i)
            self.dummies.append(i)
        print('after ',self.train.shape)

    def dummy_test(self, rmOne=False):
        print('before',self.test.shape)
        flag=1 if rmOne else 0
        for i in self.dummies:
            self.test = pd.concat([self.test, pd.get_dummies(self.test[i], prefix=i.strip()).iloc[:,flag:]], axis=1)
            _ = self.test.pop(i)
            print('processing '+i)
        print('after ',self.test.shape)
        
        
    def train_stdnorm(self, cols):
        for i in cols:
            print('scaling '+i)
            scaler = StandardScaler()
            self.train[i]=scaler.fit_transform(self.train[i].values.reshape(-1,1))
            self.stdnorm[i]=scaler
            
    def test_stdnorm(self):
        if not self.stdnorm: print('train_stdnorm on training data first')
        try:
            self.test.shape
            for i in self.stdnorm:
                print ('scaleing '+i)
                self.test[i] = self.stdnorm[i].transform(self.test[i].values.reshape(-1,1))
        except Exception as e:
            print (e)
            print ('add test data first')

    def train_labelencode(self, cols):
        for i in cols:
            print('label encoding '+i)
            lb = LabelEncoder()
            self.train[i]=lb.fit_transform(self.train[i])
            self.lbencode[i]=lb          

    def test_labelencode(self):
        if not self.lbencode: print('train_labelencode on training data first')
        try:
            self.test.shape
            for i in self.lbencode:
                print ('label encoding '+i)
                self.test[i] = self.lbencode[i].transform(self.test[i])
        except Exception as e:
            print (e)
            print ('add test data first')             
            
            

            
    def taxi_add_xy_distance(self, test=False):
        
        try:
            import geopy.distance
        except:
            print('install geopy, e.g. "pip install geopy"')
            return
        print("add new col: approx distance (miles) between latitude and longitude (may take some time...)")
        
        
        def process(df):
            start=time()
            df=df.copy()
            t = df.shape[0]
            count={'N':0}
           
            def helper(row):
                
                n=count['N']
                if n%100000==0 or n==0: 
                    print("{}/{}".format(n//100000, t//100000), end=" ")
                    
                n+=1
                count['N']=n
                
                return geopy.distance.vincenty([row['Dropoff_latitude'], row['Dropoff_longitude']],
                                 [row['Pickup_latitude'], row['Pickup_longitude']]).miles   
            
            df['xydistance'] = df.apply(helper, axis=1)
            print('total used {:.2f} s'.format(time()-start))
            return df
        try:
            self.train.shape
            if "xydistance" not in self.train.columns:
                print('adding xydistance to TRAINing data')
                self.train = process(self.train)
            else:
                print ('xydistance exists in training')
        except:
            print ('no train data')
            
        if test:
            if "xydistance" not in self.test.columns:
                print('adding xydistance to TESTing data')
                self.test = process(self.test)
            else:
                print ('xydistance exists in testing')


            
    def taxi_addhour(self, pickup=True, test=False):
        """add new col hour of the day (after parse date)"""
        print("""add new col hour of the day (after parse date)""")
        if not test:
            try:
                self.train.shape
                if pickup:
                    self.train['pickup_hour']=self.train['lpep_pickup_datetime'].dt.hour
                else:
                    self.train['dropoff_hour']=self.train['Lpep_dropoff_datetime'].dt.hour
            except:
                print ('no train data')
        else:    
            try:
                self.test.shape
                if pickup:
                    self.test['pickup_hour']=self.test['lpep_pickup_datetime'].dt.hour
                else:
                    self.test['dropoff_hour']=self.test['Lpep_dropoff_datetime'].dt.hour
            except:
                print ('no test data')        

    def taxi_addweekday(self, pickup=True, test=False):
        """add new col weekday (after parse date)"""
        print("""add new col weekday (after parse date)""")
        if not test:
            try:
                self.train.shape
                if pickup:
                    self.train['pickup_weekday']=self.train['lpep_pickup_datetime'].dt.weekday
                else:
                    self.train['dropoff_weekday']=self.train['Lpep_dropoff_datetime'].dt.weekday
            except:
                print ('no train data')
        else:    
            try:
                self.test.shape
                if pickup:
                    self.test['pickup_weekday']=self.test['lpep_pickup_datetime'].dt.weekday
                else:
                    self.test['dropoff_weekday']=self.test['Lpep_dropoff_datetime'].dt.weekday
            except:
                print ('no test data')                    
            
    def rm_cols(self, cols):
        try:
            self.train.shape
            for i in cols:
                _ = self.train.pop(i)
                self.del_cols.append(i)
        except:
            print ('no train data')
                
               
    def taxi_train_pcaXY(self):
        print ('training PCA of XY coordinates & add train data')
        xy=[['Pickup_longitude', 'Pickup_latitude'], ['Dropoff_longitude', 'Dropoff_latitude']]
        coll=[]
        for i in xy:
            coll.append(self.train[i].values)
            
        pca=PCA(2)    
        pca.fit(np.concatenate(coll))
        self.pca['PCA']=pca
        
        pca_pickup  = pca.transform(self.train[xy[0]])
        pca_dropoff = pca.transform(self.train[xy[1]])
        
        self.train['xyPCA_pickup1']  = pca_pickup[:,0]
        self.train['xyPCA_pickup2']  = pca_pickup[:,1]
        self.train['xyPCA_dropoff1'] = pca_dropoff[:,0]
        self.train['xyPCA_dropoff2'] = pca_dropoff[:,1]
        
    def taxi_rmXYoutliers(self, test=False):
        print('remove latitude & longtitude outliers "0"')
        xy=['Pickup_longitude', 'Pickup_latitude','Dropoff_longitude', 'Dropoff_latitude']
        if test:
            for i in xy:
                mean=self.test[i].mean()
                self.test[i] = self.test[i].apply(lambda x: mean if x==0 else x)
        else:
            for i in xy:
                mean=self.train[i].mean()
                self.train[i] = self.train[i].apply(lambda x: mean if x==0 else x)            
                
    
    def taxi_test_pcaXY(self):
        print ('adding PCA of XY coordinates to test data')
        xy=[['Pickup_longitude', 'Pickup_latitude'], ['Dropoff_longitude', 'Dropoff_latitude']]
        pca=self.pca['PCA']

        pca_pickup  = pca.transform(self.test[xy[0]])
        pca_dropoff = pca.transform(self.test[xy[1]])        

        self.test['xyPCA_pickup1']  = pca_pickup[:,0]
        self.test['xyPCA_pickup2']  = pca_pickup[:,1]
        self.test['xyPCA_dropoff1'] = pca_dropoff[:,0]
        self.test['xyPCA_dropoff2'] = pca_dropoff[:,1]
        
        
    def taxi_train_clusterKM(self, cluster=50):
        """add new feature by clustering XY, use MiniBatch_Kmean instead of Kmean for less training time"""
        print('start training K_Means cluster')
        xy=[['Pickup_longitude', 'Pickup_latitude'], ['Dropoff_longitude', 'Dropoff_latitude']]
        start=time()
        coll=[]
        for i in xy:
            coll.append(self.train[i].values)    
        
        coll = np.vstack(coll)
        km = MiniBatchKMeans(n_clusters=cluster, batch_size=10000).fit(coll)     
        self.cluster['KMean']=km
        
        print('training used {:.2f} s'.format(time()-start))
        
        print('starting clustering training XY')
        
        self.train['cluster_pickup'] = km.predict(self.train[xy[0]])
        self.train['cluster_dropoff'] = km.predict(self.train[xy[1]])    
        
    def taxi_test_clusterKM(self):
        """add new feature by clustering XY on test data"""
        xy=[['Pickup_longitude', 'Pickup_latitude'], ['Dropoff_longitude', 'Dropoff_latitude']]
        start=time()
            
        km = self.cluster['KMean']
        
       
        self.test['cluster_pickup'] = km.predict(self.test[xy[0]])
        self.test['cluster_dropoff'] = km.predict(self.test[xy[1]])         
        print('used {:.2f} s'.format(time()-start))
        
    def taxi_addSpeed(self, test=False):  
        "average miles/hour"
        print ('add speed mph')
        if not test:
            self.train['speed']=self.train['Trip_distance']/(self.train['duration_min']/60)
            self.train['speed']=self.train['speed'].apply(lambda x: 0 if x>100 else x)
            self.train['speed']=self.train['speed'].fillna(0)
            
        else:
            self.test['speed']=self.test['Trip_distance']/(self.test['duration_min']/60)
            self.test['speed']=self.test['speed'].apply(lambda x: 0 if x>100 else x)
            self.test['speed']=self.test['speed'].fillna(0)
    
    

    
    def taxi_addDuration(self, min_sec='m', test=False):
        print ('add duration (minutes)')
        if not test:
            if min_sec=='m':
                self.train['duration_min'] = (self.train['Lpep_dropoff_datetime'] - self.train['lpep_pickup_datetime']).dt.seconds/60
            else:
                self.train['duration_sec'] = (self.train['Lpep_dropoff_datetime'] - self.train['lpep_pickup_datetime']).dt.seconds

        else:
            if min_sec=='m':
                self.test['duration_min'] = (self.test['Lpep_dropoff_datetime'] - self.test['lpep_pickup_datetime']).dt.seconds/60
            else:
                self.test['duration_sec'] = (self.test['Lpep_dropoff_datetime'] - self.test['lpep_pickup_datetime']).dt.seconds    

    def taxi_addTipPct(self, test=False):    
        pass
        

        
        
def plot_cluster(train,  N=None):
    """plot distribution of clusters of taxi after clustering"""
    if not N:
        N=train.shape[0]


    xlim=[-74.05,-73.72]
    ylim=[40.56,40.92]



    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=[14,14])


    ax.scatter(train['Pickup_longitude'].values[:N], train['Pickup_latitude'].values[:N], s=5, lw=0,
               c=train['cluster_pickup'][:N].values, cmap='tab20', alpha=0.1)

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.show()