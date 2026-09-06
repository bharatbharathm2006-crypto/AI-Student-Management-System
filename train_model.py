import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import pickle

# Sample student data
data = {
    "Attendance": [95, 80, 60, 90, 75, 50, 85, 65],
    "Marks": [90, 70, 45, 88, 60, 35, 78, 50],
    "Result": ["Pass", "Pass", "Fail", "Pass", "Pass", "Fail", "Pass", "Fail"]
}

# Create DataFrame
df = pd.DataFrame(data)

# Input (X)
X = df[["Attendance", "Marks"]]

# Output (Y)
y = df["Result"]

# Train AI Model
model = DecisionTreeClassifier()
model.fit(X, y)

# Save the trained model
with open("student_model.pkl", "wb") as file:
    pickle.dump(model, file)

print("AI Model Trained Successfully!")