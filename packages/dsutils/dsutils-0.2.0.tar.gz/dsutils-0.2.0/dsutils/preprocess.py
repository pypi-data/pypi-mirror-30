from __future__ import division, print_function

import pandas as pd
import numpy as np
from time import time
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA

import matplotlib.pyplot as plt
import seaborn as sns

class PreprocessDataFrame(object):
    """ main class of data preprocessing on Pandas DataFrame for data science projects,
    e.g it can apply label encoding, onehot encoding, PCA directly on DataFrame.
        it saves training proprecess instances (e.g. label encoding instances) to the object to be able to apply those on testing data.
    """
    def __init__(self, traindf, testdf = None):
        
        self.train = traindf.copy()
        self.train.columns = map(lambda x: x.strip(), self.train.columns)
        
        print(self.train.shape)
        self._stdnorm={}
        self._lbencode={}
        self._onehot={}
        self._del_cols=[]
        self._dummies=[]
        self._pca={}
        self._cluster={}
        # taxi project: keep original total_amount
        try:
            self._train_totamt = self.train['Total_amount']
            print("taxi project: save original total_amount data to _train_totamt")
        except:
            pass
        
        try:
            testdf.shape
            self.test.columns = map(lambda x: x.strip(), self.test.columns)
            self._test_totamt = self.test['Total_amount']
            print("taxi project: save original total_amount data to _test_totamt")
        except:
            self.test=testdf
        
    def add_testDataFrame(self, testdf):
        self.test=testdf.copy()
        self.test.columns = map(lambda x: x.strip(), self.test.columns)
        
        # taxi project: keep original total_amount
        try:
            self._test_totamt = self.test['Total_amount']
            print("taxi project: save original total_amount data to _test_totamt")
            
        except:
            pass        
        
        print (self.test.shape)
    
    def abs_posCols(self, cols, test=False):
        """abs cols should be all positives"""
        print("""abs cols should be all positives""")
        if not test:
            for i in cols:
                ngn=(self.train[i]<0).sum()
                if ngn>0:
                    self.train[i]=self.train[i].apply(abs)
                    print('negative found:',i,ngn)
        else:
            for i in cols:
                ngn=(self.test[i]<0).sum()
                if ngn>0:
                    self.test[i]=self.test[i].apply(abs)
                    print('negative found:',i,ngn)
                    
    def rm_null(self, threshold=0.995):
        print('before',self.train.shape)
        n=self.train.shape[0]
        for i in self.train:
            if self.train[i].isnull().sum()>n*threshold:
                print('remove column '+i)
                _ = self.train.pop(i)
                self._del_cols.append(i)
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
                self._del_cols.append(i)
        print('after ',self.train.shape)

    def dummy_train(self, cols, rmOne=False):
        print('before',self.train.shape)
        flag=1 if rmOne else 0
        for i in cols:
            self.train = pd.concat([self.train, pd.get_dummies(self.train[i], prefix=i.strip()).iloc[:,flag:]], axis=1)
            _ = self.train.pop(i)
            print('processing '+i)
            self._dummies.append(i)
        print('after ',self.train.shape)

    def dummy_test(self, rmOne=False):
        print('before',self.test.shape)
        flag=1 if rmOne else 0
        for i in self._dummies:
            self.test = pd.concat([self.test, pd.get_dummies(self.test[i], prefix=i.strip()).iloc[:,flag:]], axis=1)
            _ = self.test.pop(i)
            print('processing '+i)
        print('after ',self.test.shape)
        
        
    def train_stdnorm(self, cols):
        """standard scaling on selected cols"""
        import warnings
        warnings.filterwarnings("ignore") 
        
        for i in cols:
            print('scaling '+i)
            scaler = StandardScaler()
            self.train[i]=scaler.fit_transform(self.train[i].values.reshape(-1,1))
            self._stdnorm[i]=scaler
            
    def test_stdnorm(self):
        """standard scaling on cols that scaled in training"""
        
        import warnings
        warnings.filterwarnings("ignore") 
        
        if not self._stdnorm: print('train_stdnorm on training data first')
        try:
            self.test.shape
            for i in self._stdnorm:
                print ('scaleing '+i)
                self.test[i] = self._stdnorm[i].transform(self.test[i].values.reshape(-1,1))
        except Exception as e:
            print (e)
            print ('add test data first')

    def train_labelencode(self, cols):
        for i in cols:
            print('label encoding '+i)
            lb = LabelEncoder()
            self.train[i]=lb.fit_transform(self.train[i])
            self._lbencode[i]=lb          

    def test_labelencode(self):
        if not self._lbencode: print('train_labelencode on training data first')
        try:
            self.test.shape
            for i in self._lbencode:
                print ('label encoding '+i)
                self.test[i] = self._lbencode[i].transform(self.test[i])
        except Exception as e:
            print (e)
            print ('add test data first')             
            
            
    def train_Onehot(self, cols, rmOne=False):
        """make dummies with Onehot encoding from sklearn (After label encoding)"""
        print('before',self.train.shape)
        flag=1 if rmOne else 0


        
        for i in cols:
            print('Onehot encoding '+i)
            oh=OneHotEncoder(handle_unknown='ignore')
            x = oh.fit_transform(self.train[i].values.reshape(-1,1)).todense()
            x_cols=[i+'_'+str(j) for j in range(1,x.shape[1]+1)]
            X=pd.DataFrame(x, columns=x_cols).iloc[:,flag:]
            
            self.train = pd.concat([self.train, pd.DataFrame(X, columns=x_cols)], axis=1)
            _ = self.train.pop(i)
            self._onehot[i]=oh
            
        print('after',self.train.shape)
        
    def test_Onehot(self, rmOne=False):
        """make dummies with Onehot encoding from sklearn (After label encoding) on testing data"""
        print('before',self.test.shape)
        for i in self._onehot:
            print('Onehot encoding '+i)
            oh=self._onehot[i]
            
            x = oh.transform(self.test[i].values.reshape(-1,1)).todense()
            x_cols=[i+'_'+str(j) for j in range(1,x.shape[1]+1)]
            X=pd.DataFrame(x, columns=x_cols)
            
            self.test = pd.concat([self.test, pd.DataFrame(X, columns=x_cols)], axis=1)
            _ = self.test.pop(i)
            
        print('after',self.test.shape)   
        
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
            
    def rm_cols(self, cols, test=False):
        """remove features(cols) from dataFrame"""
        if not test:
            print('remove cols from training set')
            try:
                self.train.shape
                for i in cols:
                    _ = self.train.pop(i)
                    self._del_cols.append(i)
            except:
                print ('no train data')
        else:
            print('remove cols from test set')
            for j in cols:
                _ = self.test.pop(j)
    
    def rm_delcols_test(self):
        """remove training data deleted cols from test data as well"""
        print ("""remove training data deleted cols from test data as well""")
        for i in self._del_cols:
            _ = self.test.pop(i)
                
               
    def taxi_train_pcaXY(self):
        print ('training PCA of XY coordinates & add train data')
        xy=[['Pickup_longitude', 'Pickup_latitude'], ['Dropoff_longitude', 'Dropoff_latitude']]
        coll=[]
        for i in xy:
            coll.append(self.train[i].values)
            
        pca=PCA(2)    
        pca.fit(np.concatenate(coll))
        self._pca['PCA']=pca
        
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
        pca=self._pca['PCA']

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
        self._cluster['KMean']=km
        
        print('training used {:.2f} s'.format(time()-start))
        
        print('starting clustering training XY')
        
        self.train['cluster_pickup'] = km.predict(self.train[xy[0]])
        self.train['cluster_dropoff'] = km.predict(self.train[xy[1]])    
        
    def taxi_test_clusterKM(self):
        """add new feature by clustering XY on test data"""
        print("""add new feature by clustering XY on test data""")
        xy=[['Pickup_longitude', 'Pickup_latitude'], ['Dropoff_longitude', 'Dropoff_latitude']]
        start=time()
            
        km = self._cluster['KMean']
        
       
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
        print('add tip percentage col')
        if not test:
            self.train['Tip_pct'] = (self.train['Tip_amount']/self._train_totamt)*100
            self.train['Tip_pct'] = self.train['Tip_pct'].fillna(0)
            #self.train['Tip_pct'] = self.train['Tip_pct'].apply(lambda x: 100 if x>100 else x)
        else:
            self.test['Tip_pct'] = (self.test['Tip_amount']/self._test_totamt)*100
            self.test['Tip_pct'] = self.test['Tip_pct'].fillna(0)
            #self.test['Tip_pct'] = self.test['Tip_pct'].apply(lambda x: 100 if x>100 else x)   
            
    def taxi_rmTip(self, test=False):
        print('remove total Tip_amount')
        if not test:
            _ = self.train.pop('Tip_amount')
        else:
            _ = self.test.pop('Tip_amount')
            
                
    def remove_data(self):
        """for space purose remove train & test data and keeping trained models and parameters (scaler, PCA, kmeans, etc)"""
        print("""remove train & test data and keeping trained models and parameters (scaler, PCA, kmeans, etc)""")
        self.train=None
        self.test=None
        
    def chkRm_TrainTestDiff(self):
        """check and remove feature diff from test on train"""
        print("""check and remove feature diff from test on train""")
        print('train shape',self.train.shape)
        print('test shape',self.test.shape)
        flag = self.test.equals(self.test[self.train.columns])
        print ('train and test features are the same:',flag)
        self.test = self.test if flag else self.test[self.train.columns]
        

    #green taxi project, preprocess training data
    #pre-defined input, e.g.to_be_normalize_cols, can be replaced when calling the method
    def Taxi_train_preprocess(self, add_tip_pct=False, rm_tip_amount=False, add_XYdistance=True, kp_all_positive=False,
                              pos_cols = ['Passenger_count', 'Trip_distance', 'Fare_amount', 'Extra', 'MTA_tax', 'Tip_amount',\
                                                'Tolls_amount', 'improvement_surcharge', 'Total_amount'],
                              to_be_normalize_cols = [u'lpep_pickup_datetime', u'Lpep_dropoff_datetime', u'Pickup_longitude',\
                                                        u'Pickup_latitude', u'Dropoff_longitude', u'Dropoff_latitude', u'Passenger_count',\
                                                        u'Trip_distance', u'Fare_amount', u'Extra', u'MTA_tax', u'Tolls_amount',\
                                                        u'improvement_surcharge', u'Total_amount', u'duration_min', u'speed', \
                                                        u'xydistance', u'xyPCA_pickup1', u'xyPCA_pickup2', u'xyPCA_dropoff1',\
                                                        u'xyPCA_dropoff2', u'cluster_pickup', u'cluster_dropoff', u'pickup_weekday',\
                                                        u'pickup_hour'],\
                              to_be_dummies_cols = [u'VendorID', u'Store_and_fwd_flag',\
                                                    u'RateCodeID', u'Trip_type', u'Payment_type']):
        
        
        """green taxi project, preprocess training data"""
        import warnings
        warnings.filterwarnings("ignore") 
        
        print('preprocessing training data set')
        start=time()
        print("\n1/14 remove null values (>99%)")
        self.rm_null()    

        print("\n2/14 absolute features should be all positives")
        if kp_all_positive:
            self.abs_posCols(pos_cols, test=False)

        print("\n3/14 impute missing value as mode")
        self.imput_missing(kind='mode', test=False)

        print("\n4/14 parse date cols")
        self.parse_date(['lpep_pickup_datetime', 'Lpep_dropoff_datetime'], test=False)

        print("\n5/14 remove latitude and longitude outliers")
        self.taxi_rmXYoutliers(test=False)
        
        if add_tip_pct:
            print("\n5.2/14 add tip percentage")
            self.taxi_addTipPct(test=False)
        
        if rm_tip_amount:
            print("\n5.3/14 remove Tip_amount")
            self.taxi_rmTip(test=False)
        
        print("\n6/14 add duration minutes")
        self.taxi_addDuration(test=False)

        print("\n7/14 add speed")
        self.taxi_addSpeed(test=False)

        print("\n8/14 add coordinate distance (need external library geopy)")
        if add_XYdistance:
            self.taxi_add_xy_distance(test=False)
        else:
            to_be_normalize_cols.remove("xydistance")
            
        print("\n9/14 add hour of a day")
        self.taxi_addhour(test=False)

        print("\n10/14 add weekday")
        self.taxi_addweekday(test=False)

        print("\n11/14 apply PCA to latitude and longitude")
        self.taxi_train_pcaXY()

        print("\n12/14 apply K-mean cluster to latitude & longitude")
        self.taxi_train_clusterKM()

        print("\n13/14 scaling features")
        self.train_stdnorm(to_be_normalize_cols)

        print("\n14/14 One Hot encoding features")
        self.dummy_train(to_be_dummies_cols)

        print('Done!')
        print('Total time {:.2f} s'.format(time()-start))        

        
        
    #green taxi project, preprocess testing data
    #pre-defined input, e.g.to_be_normalize_cols, can be replaced when calling the method
    def Taxi_test_preprocess(self, add_tip_pct=False, rm_tip_amount=False, add_XYdistance=True, kp_all_positive=False,
                              pos_cols = ['Passenger_count', 'Trip_distance', 'Fare_amount', 'Extra', 'MTA_tax', 'Tip_amount',\
                                                'Tolls_amount', 'improvement_surcharge', 'Total_amount'],
                              to_be_normalize_cols = [u'lpep_pickup_datetime', u'Lpep_dropoff_datetime', u'Pickup_longitude',\
                                                        u'Pickup_latitude', u'Dropoff_longitude', u'Dropoff_latitude', u'Passenger_count',\
                                                        u'Trip_distance', u'Fare_amount', u'Extra', u'MTA_tax', u'Tolls_amount',\
                                                        u'improvement_surcharge', u'Total_amount', u'duration_min', u'speed', \
                                                        u'xydistance', u'xyPCA_pickup1', u'xyPCA_pickup2', u'xyPCA_dropoff1',\
                                                        u'xyPCA_dropoff2', u'cluster_pickup', u'cluster_dropoff', u'pickup_weekday',\
                                                        u'pickup_hour'],\
                              to_be_dummies_cols = [u'VendorID', u'Store_and_fwd_flag',\
                                                    u'RateCodeID', u'Trip_type', u'Payment_type']):
        
        
        """green taxi project, preprocess training data"""
        import warnings
        warnings.filterwarnings("ignore") 
        
        print('preprocessing testing data set')
        start=time()
        print("\n1/14 remove deleted cols from test")
        self.rm_delcols_test()    

        print("\n2/14 absolute features should be all positives")
        if kp_all_positive:
            self.abs_posCols(pos_cols, test=True)

        print("\n3/14 impute missing value as mode")
        self.imput_missing(kind='mode', test=True)

        print("\n4/14 parse date cols")
        self.parse_date(['lpep_pickup_datetime', 'Lpep_dropoff_datetime'], test=True)

        print("\n5/14 remove latitude and longitude outliers")
        self.taxi_rmXYoutliers(test=True)

        if add_tip_pct:
            print("\n5.2/14 add tip percentage")
            self.taxi_addTipPct(test=True)
        
        if rm_tip_amount:
            print("\n5.3/14 remove Tip_amount")
            self.taxi_rmTip(test=True)
        
        print("\n6/14 add duration minutes")
        self.taxi_addDuration(test=True)

        print("\n7/14 add speed")
        self.taxi_addSpeed(test=True)

        print("\n8/14 add coordinate distance (need external library geopy)")
        if add_XYdistance:
            self.taxi_add_xy_distance(test=True)
        else:
            to_be_normalize_cols.remove("xydistance")
            

        print("\n9/14 add hour of a day")
        self.taxi_addhour(test=True)

        print("\n10/14 add weekday")
        self.taxi_addweekday(test=True)

        print("\n11/14 apply PCA to latitude and longitude on test data")
        self.taxi_test_pcaXY()

        print("\n12/14 apply K-mean cluster to latitude & longitude on test data")
        self.taxi_test_clusterKM()

        print("\n13/14 scaling features on test data")
        self.test_stdnorm()

        print("\n14/14 One Hot encoding features on test")
        self.dummy_test()

        print('Done!')
        print('Total time {:.2f} s'.format(time()-start))        
        
        
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