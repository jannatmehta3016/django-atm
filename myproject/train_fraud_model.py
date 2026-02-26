import os
import django
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
import joblib

# ----------------------------
# Step 0: Setup Django
# ----------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")  # replace with your settings
django.setup()
print("✅ Django environment ready")

# ----------------------------
# Step 1: Load data from Django model
# ----------------------------
from main.models import Transaction  # replace with your app/model

qs = Transaction.objects.all().values()
data = pd.DataFrame.from_records(qs)
if data.empty:
    raise ValueError("No transactions found in DB!")
print(f"✅ Loaded {len(data)} transactions from database")

# ----------------------------
# Step 2: Preprocessing
# ----------------------------

# Drop unneeded columns
drop_cols = ['id', 'created_at', 'updated_at']
data = data.drop(columns=[c for c in drop_cols if c in data.columns])

# 1️⃣ Convert categorical columns
if 'transaction_type' in data.columns:
    data['transaction_type'] = data['transaction_type'].astype('category').cat.codes

# 2️⃣ Convert numeric-like columns
if 'amount' in data.columns:
    data['amount'] = data['amount'].astype(str).str.replace(',', '').astype(float)

# 3️⃣ Convert datetime columns to numeric
if 'timestamp' in data.columns:
    data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
    data['timestamp_year'] = data['timestamp'].dt.year.astype(int)
    data['timestamp_month'] = data['timestamp'].dt.month.astype(int)
    data['timestamp_day'] = data['timestamp'].dt.day.astype(int)
    data['timestamp_hour'] = data['timestamp'].dt.hour.astype(int)
    data['timestamp_minute'] = data['timestamp'].dt.minute.astype(int)
    data['timestamp_weekday'] = data['timestamp'].dt.weekday.astype(int)
    data.drop(columns=['timestamp'], inplace=True)

# 4️⃣ Convert any remaining object/string columns (except target) to codes
text_cols = data.select_dtypes(include=['object', 'string']).columns.tolist()
if 'is_fraud' in text_cols:
    text_cols.remove('is_fraud')
for col in text_cols:
    data[col] = data[col].astype('category').cat.codes

# Ensure target exists
if 'is_fraud' not in data.columns:
    raise ValueError("'is_fraud' column not found!")

print("✅ Preprocessing done (all features numeric)")

# ----------------------------
# Step 3: Split features & target
# ----------------------------
X = data.drop('is_fraud', axis=1)
y = data['is_fraud']

# Convert everything to numeric, drop only columns that cannot be converted
X = X.apply(pd.to_numeric, errors='coerce')
X = X.dropna(axis=1)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"✅ Data split: {len(X_train)} train rows, {len(X_test)} test rows")

# ----------------------------
# Step 4: Train model with class balancing
# ----------------------------
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight='balanced'  # handle imbalanced classes
)
model.fit(X_train, y_train)
print("✅ Model trained")

# ----------------------------
# Step 5: Evaluate model
# ----------------------------
y_pred = model.predict(X_test)
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

# ----------------------------
# Step 6: Save model
# ----------------------------
joblib.dump(model, "fraud_model.pkl")
print("💾 Model saved as fraud_model.pkl")
print("🎉 Script finished successfully!")