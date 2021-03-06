# -*- coding: utf-8 -*-
"""machine_learning.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NSs6iY1oOlJ-S8nsrFv0Bcy2ta4FctQo

# Step 1 : We download the dataset from the server and store it in two different directores
"""

!wget https://ceb.nlm.nih.gov/proj/malaria/cell_images.zip

!unzip cell_images.zip

# Keras Utils for image processing
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Sklearn Utils for Machine Learning Models 
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier as KNN 


# Metrics to access Performance
from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix, classification_report 


# Numpy for matrix algebra
import numpy as np

# Matplotlib and Seaborn for plotting
import matplotlib.pyplot as plt
import seaborn as sns ; sns.set()



from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint

"""# Step 2 : Preprocessing the Dataset

- Here, we the ImageDataGenerator functionality from keras to create a tensore-dataset of all the images along with predictions. 
- Since the 'Parasitized' Directory occurs first, it is alloted the label '0' while Uninfected images are allotted the label'1'
"""

data_directory = '/content/cell_images'
image_width = 32
image_height = 32
m = 27558
datagen = ImageDataGenerator(rescale=1/255)  #rescale all pixel values between [-1,1]

data_generator = datagen.flow_from_directory(directory=data_directory, target_size=(image_width,image_height),
                                                   class_mode = 'binary', batch_size = m, shuffle=True, subset='training'
                                                   )

"""Now we obtain the Image Tesnor from the Datagenerator object and extract the Tensor containing data as 'X'. We reshape it to suitable for training on Machine learning algorithms."""

x_data = data_generator[0][0]
print(x_data.shape)  #expect (27558,32,32,3)
x_data = x_data.reshape(x_data.shape[0],x_data.shape[1]*x_data.shape[2]*x_data.shape[3])
print(x_data.shape)  #expect (27558,3072)

"""Similarly we apply a similar transformation for the labels 'Y'"""

y_data = data_generator[0][1]
print(y_data.shape)

# We only use 5000 Images for training and testing ; otherwise the training tends to be too slow 
x_data = x_data[:5000,:]
y_data = y_data[:5000]

"""# Step 3 : Training the Model"""

X_train, X_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.2, random_state=0)

print(len(X_train),len(X_test))

"""## Logistic Regression"""

logreg = LogisticRegression(random_state=0,max_iter=5000)
logreg.fit(X_train, y_train)
logreg_probs = logreg.predict_proba(X_test)

"""## Random Forest Classifier"""

rf = RandomForestClassifier(n_estimators =500,criterion='entropy', random_state=50)
rf.fit(X_train, y_train)
rf_probs = rf.predict_proba(X_test)

"""## Support Vector Machine

## K- Nearest Neighbour Classifier
"""

knn = KNN(n_neighbors = 2) 
knn.fit(X_train, y_train)
knn_probs = knn.predict_proba(X_test)

"""## Naive Bayes Classification"""

nb = GaussianNB()
nb.fit(X_train,y_train)
nb_probs = nb.predict_proba(X_test)

"""# Step 4 : Computing AUC and ROC values"""

# Storing the probabilities for positive outcome 

prob_vals = [logreg_probs,rf_probs, knn_probs,nb_probs]
r_probs = [0 for _ in range(len(y_test))]  # worst case probability

positive_prob_vals = [i[:,1] for i in prob_vals]

p_logreg_probs,p_rf_probs, p_knn_probs,p_nb_probs = positive_prob_vals

## Computing ROC and AUC values

r_auc = roc_auc_score(y_test,r_probs)
log_reg_auc = roc_auc_score(y_test,p_logreg_probs)
rf_auc = roc_auc_score(y_test,p_rf_probs)
knn_auc = roc_auc_score(y_test,p_knn_probs)
nb_auc = roc_auc_score(y_test,p_nb_probs)

## Print AUROC scores

print("Random (chance) Prediction : AUROC = %.3f" %(r_auc))
print('Logistic Regression : AUROC = %.3f' %(log_reg_auc))
print('Random Forest : AUROC = %.3f' %(rf_auc))
print('KNN : AUROC = %.3f' %(knn_auc))
print('Naive Bayes : AUROC = %.3f' %(nb_auc))

"""## ROC curve

The **Receiver Operating Characteristic** (ROC) curve summarises the prediction performance of a classification model at all classification thresholds. Particularly, the ROC curve plots the **False Positive Rate** (FPR) on the X-axis and the **True Positive Rate** (TPR) on the Y-axis. 

TPR (Sensitivity) = TP / (TP + FN)

FPR (1 - Specificity) = FP/ (TN + FP)
"""

## Calculate ROC curve

r_fpr, r_tpr , _ = roc_curve(y_test, r_probs)
logreg_fpr,logreg_tpr, _ = roc_curve(y_test, p_logreg_probs)
rf_fpr,rf_tpr, _ = roc_curve(y_test, p_rf_probs)
knn_fpr,knn_tpr, _ = roc_curve(y_test, p_knn_probs)
nb_fpr, nb_tpr, _ = roc_curve(y_test, p_nb_probs)

### Plot the ROC curves

fig = plt.figure(num=1,dpi=90,figsize=(6,5))
axes = fig.add_axes([0.1,0.1,0.8,0.8])

axes.plot(r_fpr,r_tpr, ls = '--', label='Random prediction (AUROC = %0.2f)' %(r_auc))

axes.plot(rf_fpr,rf_tpr, marker = ',', label='Random Forest (AUROC = %0.2f)' %(rf_auc))
axes.plot(logreg_fpr,logreg_tpr, marker = ',', label='Logistic Regression (AUROC = %0.2f)' %(log_reg_auc))
axes.plot(knn_fpr,knn_tpr, marker = ',', label='KNN (AUROC = %0.2f)' %(knn_auc))
axes.plot(nb_fpr,nb_tpr, marker = '.', label='Naive Bayes (AUROC = %0.2f)' %(nb_auc))

axes.set_xlabel('False Positive Rate')
axes.set_ylabel('True Positive Rate')
axes.set_title('Receiver Operating Characteristic (ROC) curve') 

axes.legend(fancybox=True, framealpha=1, shadow=True, borderpad=1)

plt.show()

"""# Classification Report

- Can be written to external text files
- Clearly Random Forest achieves the best classification task
"""

report_lr = classification_report(y_test,logreg.predict(X_test))
report_rf = classification_report(y_test,rf.predict(X_test))
report_nb = classification_report(y_test,nb.predict(X_test))
report_knn = classification_report(y_test,knn.predict(X_test))