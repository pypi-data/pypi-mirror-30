# -*- coding: utf-8 -*-
__author__ = 'Xujing' 

import pandas as pd
import numpy as np

from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import VotingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation, metrics
from sklearn.model_selection import cross_val_score
from sklearn.cross_validation import train_test_split
from sklearn.externals import joblib

import xgboost as xgb
from xgboost.sklearn import XGBClassifier
import lightgbm as lgb

import matplotlib.pyplot as plt
import itertools
import time
import datetime
from pandasql import sqldf
import re
import os

  


class gridxgb():
    '''
    =============================================================================================
    Description: A class for Inter-Credit xinxiu predict,haha.

    Usage：The whole process of data processing, model training and evaluation and model prediction.

    Author(s): XuJing
    =============================================================================================
    Methods:

    	data_pro
    	threshold_bset
    	predict_clf
    	gridxgbt
    	xgbt
    	predictm
        ......
        -----------------------------------------------------------------------------------------
        
    Require:
        import pandas as pd
    	import numpy as np

    	from sklearn.model_selection import GridSearchCV
    	from sklearn.ensemble import VotingClassifier
    	from sklearn.ensemble import RandomForestClassifier
    	from sklearn import cross_validation, metrics
    	from sklearn.model_selection import cross_val_score
    	from sklearn.cross_validation import train_test_split
    	from sklearn.externals import joblib

    	import xgboost as xgb
    	from xgboost.sklearn import XGBClassifier
    	import lightgbm as lgb

    	import matplotlib.pyplot as plt
    	import itertools
    	import json
    	import time
    	import datetime
    	from pandasql import sqldf
    	import re

    '''

    def stamp2date(self,timeStamp):
        try:
            timeArray = time.localtime(float(timeStamp))
            otherStyleTime = time.strftime("%Y-%m-%d", timeArray) 
            timeArray = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d")
        except:
            timeArray = datetime.datetime.strptime('1970-01-01', "%Y-%m-%d")

        return timeArray


    def data_pro(self,data_seek,data_case,phone_data,address_data,progress_data,data_type = 'train',target_index=0):
        '''
        =================================================================================
        Description: A class for Inter-Credit xinxiu data process.

        Usage：you can use this method to process train or test data.

        Author(s): XuJing

        =================================================================================

        Arguments:

        		data_seek: seek table data frame
        		data_case: case table data frame
        		phone_data: phone table data frame
        		address_data: address table data frame
        		progress_data: progress table data frame

        		data_type: train or test
        		target_index:0 threshold of recovery rate

        '''
        #data_seek
        self.data0_fina  = pd.DataFrame({'kehu':list(data_seek.kehu),'case_no':list(data_seek.case_no),'id_no':list(data_seek.id_no),'handle_time':list(data_seek.handle_time),'seek_progress':list(data_seek.seek_progress)})
        self.data0_fina.dropna(axis=0,inplace=True)

        #ga table
        #data_case
        my_bool1 = [list(data_case.case_no)[i] not in list(self.data0_fina.case_no) for i in range(len(list(data_case.case_no)))]
        
        self.data_ga = self.data_case[my_bool1]
        self.data_cases = self.data_case[np.logical_not(my_bool1)]

        #data_case self

        self.data_cases_1 = self.data_cases[['case_no','id_no','start_date']]
        self.data_case_1['hkje'] = list(self.data_cases.repay_allmoney_yes)
        self.data_case_1['waje'] = list(self.data_cases.case_money)
        self.data_ga_1 = pd.merge(self.data_ga, self.data_cases_1, how='left', on='id_no', left_on=None, right_on=None,
              left_index=False, right_index=False, sort=False,
              suffixes=('_x', '_y'), copy=True, indicator=False)

         
        self.data_ga_1[['start_date_x']] = [ self.stamp2date(i) for i in list(self.data_ga_1.start_date_x)]
        self.data_ga_1[['start_date_y']] = [ self.stamp2date(i) for i in list(self.data_ga_1.start_date_y)]

        delta =np.array(list(self.data_ga_1.start_date_y))-np.array(list(self.data_ga_1.start_date_x))
        self.data_ga_1['diff_day'] = [delta[i].days for i in range(len(list(self.data_ga_1.start_date_x)))]
        self.data_ga_2 = self.data_ga_1[np.array(list(self.data_ga_1.diff_day))>0]

        closed_status = ['Closed1','Closed2','Closed4','Closed5','Return1','Return2','Return4','Return5']
        search_status = ['Search','Search1','Search2']
        cpt_status = ['CPT1','CPT2']
        found_status = ['Found1','Found2','Found3']
        fresh_status =['Fresh']
        payoff_status = ['Payoff','Closed3','Return3']

        closing=[]
        searching=[]
        cpting=[]
        founding=[]
        freshing=[]
        payoffing=[]
        for i in list(self.data_ga_2.status):
            if i in closed_status:
                closing.append(1)
            else:
                closing.append(0)

            if i in search_status:
                searching.append(1)
            else:
                searching.append(0)

            if i in cpt_status:
                cpting.append(1)
            else:
                cpting.append(0)

            if i in found_status:
                founding.append(1)
            else:
                founding.append(0)

            if i in fresh_status:
                freshing.append(1)
            else:
                freshing.append(0)


            if i in payoff_status:
                payoffing.append(1)
            else:
                payoffing.append(0)

        self.data_ga_2['closed'] =closing
        self.data_ga_2['search'] =searching
        self.data_ga_2['cpt'] =cpting
        self.data_ga_2['found'] =founding
        self.data_ga_2['fresh'] =freshing
        self.data_ga_2['payoff'] =payoffing

        #self.data_ga_2.to_csv('my_temp_data/data_ga.csv')

        global data_ga_21
        data_ga_21 = self.data_ga_2
        #data_ga_21 = pd.read_csv('my_temp_data/data_ga.csv')

        #pysqldf = lambda q: sqldf(q, globals())

        q1 = '''select case_no_y, count(case_no_x) as hs,sum(case_money) as totalcasemoney,
                                 sum(repay_allmoney_yes) as totalrepay,max(case_money) as maxcasemoney,
                                 sum(seek_apply_count) as totalseekapply,
                                 sum(seek_count) as totalseek,
                                 sum(closed) as closed,
                                 sum(search) as search,
                                 sum(cpt) as cpt,
                                 sum(found) as found,
                                 sum(fresh) as fresh,
                                 sum(payoff) as payoff,
                                 hkje,
                                 waje
                                 from data_ga_21 
                                 group by case_no_y'''

        self.data_ga_3 = sqldf(q1)

        
        # if 'data_ga_3b' not in globals():
        #self.data_ga_3.to_csv('my_temp_data/data_ga_3.csv')
        global data_ga_3b1
        #data_ga_3b1 = pd.read_csv('my_temp_data/data_ga_3.csv')
        data_ga_3b1 = self.data_ga_3

        # if 'data_casea' not in globals():
        #self.data_cases.to_csv('my_temp_data/data_cases.csv')
        global data_casea1
        #data_casea1 = pd.read_csv('my_temp_data/data_cases.csv')
        data_casea1 = elf.data_cases

        q2 ='''
        select a.case_no as case_no,a.id_no as id_no,a.department_top_name as department_top_name,a.city as city,a.age as age,a.sexual as sexual,a.case_money as case_money,a.start_date as start_date,a.repay_allmoney_yes as repay_allmoney_yes,
        b.hs as hs,b.totalcasemoney as totalcasemoney,b.totalrepay as totalrepay,b.maxcasemoney as maxcasemoney,b.totalseekapply as totalseekapply,b.totalseek as totalseek,b.closed as closed,b.search as search,b.cpt as cpt,b.found as found,b.fresh as fresh,b.payoff as payoff
        from data_casea1 a  
        left join data_ga_3b1 b
        on a.case_no = b.case_no_y
        ''' 

        self.data_ga_fina =  sqldf(q2)

        self.data_ga_fina_1 = self.data_ga_fina.fillna(0)

        # phone table

        my_pattern_1 = re.compile(r'^\d{7,15}$')
        my_phone1 = []
        for i in range(len(phone_data.phone)):
            try:
                my_phone1.append(re.search(my_pattern_1,phone_data.phone[i]).group())
            except:
                my_phone1.append(None)

        phone_data['phone1'] =my_phone1 


        self.my_data_phone_2 = phone_data.drop_duplicates()


        temp_flag_self = [1 if list(self.my_data_phone_2.relation_ship)[i] == '本人' else 0 for i in range(len(list(self.my_data_phone_2.relation_ship)))]
        self.my_data_phone_2['flag_self'] = temp_flag_self
        self.my_data_phone_2['flag_self'].fillna(0)
        self.my_data_phone_2['flag_other'] = list(1- np.array(list(self.my_data_phone_2.flag_self)))

        # if 'my_data_phone_2a' not in globals():
        
        #self.my_data_phone_2.to_csv('my_temp_data/my_data_phone_2.csv')
        global my_data_phone_2a1
        #my_data_phone_2a1 = pd.read_csv('my_temp_data/my_data_phone_2.csv')
        my_data_phone_2a1 = self.my_data_phone_2

        q3 = '''select case_no,id_no,count(phone) as phone_id_tot, sum(flag_self) as phone_self_tot,sum(flag_other) as phone_other_tot
        from my_data_phone_2a1
        group by id_no
        '''
        self.data_phone_fina =  sqldf(q3)


        #address table
        # if 'my_data_progress_1a' not in globals():
        #self.my_data_address_1.to_csv('my_temp_data/my_data_address_1.csv')
        global my_data_progress_1a1
        my_data_progress_1a1 = address_data
        
        q4 = '''select case_no,id_no,count(address) as ad_tot from my_data_progress_1a1 group by id_no'''

        self.data_address_fina =  sqldf(q4)

        # progress
        self.data_progress_2 = progress_data[np.array(list(progress_data.progress_type)) == '1']
        list_contact = pd.read_excel('data/list_contact.xlsx', sheet_name='Sheet1', header=0)
        self.data_progress_2[['action_code']].fillna(np.nan)

        self.data_progress_3 = pd.merge(self.data_progress_2,list_contact,how='left', on='action_code', left_on=None, right_on=None,
              left_index=False, right_index=False, sort=False,
              suffixes=('_x', '_y'), copy=True, indicator=False)


        patternA = '接|说|沟通|表示|言|称|告|承诺|问|来电'
        patternB = u"无人接听|无法接通|留言|拒接"

        my_flag_operate_cont=[]
        for i in list(self.data_progress_3.operate):
            try:
                a = re.search(patternA,i).group()
            except:
                a = None

            try:
                b = re.search(patternB,i).group()
            except:
                b = None

            if a !=None and b == None:
                my_flag_operate_cont.append(1)
            elif b != None:
                my_flag_operate_cont.append(0)
            else:
                my_flag_operate_cont.append(0)

        self.data_progress_3['flag_operate_cont'] = my_flag_operate_cont


        self.data_progress_3['sum_flag'] = np.array(list(self.data_progress_3.flag_operate_cont)) + np.array(list(self.data_progress_3.flag_contact))

        self.data_progress_4 = self.data_progress_3[np.array(list(self.data_progress_3.sum_flag))>0]

        self.data_progress_5 = pd.merge(self.data_progress_4,data_seek[['case_no','create_time']],how='left',on='case_no')
       

        self.data_progress_5[['create_date']] = [ self.stamp2date(i) for i in list(self.data_progress_5.create_date)]
        self.data_progress_5[['create_time']] = [ self.stamp2date(i) for i in list(self.data_progress_5.create_time)]
        delt1 = np.array(list(self.data_progress_5.create_date)) - np.array(list(self.data_progress_5.create_time))
        self.data_progress_5['dif_create_date'] = list(delt1)
        self.data_progress_5['diff_day'] = [delt1[i].days for i in range(len(list(self.data_progress_5.dif_create_date)))]


        self.data_progress_6_0 = self.data_progress_5[np.array(list(self.data_progress_5.diff_day))>=-7]
        self.data_progress_6 = self.data_progress_6_0[np.array(list(self.data_progress_6_0.diff_day))<=0]

        # if 'data_progress_6a' not in globals():
        #self.data_progress_6.to_csv('my_temp_data/data_progress_6.csv')
        global data_progress_6a1
        #data_progress_6a1 = pd.read_csv('my_temp_data/data_progress_6.csv')
        data_progress_6a1 = self.data_progress_6

        q5 = '''
        select case_no,sum(sum_flag) as flag_contact_seek7day from data_progress_6a1 group by case_no
        '''
        self.data_progress_fina =  sqldf(q5)
        self.data_progress_fina = self.data_progress_fina.fillna(0)

        #merge
        
        self.my_data_all_0 = pd.merge(self.data0_fina,self.data_ga_fina_1,how='left',on=['case_no','id_no'])
        self.my_data_all_1 = pd.merge(self.my_data_all_0,self.data_phone_fina,how='left',on=['case_no','id_no'])
        self.my_data_all_2 = pd.merge(self.my_data_all_1,self.data_address_fina,how='left',on=['case_no','id_no'])
        self.my_data_all_3 = pd.merge(self.my_data_all_2,self.data_progress_fina,how='left',on='case_no')
        self.my_data_all_3.fillna(0)


        self.test_kehu = list(self.my_data_all_3.kehu)
        self.test_case_no = list(self.my_data_all_3.case_no)
        self.test_id_no = list(self.my_data_all_3.id_no)
        self.test_department_top_name= list(self.my_data_all_3.department_top_name)
        self.test_city = list(self.my_data_all_3.city)
        self.test_age = list(self.my_data_all_3.age)
        self.test_sexual = list(self.my_data_all_3.sexual)
        self.test_case_money = list(self.my_data_all_3.case_money)  
        self.test_hs = list(self.my_data_all_3.hs)
        self.test_totalcasemoney = list(self.my_data_all_3.totalcasemoney)
        self.test_totalrepay = list(self.my_data_all_3.totalrepay)
        self.test_maxcasemoney = list(self.my_data_all_3.maxcasemoney)
        self.test_totalseekapply = list(self.my_data_all_3.totalseekapply)
        self.test_totalseek = list(self.my_data_all_3.totalseek)
        self.test_closed = list(self.my_data_all_3.closed)
        self.test_search = list(self.my_data_all_3.search)
        self.test_cpt = list(self.my_data_all_3.cpt)
        self.test_found = list(self.my_data_all_3.found)
        self.test_fresh = list(self.my_data_all_3.fresh)
        self.test_payoff = list(self.my_data_all_3.payoff)
        self.test_phone_id_tot = list(self.my_data_all_3.phone_id_tot)
        self.test_phone_self_tot = list(self.my_data_all_3.phone_self_tot)
        self.test_phone_other_tot = list(self.my_data_all_3.phone_other_tot)
         #24,ga_same1
        self.test_ad_tot = list(self.my_data_all_3.ad_tot)
        #self.test_con_ad_tot = list(self.my_data_all_3.con_ad_tot)
        #27,seekornot
        self.flag_contact_seek7day = list(self.my_data_all_3.flag_contact_seek7day)
        self.handletime1 = list(self.my_data_all_3.handle_time)
        self.my_hkje = list(self.my_data_all_3.hkje)
        self.my_waje = list(self.my_data_all_3.waje)
        self.hsl = list(np.array(self.my_hkje)/(np.array(self.my_waje)+1))

        if data_type == 'train':
            self.my_train_target = [1 if hsl > target_index else 0 for hsl in self.hsl]
            self.my_seek_cuji = list(list(self.my_data_all_3.seek_progress))

            patternC = u"提请搜索中心协助|Processing|Return|搜索协助|处理中|ss|nbsp|TQSS|状态修改"
            self.my_temp_cuiji = [str1.split(";") for str1 in  self.my_seek_cuji]

            my_flag_seek_cuji=[]
            for my_list in list(self.my_temp_cuiji):
                temp_list = []
                for j in my_list:
                    try:
                        c = re.search(patternC,j).group()
                    except:
                        c = None

                    if c ==None:
                    	temp_list.append(1)
                    else:
                    	temp_list.append(0)
                if np.sum(np.array(temp_list)) >= 1:
                    my_flag_seek_cuji.append(1)
                else:
                	my_flag_seek_cuji.append(0)

            self.train_xgb_targets = my_flag_seek_cuji


        elif data_type == 'test':
        	pass


        if data_type == 'train':

	        #last data
            self.model0_data = pd.DataFrame({'kehu':self.test_kehu,'case_no':self.test_case_no,'id_no':self.test_id_no,
	        	'department_top_name':self.test_department_top_name,'city':self.test_city,
	            'age':self.test_age,'sexual':self.test_sexual,'case_money':self.test_case_money,'hs':self.test_hs,
	            'totalcasemoney':self.test_totalcasemoney,'totalrepay':self.test_totalrepay,'maxcasemoney':self.test_maxcasemoney,
	            'totalseekapply':self.test_totalseekapply,'totalseek':self.test_totalseek,'closed':self.test_closed,
	            'search':self.test_search,'cpt':self.test_cpt,'found':self.test_found,'fresh':self.test_fresh,
	            'payoff':self.test_payoff,'phone_id_tot':self.test_phone_id_tot,'phone_self_tot':self.test_phone_self_tot,
	            'phone_other_tot': self.test_phone_other_tot,'ad_tot':self.test_ad_tot,
	            'contact_seek7day':self.flag_contact_seek7day,'handletime1':self.handletime1,
	            'hk_traget':self.my_train_target 
	            })

            self.model1_data = pd.DataFrame({'kehu':self.test_kehu,'case_no':self.test_case_no,'id_no':self.test_id_no,
	        	'department_top_name':self.test_department_top_name,'city':self.test_city,
	            'age':self.test_age,'sexual':self.test_sexual,'case_money':self.test_case_money,'hs':self.test_hs,
	            'totalcasemoney':self.test_totalcasemoney,'totalrepay':self.test_totalrepay,'maxcasemoney':self.test_maxcasemoney,
	            'totalseekapply':self.test_totalseekapply,'totalseek':self.test_totalseek,'closed':self.test_closed,
	            'search':self.test_search,'cpt':self.test_cpt,'found':self.test_found,'fresh':self.test_fresh,
	            'payoff':self.test_payoff,'phone_id_tot':self.test_phone_id_tot,'phone_self_tot':self.test_phone_self_tot,
	            'phone_other_tot': self.test_phone_other_tot,'ad_tot':self.test_ad_tot,
	            'contact_seek7day':self.flag_contact_seek7day,'handletime1':self.handletime1,
	            'seek_traget':self.train_xgb_targets 
	            })
        if data_type == 'test':
	    	#last data
            self.model0_data = pd.DataFrame({'kehu':self.test_kehu,'case_no':self.test_case_no,'id_no':self.test_id_no,
	        	'department_top_name':self.test_department_top_name,'city':self.test_city,
	            'age':self.test_age,'sexual':self.test_sexual,'case_money':self.test_case_money,'hs':self.test_hs,
	            'totalcasemoney':self.test_totalcasemoney,'totalrepay':self.test_totalrepay,'maxcasemoney':self.test_maxcasemoney,
	            'totalseekapply':self.test_totalseekapply,'totalseek':self.test_totalseek,'closed':self.test_closed,
	            'search':self.test_search,'cpt':self.test_cpt,'found':self.test_found,'fresh':self.test_fresh,
	            'payoff':self.test_payoff,'phone_id_tot':self.test_phone_id_tot,'phone_self_tot':self.test_phone_self_tot,
	            'phone_other_tot': self.test_phone_other_tot,'ad_tot':self.test_ad_tot,
	            'contact_seek7day':self.flag_contact_seek7day,'handletime1':self.handletime1
	            })

            self.model1_data = pd.DataFrame({'kehu':self.test_kehu,'case_no':self.test_case_no,'id_no':self.test_id_no,
	        	'department_top_name':self.test_department_top_name,'city':self.test_city,
	            'age':self.test_age,'sexual':self.test_sexual,'case_money':self.test_case_money,'hs':self.test_hs,
	            'totalcasemoney':self.test_totalcasemoney,'totalrepay':self.test_totalrepay,'maxcasemoney':self.test_maxcasemoney,
	            'totalseekapply':self.test_totalseekapply,'totalseek':self.test_totalseek,'closed':self.test_closed,
	            'search':self.test_search,'cpt':self.test_cpt,'found':self.test_found,'fresh':self.test_fresh,
	            'payoff':self.test_payoff,'phone_id_tot':self.test_phone_id_tot,'phone_self_tot':self.test_phone_self_tot,
	            'phone_other_tot': self.test_phone_other_tot,'ad_tot':self.test_ad_tot,
	            'contact_seek7day':self.flag_contact_seek7day,'handletime1':self.handletime1
	            })


    
        #dummy var
        self.model0_data = self.model0_data.fillna(0)
        self.model0_data_0 = pd.get_dummies(self.model0_data,prefix=None,prefix_sep="_",dummy_na=False,columns=['department_top_name','city','sexual','handletime1'],drop_first=True)

        self.model1_data = self.model1_data.fillna(0)
        self.model1_data_0 = pd.get_dummies(self.model1_data,prefix=None,prefix_sep="_",dummy_na=False,columns=['department_top_name','city','sexual','handletime1'],drop_first=True)

        data_last = {'data_model0': self.model0_data_0,'data_model1':self.model1_data_0}
        return data_last
        
  


    def threshold_bset(self,fpr,tpr,threshold):
        '''
        =================================================
        Youden index = (tpr+(1-fpr)-1)
        To use to Selecting the optimal threshold
        =================================================

        '''
        RightIndex = np.array(tpr)+(1-np.array(fpr))-1
        index = np.argmax(RightIndex)
        best_fpr = fpr[index]
        best_tpr = tpr[index]
        best_thr = threshold[index]
        return best_thr

    def predict_clf(self,pre,thr):
        '''
        =================================================
        Classification prediction with optimal threshold
        =================================================
        '''
        pre_clf = np.array(pre)>thr
        return pre_clf


    def gridxgbt(self,path_file,train):
        '''
        ================================================================
        The model train for stacking xgboost and lightgbm for xinxiu 
        ================================================================
        Arguments:

        		path_file: File which your model should save.
        		train: Train data include target and other columns.

        '''
        self.kehu = list(train.kehu)[0]
        self.train_targets = list(train.hk_traget)
        train.drop(['kehu','case_no','id_no'],axis=1,inplace=True)
        if not os.path.exists(path_file):
        	os.makedirs(path_file) 
        ##first model
        clf_xgb = XGBClassifier(learning_rate =0.1,n_estimators=1000,max_depth=5,min_child_weight=1,gamma=20,subsample=0.8,colsample_bytree=0.8,objective= 'binary:logistic',nthread=4,scale_pos_weight=1,seed=27)
        clf_lgb = lgb.LGBMClassifier(boosting_type='gbdt', num_leaves=31,\
        	max_depth=-1, learning_rate=0.1, n_estimators=10, max_bin=255, \
        	subsample_for_bin=2000, objective=None, min_split_gain=0.0, min_child_weight=0.001, \
        	min_child_samples=20, subsample=1.0, subsample_freq=1, colsample_bytree=1.0,\
        	reg_alpha=0.01, reg_lambda=0.01, random_state=None, n_jobs=-1, silent=True)

        #stacking
        eclf = VotingClassifier(estimators=[('lgb', clf_lgb), ('xgb', clf_xgb)],voting='soft')
        #param opt found
        params = {'lgb__num_leaves': range(40, 130,30),'lgb__learning_rate':[0.1,0.2,0.01],'lgb__n_estimators':range(40,100,30),'xgb__max_depth':range(10,100,20),'xgb__learning_rate':[0.1,0.2,0.01],'xgb__n_estimators':range(10,100,40)}
        grid = GridSearchCV(estimator=eclf, param_grid=params, cv=5)
        grid_fit = grid.fit(train,self.train_targets)
        #save_model
        my_path = path_file + str(self.my_kehu) + 'stack.model'
        joblib.dump(grid_fit,my_path)

        #index save
        grid_clf_prob = grid_fit.predict_proba(train)
        fpr1, tpr1, threshold = metrics.roc_curve(np.array(self.train_targets), grid_clf_prob[:,1])
        auc1 = metrics.auc(fpr1, tpr1)
        best_thr = pd.DataFrame({'best_thr':list(self.threshold_bset(fpr1,tpr1,threshold))})
        best_thr.to_csv(self.path_file + str(self.my_kehu) + 'stack.csv')

        #save_col_names
        my_col_names = pd.DataFrame({'my_col':list(train.columns)})
        my_col_names.to_csv(path_file + str(self.my_kehu) + 'colname.csv')
		

        print('信修回款预测训练模型保存成功,请在' + self.path_file + '查看！')


    def xgbt(self,path_file,train_xgb):
        '''
        =================================================
        The model train xgboost for xinxiu success!
        =================================================
        Arguments: same as gridxgbt()

        '''

        self.kehu = list(train_xgb.kehu)[0]
        self.train_xgb_targets = list(train_xgb.seek_traget)
        train_xgb.drop(['kehu','case_no','id_no'],axis=1,inplace=True)
        if not os.path.exists(path_file):
        	os.makedirs(path_file) 

        clf_xgb = XGBClassifier(learning_rate =0.1,n_estimators=1000,max_depth=5,\
        	min_child_weight=1,gamma=20,subsample=0.8,colsample_bytree=0.8,objective= 'binary:logistic',\
        	nthread=4,scale_pos_weight=1,seed=27)
        xgb_sucess = clf_xgb.fit(train_xgb,self.train_xgb_targets)
        #save_model
        my_path = self.path_file + str(self.my_kehu) + 'xgb_sucess.model'
        joblib.dump(xgb_sucess,my_path)

        #index save
        xgb_sucess_clf_prob = xgb_sucess.predict_proba(train_xgb)
        fpr1, tpr1, threshold = metrics.roc_curve(np.array(self.train_xgb_targets), xgb_sucess_clf_prob[:,1])
        auc1 = metrics.auc(fpr1, tpr1)
        best_thr = pd.DataFrame({'best_thr':list(self.threshold_bset(fpr1,tpr1,threshold))})
        best_thr.to_csv(self.path_file + str(self.my_kehu) + 'xgb_sucess.csv')

        print('信修是否成功返回结果预测训练模型保存成功,请在' + self.path_file + '查看！')




    def predictm(self,path_model,path_thr,path_cols,my_test_df):
        '''
        ==============================================
        Method to test data predict 
        ==============================================
        Arguments:
        		path_model: Where is the model saved.
        		path_thr:   Where is the best_thr saved.
        		path_cols:  Where is the model columns saved.
        		my_test_df: Test data a data frame.
        '''


        self.my_kehu =list(my_test_df.kehu)[0]
        self.case_no = list(my_test_df.case_no)
        my_test_df.drop(['kehu','case_no','id_no'],axis=1,inplace=True)

        #test_data_pro
        my_cols = pd.read_csv(path_cols)
        my_col_list = list(my_cols.my_col)

        for test_col in my_col_list:
            if test_col not in list(my_test_df.columns):
                my_test_df[test_col] = [0]*my_test_df.shape[0]
            else:
                pass
        my_test_df_0 = my_test_df[my_col_list]  

        #load_model
        ensemble_m = joblib.load(path_model)
        best_thr0 = pd.read_csv(path_thr)
        bset_thr = list(best_thr0['best_thr'])[0]
        #predict
        grid_clf_prob = ensemble_m.predict_proba(my_test_df_0)
        grid_pre_clf = predict_clf(grid_clf_prob[:,1],best_thr) 

        #predict result
        grid_prob_clf1 = list(grid_clf_prob[:,1])
        grid_pre_clf1 = [np.int(grid_pre_clf[i]) for i in range(len(grid_pre_clf))]

        data_result = {'case_no':self.case_no,'prob':grid_prob_clf1,'pred':grid_pre_clf1}

        return data_result

