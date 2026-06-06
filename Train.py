import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
import pickle

# ===========================
# 1. Load Dataset
# ===========================
df = pd.read_csv("data.csv")

X = df.drop("depression_score", axis=1)
y = df["depression_score"]

# ===========================
# 2. Train Test Split
# ===========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ===========================
# 3. Feature Scaling
# ===========================
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# ===========================
# 4. Initialize Models
# ===========================
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Random Forest": RandomForestClassifier(n_estimators=300),
    "SVM": SVC(kernel="rbf")
}

accuracy_results = {}
trained_models = {}

# ===========================
# 5. Training Loop
# ===========================
for name, model in models.items():
    print(f"\nTraining model: {name} ...")
    
    # For SVM / Logistic → use scaled data
    if name in ["SVM", "Logistic Regression"]:
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    accuracy_results[name] = acc
    trained_models[name] = model

    print(f"{name} Accuracy: {acc:.4f}")

# ===========================
# 6. Best Model Selection
# ===========================
best_model_name = max(accuracy_results, key=accuracy_results.get)
best_model = trained_models[best_model_name]

print("\n==============================")
print(f"BEST MODEL: {best_model_name}")
print(f"ACCURACY  : {accuracy_results[best_model_name]:.4f}")
print("==============================")

# ===========================
# 7. Save Best Model
# ===========================
with open("best_depression_model.pkl", "wb") as file:
    pickle.dump(best_model, file)

# save scaler too (important for frontend prediction)
with open("scaler.pkl", "wb") as file:
    pickle.dump(scaler, file)

print("\nModel and Scaler Saved Successfully!")
