# -*- coding: utf-8 -*-
"""A3_Q3_IMDB.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sa70gG5LXfrdeklna6rVgr9sBfdQfiwA
"""

#Importing necessary Libraries
import pandas as pd
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import string
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
import nltk
import os
import warnings

#Libraries used to remove Stop words
nltk.download('stopwords')
nltk.download('wordnet')

#Loading text files from a folder and assign labels
def load_text_files_as_list(data_dir, label):
    texts = []
    for fname in os.listdir(data_dir):
        if fname.endswith('.txt'):
            with open(os.path.join(data_dir, fname), 'r', encoding='utf-8') as f:
                texts.append((f.read(), label))
    return texts

#Data Preprocessing
#Cleaning the data using regex
def clean_text(text):
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    REPLACE_NO_SPACE = re.compile("[.;:!\'?,\"()\[\]]")
    text = REPLACE_NO_SPACE.sub("", text.lower())
    REPLACE_WITH_SPACE = re.compile("(<br\s*/><br\s*/>)|(\-)|(\/)")
    text = REPLACE_WITH_SPACE.sub(" ", text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub('[''"",,,]', '', text)
    text = re.sub('\n', '', text)
    return text

#Removing stop words
def remove_stop_words(corpus):
    english_stop_words = stopwords.words('english')
    return [' '.join([word for word in review.split() if word not in english_stop_words]) for review in corpus]

#Implementing Lemmatization
def get_lemmatized_text(corpus):
    from nltk.stem import WordNetLemmatizer
    lemmatizer = WordNetLemmatizer()
    return [' '.join([lemmatizer.lemmatize(word) for word in review.split()]) for review in corpus]

if __name__ == "__main__":
    # Loading training and test data, and concatenate them into a single DataFrame
    folder_neg_train = 'train/neg'
    folder_pos_train = 'train/pos'
    folder_neg_test = 'test/neg'
    folder_pos_test = 'test/pos'
    texts_list_train = load_text_files_as_list(folder_neg_train, label=0) + load_text_files_as_list(folder_pos_train, label=1)
    texts_list_test = load_text_files_as_list(folder_neg_test, label=0) + load_text_files_as_list(folder_pos_test, label=1)
    df_train = pd.DataFrame(texts_list_train, columns=['Review', 'Label'])
    df_test = pd.DataFrame(texts_list_test, columns=['Review', 'Label'])
    concatenated_df = pd.concat([df_train, df_test], ignore_index=True)
    concatenated_df.to_csv('data_not_clean.csv', index=False)

    # Data Preprocessing - Calling the functions to clean the data
    concatenated_df['Review'] = concatenated_df['Review'].apply(clean_text)
    concatenated_df['Review'] = remove_stop_words(concatenated_df['Review'])
    concatenated_df['Review'] = get_lemmatized_text(concatenated_df['Review'])

    #Exporting the clean data to the CSV file
    concatenated_df.to_csv('data_IMDB.csv', index=False)

    # Splitting the concatenated DataFrame back into train and test DataFrames
    # First 25k datapoints are Training dataset and the next 25k datapoints are the testing dataset
    df_train = concatenated_df.iloc[:len(df_train)]
    df_test = concatenated_df.iloc[len(df_train):]
    x_train = df_train['Review']
    x_test = df_test['Review']
    y_train = df_train['Label']
    y_test = df_test['Label']

    #Defining Vectorizer and Classifier
    #Here we are using Tfidf Vectorizer and LogisticRegression Classifier
    tf = TfidfVectorizer()
    classifier = LogisticRegression()
    #Defining the Model
    model = Pipeline([('vectorizer', tf), ('classifier', classifier)])

    # Define the hyperparameter grid for grid search - Tuning the Hyperparamters
    param_grid = {
        'vectorizer__max_features': [5000, 10000],  # Max number of features in TfidfVectorizer
        'classifier__C': [0.1, 1, 10],  # Regularization parameter for Logistic Regression
        'classifier__penalty': ['l1', 'l2']  # Regularization type for Logistic Regression
    }

    # Split the training data into training and validation sets
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.25, random_state=42)

    # Perform grid search with cross-validation
    grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy', n_jobs=-1)
    grid_search.fit(x_train, y_train)

    # Get the best hyperparameters and the corresponding model
    best_params = grid_search.best_params_
    best_model = grid_search.best_estimator_

    #Evaluating training accuracy of the model with the best hyperparameters
    y_train_pred = best_model.predict(x_train)
    train_accuracy = accuracy_score(y_train, y_train_pred)
    print("Training Accuracy", train_accuracy)

    # Saving the the model
    import joblib
    joblib.dump(best_model, 'model.pkl')

