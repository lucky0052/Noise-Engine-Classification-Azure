# -*- coding: utf-8 -*-
"""Engine Noise Classification

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ZhA0OxmlKN0S1I_MVjfAce8vRp9wp_1S
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.pyplot import rcParams

"""**importing data**"""

df = pd.read_csv('Hackathon_Train.csv',sep=';',index_col=0)
df.head(5)

"""# **Exploratory Data Analysis**"""

df.shape

# drop duplicate column and unnecessary column

df.drop(columns=['brand','spec','model','make_country_cqa','model_drive_cqa_1','model_mpg_city'],inplace=True)

df.info()

# drop duplicate
df.drop_duplicates(keep='first',inplace=True)

df.shape

# No. of Null value in each column

plt.figure(figsize=(18,6))
sns.barplot(x=[col for col in df.columns],y=df.isna().sum()).set(title='No. of NA\'s column in each column')
plt.xticks(rotation=90)
plt.xlabel('column index')

((df.isna().sum())/ df.shape[0] )*100

# drop all the null values in the dataset

df.dropna(inplace=True)

df.shape

# No. of value which are -ve in each column

plt.figure(figsize=(14,6))
plt.xticks(rotation=90)
sns.barplot(x=[col for col in df.columns if df[col].dtypes != 'object'], y=[len(df[df[feature] < 0]) for feature in df.columns if df[feature].dtypes != 'object']).set(title='Total Negative no. in each column')

# drop all the negative values

df.drop(index=df[df['year']  < 0].index,inplace=True)
df.drop(index=df[df['dB_at_80kmh']  < 0].index,inplace=True)
df.drop(index=df[df['dB_at_50kmh']  < 0].index,inplace=True)
df.drop(index=df[df['dB_at_120kmh']  < 0].index,inplace=True)
df.drop(index=df[df['model_weight_lbs_cqa']  < 0].index,inplace=True)

"""# **Feature Engineering**"""

df['model_top_speed_kph_cqa'] = df['model_top_speed_kph_cqa'].apply(lambda x : int(x.replace('+','')))

df['model_engine_valves_cqa'].replace({'Eighty':80,'Twenty':20,'Six':6,'Thirty':30,'Eight':8},inplace=True)

df['model_engine_valves_cqa'] = df['model_engine_valves_cqa'].apply(lambda x : int(x))

df[['model_engine_bore_mm_cqa','model_engine_bore_in_cqa']]

df.shape

from datetime import date

current_year = date.today().year

df['year'] = df['year'].apply(lambda x : current_year - x)

# Pull out the feature where data type is object

object_feature = [feature for feature in df.columns if df[feature].dtypes == 'object']

object_df = df[object_feature]

# convert the label into numeric

from sklearn.preprocessing import LabelEncoder


le = LabelEncoder()
obj_feature1 = df[object_feature].apply(le.fit_transform)
obj_feature1

# Pull out the numeric columns

numeric_cols = [feature for feature in df.columns if df[feature].dtypes != 'object']
numeric_col = df[numeric_cols]

df[numeric_cols].describe()

new_df = obj_feature1.join(numeric_col,on='Index')
new_df.shape

new_df

# drop column due to highly correlated

df.drop(columns=['dB_at_100kmh','model_engine_bore_in_cqa','model_engine_bore_mm_cqa'],inplace=True)

"""**Test dataset**

"""

test_df = pd.read_csv('Hackathon_Test.csv',sep=';',index_col=0)
test_df

test_df.dropna(inplace=True)

test_features = test_df[['model_body_cqa', 'model_engine_type_cqa', 'model_engine_power',
       'model_engine_torque', 'dB_at_80kmh', 'model_top_speed_kph_cqa',
       'model_fuel_cap_l_cqa', 'model_engine_valves_cqa',
       'model_weight_lbs_cqa', 'model_length_in_cqa',
       'model_width_in_cqa', 'model_wheelbase_in_cqa',
       'model_mpg_hwy_cqa', 'model_mpg_mixed_cqa', 'model_fuel_cap_g_cqa']]
test_features

test_features.isna().sum()

