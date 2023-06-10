import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


data = pd.read_csv('skills_200.csv')

data = pd.get_dummies(data, columns=['skill_1', 'skill_2', 'skill_3', 'skill_4', 'skill_5'])

X = data.drop('domain', axis=1)
y = data['domain']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

clf = DecisionTreeClassifier()
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

for i in range(len(X_test)):
    print("Predicted Label:", y_pred[i], "\tDomain Name:", y_test.iloc[i])

