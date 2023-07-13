import joblib

def get_prediction(x):
    clf = joblib.load('newclassify.pkl')
    return clf.predict(x)