obj_feature1 = [col for col in test_features.columns if test_features[col].dtype == 'object']
obj_feature_new = df[obj_feature1]

num_feature1 = [col for col in test_features.columns if test_features[col].dtype != 'object']
num_feature_df = df[num_feature1]

from sklearn.preprocessing import LabelEncoder

le1 = LabelEncoder()
cat_data = obj_feature_new.apply(le1.fit_transform)

test_new_df = cat_data.join(num_feature_df,on='Index')

test_new_df

from sklearn.preprocessing import StandardScaler

sc_test = StandardScaler()
sc_test_data = sc_test.fit_transform(test_new_df)

sc_test_data

X = new_df.iloc[:,:-1]
y = new_df.iloc[:,-1]


X = X.astype(int)
print(f'X.shape: {X.shape} ,y.shape: {y.shape}')

X.columns

"""# **Feature Selection**"""

# Pull out the best or important features

from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

chi2_selector = SelectKBest(chi2,k=15)
KBest = chi2_selector.fit_transform(X,y)

KBest.shape[1]

best_features = np.asarray(X.columns)[chi2_selector.get_support()]
best_features

plt.figure(figsize=(16,6))
sns.heatmap(new_df[best_features].corr(),annot=True,cmap='Blues')

chi_feature_score = pd.DataFrame({'features' : X.columns, 'Score': chi2_selector.scores_})

sns.countplot(x=df['Class'])

"""As there is class imbalance. we have to use SMOTE to avoid the class imbalance."""

get_best_feature = new_df[best_features]

X = get_best_feature
Y = y

from imblearn.over_sampling import SMOTE
from collections import Counter

sm = SMOTE(random_state=123)
X_smote,y_smote =  sm.fit_resample(X,y)
print('beofre smoting: ',Counter(y))
print('after smoting: ',Counter(y_smote))

"""# **Pre-processing**"""

# Scaling

from sklearn.preprocessing import StandardScaler

sc_x = StandardScaler()
X_sc = sc_x.fit_transform(X_smote)

"""**Model Training & Evaluation**"""

# splitting the data into train and test

from sklearn.model_selection import train_test_split

X_train,X_test,y_train,y_test = train_test_split(X_sc,y_smote,test_size=0.2,random_state=123)

from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier(n_neighbors=15,p=1,weights='distance')
knn.fit(X_train,y_train)

from sklearn.model_selection import GridSearchCV

parameters = {"n_neighbors" : [n for n in range(1,25,2)],
'p' : [1,2],
'weights' : ['uniform','distance']}


gs = GridSearchCV(knn,parameters)
gs.fit(X_train,y_train)
print(gs.best_estimator_)
print(gs.best_score_)

from sklearn.model_selection import cross_val_score,KFold


cv = KFold(n_splits=10,random_state=123,shuffle=True)

clf = cross_val_score(knn,X_train,y_train,cv=cv)
clf.mean()

# acuurcy score on training data

knn.score(X_train,y_train)

# accuracy score on test data

knn.score(X_test,y_test)

y_pred = knn.predict(X_test)

sc_test_data[0]

y_pred_test_data = knn.predict(sc_test_data[5].reshape(1,-1))
y_pred_test_data

from sklearn.metrics import accuracy_score,confusion_matrix


accuracy_score(y_test,y_pred)

confusion_matrix(y_test,y_pred)

from sklearn.metrics import classification_report

print(classification_report(y_test,y_pred))

sns.heatmap(confusion_matrix(y_test,y_pred),annot=True)

from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score

fpr, tpr, thresholds = roc_curve(y_test,y_pred)

auc = roc_auc_score(y_test, y_pred)

import matplotlib.pyplot as plt
plt.plot(fpr, tpr, color='red', label='logit model ( area  = %0.2f)'%auc)
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate or [1 - True Negative Rate]')
plt.ylabel('True Positive Rate')
print(f'fpr : {fpr.mean()}')
print(f'tpr : {tpr.mean()}')
score = roc_auc_score(y_test, y_pred)
print(f"ROC AUC: {score:.4f}")

"""**Saving the model for deplpoyment**

"""

import joblib

joblib.dump(knn,'newclassify.pkl')