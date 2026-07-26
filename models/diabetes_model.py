
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression

# Load Dataset
BASE_DIR = Path(__file__).resolve().parents[1]
data = pd.read_csv(BASE_DIR / "Datasets" / "diabetes.csv")

# Features and Target
X = data.drop("Outcome", axis=1)
y = data["Outcome"]

# Train Model
model = LogisticRegression(max_iter=1000)
model.fit(X, y)

def predict_diabetes(values):

    prediction = model.predict([values])[0]
    probability = model.predict_proba([values])[0][1]

    if prediction == 1:
        result = "High Risk"
    else:
        result = "Low Risk"

    return {
        "result": result,
        "probability": round(float(probability), 2)
    }
