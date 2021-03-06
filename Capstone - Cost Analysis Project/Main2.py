#!/usr/bin/env python
# coding: utf-8


import pandas as pd


# wd='UMich_Sample_Data/'
# file=(wd+'UMich-SampleData-PicksMadePNW-Jan3.csv')
# file1=()

file = pd.read_json('konbert-export-af13702aff904.json')

file.to_csv()

#file = 'UMich-SampleData-PicksMadePNW-Jan3.csv'



def combine(row):
    '''
    function that combines the product name, picktime and quantity into a list that is then put in a column
    '''
    pname=row['PRODUCTNAME']
    time=row['PICKCOMPLETETIME']
    qty=row['QTY']
    return [pname, time, qty]


def get_package_start_time(df):
    #trying to gather the box in time 
    
    '''
    takes in: a dataframe
    returns:  a dictionary of boxbarcodes and the start time
    
    '''
    
    start=df.groupby('BOXBARCODE')['PICKORDERSTARTTIME'].apply(list)
    start=start.reset_index()
    start['PICKORDERSTARTTIME']=start['PICKORDERSTARTTIME'].apply(lambda x: x[0])
    start['PICKORDERSTARTTIME']=pd.to_datetime(start['PICKORDERSTARTTIME'])

    start=start.set_index('BOXBARCODE')
    start=start.to_dict()
    #df=pd.from_dict(start)
        
    return start['PICKORDERSTARTTIME']
  

# returns dictionary with box ID's as keys and start times as values
#THIS IS NEEDED IN FINDING TIME DIFFERENCE BETWEEN TIME OF FIRST ITEM PACKED



def get_time_diff(boxname, lst,box_start_times):
    
    '''
    takes in: a list containing lists containing product name, time of stamp, and quantity
    
    returns: [Product name, the time difference, picktime]
    
    '''
    
    output_lst=[]  

    
    #sort product,picktime by picktime within list
    lst=sorted(lst, key=lambda x: pd.Timestamp(x[1]))
    
    #turning l=[(p1,t1),(p2,t2),(p3,t3)]
    #into new_l=[(p1,t0-t1),(p2,t1-t2),(p3,t2-t3)]
    
    
    for i in range(len(lst)):        
        # if its the first instance in the list, then we need to use the "pack box" or whatever it's called as our 
        #start time (our t0) in order to create a difference
        qty=lst[i][2]
        t1=pd.Timestamp(lst[i][1])

        if i==0:
            t0=box_start_times[boxname]
            t0=pd.Timestamp(t0)
            time_delta=t1-t0
            time_delta=time_delta/qty
            
            #time_delta=None  
            
        else:
            t0=lst[i-1][1]
            t0=pd.Timestamp(t0)
            time_delta=t1-t0
            time_delta=time_delta/qty

        output_lst.append([lst[i][0],time_delta, t1])
    return output_lst
    



def mean(lst):
    summ=0
    count=0
    for num in lst:
        if num==None:
            pass
        else:
            num=num.total_seconds()
            summ+=num
            count+=1
    return summ/count


# STILL NEED TO INCORPORATE INSTANCES OF 0 BECAUSE IN THE DELTA CALCULATIONS, THEY ARE IMPORTANT


def main2(file):
    #import pandas as pd
    
    #~~~~~~~~~~~~~(MAY NEED TO ALTER HERE)~~~~~~~~~~~~~~~
    #loading file from csv into pandas 
    #b=pd.read_csv(file)
    b = file
    #~~~~~~~~~~~~~(MAY NEED TO ALTER HERE)~~~~~~~~~~~~~~~
    
    
    ###PREPROCESSING
    
    #Removing instances where item quantity is 0
    b=b[b['QTY']!=0]
    
    #getting columns we need
    df=b[['PICKCOMPLETETIME','BOXBARCODE','PRODUCTNAME','QTY']]
    
    #concatenating all relevant columns into a single list in a column
    df['concat']=df.apply(lambda x: combine(x), axis=1)
    
    #removing all other columns except barboxcode and concat
    df=df[['BOXBARCODE','concat']]

    #grouping by boxbarcode and cooncatenating all the items in 'concat' into a list so you have lsits of products
    df=df.groupby('BOXBARCODE')['concat'].apply(list)
    df=df.reset_index(name='[Product, PickTime, QTY]')
    
    
    
    #MAIN ANALYSIS
    #returns dictionary with box ID's as keys and start times as values
    box_start_times=get_package_start_time(b)

    y=df.apply(lambda x:get_time_diff(x['BOXBARCODE'], x['[Product, PickTime, QTY]'],box_start_times), axis=1)
    
    #turn into dataframe where each row is an instance
    reformatted=[]
    for biglst in y:
        for lst in biglst:
            reformatted.append(lst)
    output_df= pd.DataFrame(reformatted, columns=['ProductName', 'TimeDelta', 'PickTime'])

    #Creates a dicitonary where keys are product names and values are list of product times
    
    
    
    print(output_df)
    

main2(file)





