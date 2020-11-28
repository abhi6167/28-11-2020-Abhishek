# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 16:41:01 2020

@author: User
"""

import pandas as pd
import sys
import re
import configparser
import json

class BMICaliculator:
    
    def __init__(self,json_data,BMITable):
        """
        Intializing the data
        
        @args
        json_data:Conatins the input data
        BMITable:It contains the input bmi table
        
        """
        self.json_data = json_data
        self.BMITable  = BMITable

    def func_CreateDataframe(self):
        """
        Creates the data frame from the json dict
        Created BMI Table
        @returns:
            The Input and bmit table dataframe
        """
        try:
            df_Inputdata = pd.DataFrame.from_dict(self.json_data)
            df_BMITable = pd.DataFrame(self.BMITable)
            return df_Inputdata,df_BMITable
        except Exception as e:
            print("input is not correct")
            sys.exit(1)



    def func_Create_BMI_Index(self,df,power,height_colname,weight_colname):
        """
        Creates a new column and caliculates the BMI for each person
        
        @args
        df    -- Input dataframe.
        power -- parameter sq the meter
        
        output:
            BMI will be caliculated with new column in the existing Dataframe
        """
        try:
            df["HeightInMtrs (m2)"] = (df[height_colname]/100)**power
            #code to caliculate the BMI
            df["BMI (kg/m2)"] = df[weight_colname]/df["HeightInMtrs (m2)"]
        except Exception as e:
            print(e)
            print("Invalid data has been entered")
            sys.exit(1)
        return df



    def func_AddCategory_HealthRisk(self,df,lower_val,upper_val,health_risk,Category):
        """
        This function adds the 2 new columns Health Risk and Category
        
        @args
        df -- This is the inpu data frame
        lower_val -- This is the lower bound
        upper_val -- This is the upper bound
        health_risk -- Health risk take from the BMI Table
        Category -- Category is taken the from BMI Table
        
        Output:
            2 new columns and there health risk and category is added based on the weight
        """
        if type(upper_val) != str:
            counts = df.index[(df["BMI (kg/m2)"] > lower_val) & (df["BMI (kg/m2)"] < upper_val)]
            df.loc[counts,"Health Risk"] = health_risk
            df.loc[counts,"Category"] = Category
            return df
        elif ((type(upper_val)) == str) and (str(upper_val) == "below"):
            counts = df.index[(df["BMI (kg/m2)"] < lower_val)]
            df.loc[counts,"Health Risk"] = health_risk
            df.loc[counts,"Category"] = Category
            return df
        else:
            counts = df.index[(df["BMI (kg/m2)"] > lower_val)]
            df.loc[counts,"Health Risk"] = health_risk
            df.loc[counts,"Category"] = Category
            return df
    
if __name__ == "__main__":
    
    read_config = configparser.ConfigParser()
    read_config.read("C:\\Users\\User\\Desktop\\interview\\Configurations.ini")
    
    option_values = read_config.get("Input", "inputData")
    option_value_list = json.loads(option_values)
    
    #Reading Deatils Related to the BMI Table
    option_values = read_config.get("BMITable", "BMI_Table")
    BMITable_list = json.loads(option_values)
    
    #Intializing the Category
    cat_val = read_config.get("BMITable", "BMI_Cat")
    Category_col_name = cat_val
    
    #initalizing the BI Range
    bmirange = read_config.get("BMITable", "bmirange")
    bmirange = bmirange
    
    #initalizing the Health Risk
    Health_risk = read_config.get("BMITable", "Health_risk")
    Health_risk = Health_risk
    
    #Reading the input data from the configaration.ini file
    json_data = option_value_list
    BMI_Table = BMITable_list

    #Creating the object for the constructor
    BMI_caliculator = BMICaliculator(json_data,BMI_Table)
    df_inpdata,df_bmitable = BMI_caliculator.func_CreateDataframe()
    
    #Getting the power and heigth column name    
    power = int(read_config.get("UserConfig", "Power"))
    height_colname = read_config.get("Input", "Heightcm")
    weight_colname = read_config.get("Input", "weighhtKg")
    
    df_inpdata = BMI_caliculator.func_Create_BMI_Index(df_inpdata,power,height_colname,weight_colname)
    
    caltegory_list = list(df_bmitable[Category_col_name].unique())

    for cats in caltegory_list:
        df = df_bmitable[df_bmitable[Category_col_name] == cats][[bmirange,Health_risk]]
        if df.shape[0] == 1:
            if df[bmirange].str.contains("above").tolist()[0]:
                lower_bound = re.findall('[0-9\.]+',df[bmirange].tolist()[0])
                df_inpdata = BMI_caliculator.func_AddCategory_HealthRisk(df_inpdata,float(lower_bound[0]),"above",df[Health_risk].tolist()[0],cats)
            elif df[bmirange].str.contains("below").tolist()[0]:
                lower_bound = re.findall('[0-9\.]+',df[bmirange].tolist()[0])
                df_inpdata = BMI_caliculator.func_AddCategory_HealthRisk(df_inpdata,float(lower_bound[0]),"below",df[Health_risk].tolist()[0],cats)
            else:
                lower_bound = re.findall('[-]+',df[bmirange].tolist()[0])
                cond = df[bmirange].tolist()[0].split(lower_bound[0])
                df_inpdata = BMI_caliculator.func_AddCategory_HealthRisk(df_inpdata,float(cond[0]),float(cond[1]),df[Health_risk].tolist()[0],cats)
        else:
            print("BMI Table is invalid bcz Multiple range is present for one category")
            sys.exit(1)
    
    #Specify the category to get the count of that kind
    category = read_config.get("UserConfig", "category")
    if category == "ALL":
        print(df_inpdata.groupby([Category_col_name])[Category_col_name].count())
    else:
        given_Category = df_inpdata[df_inpdata["Category"] == category]["Category"].count()
        print(f'The total number of people of given category {category} is {given_Category}')



