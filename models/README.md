# Gem Price Prediction Models

## Model Files
- `gem_price_global.pkl`: Global log-transformed price prediction model
- `gem_price_by_type.pkl`: Individual models for each gem type

## Usage Example
```python
import joblib
import pandas as pd

# Load the model
model = joblib.load('outputs/models/gem_price_global.pkl')

# Prepare input data (must have same columns as training data)
features = ['Carat Weight (ct)', 'Length_mm', 'Width_mm', 'Depth_mm', 'LW_Ratio', 'DepthPct', 'Gem Type', 'Cut/Shape', 'Colour', 'Clarity', 'Treatments', 'Certification Status']

# Make prediction
X_new = pd.DataFrame([your_data], columns=features)
prediction = model.predict(X_new)

# If using log-transformed model, transform back
if "log-transformed" == "log-transformed":
    prediction = np.expm1(prediction)
```

## Model Performance
Global model RMSLE: 0.536
