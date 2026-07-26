
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression

# Load Heart Dataset
BASE_DIR = Path(__file__).resolve().parents[1]
data = pd.read_csv(BASE_DIR / "Datasets" / "heart.csv")

# Target column (change if your dataset uses a different name)
X = data.drop("target", axis=1)
y = data["target"]

# Train Model
model = LogisticRegression(max_iter=1000)
model.fit(X, y)

def predict_heart(values):

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
