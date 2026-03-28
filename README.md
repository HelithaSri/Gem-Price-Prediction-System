# 💎 Gem Price Prediction System

A machine learning-based system for predicting gemstone prices using data analysis, feature engineering, and scikit-learn models. The project is organized with Jupyter notebooks for exploration and a Python source package for modular, reusable code.

---

## 📁 Project Structure

```
Gem-Price-Prediction-System/
├── models/             # Trained model files (saved artifacts)
├── notebooks/          # Jupyter notebooks for EDA and model development
├── src/                # Source Python modules (preprocessing, training, prediction)
├── requirements.txt    # Python dependency list
└── .gitignore
```

---

## 🚀 Features

- Exploratory Data Analysis (EDA) on gemstone datasets
- Data preprocessing and feature engineering pipeline
- Machine learning model training and evaluation using scikit-learn
- Handles class imbalance using imbalanced-learn
- Visualization with matplotlib and seaborn
- Modular and reusable source code under `src/`

---

## 🛠️ Tech Stack

| Category | Libraries |
|---|---|
| Machine Learning | scikit-learn, imbalanced-learn |
| Data Processing | pandas, numpy, scipy |
| Visualization | matplotlib, seaborn |
| Notebook Environment | JupyterLab, ipywidgets |
| HTTP / Utilities | requests, beautifulsoup4 |

---

## ⚙️ Installation

### Prerequisites

- Python 3.9+
- pip

### Steps

1. **Clone the repository**

```bash
git clone https://github.com/HelithaSri/Gem-Price-Prediction-System.git
cd Gem-Price-Prediction-System
```

2. **Create and activate a virtual environment** (recommended)

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

---

## 📓 Usage

### Running Notebooks

Launch JupyterLab and open the notebooks in the `notebooks/` folder:

```bash
jupyter lab
```

The notebooks cover:
- Data loading and exploration
- Feature engineering
- Model training and evaluation
- Price prediction

### Running Source Modules

Python modules in the `src/` directory can be imported and used independently for preprocessing, training, or inference tasks.

---

## 📊 Model

Trained model artifacts are stored in the `models/` directory. These can be loaded using joblib or pickle for inference without retraining.

```python
import joblib

model = joblib.load("models/<model_file>.pkl")
prediction = model.predict(X_new)
```

---

## 📦 Key Dependencies

```
scikit-learn==1.7.1
imbalanced-learn==0.14.0
pandas==2.3.2
numpy==2.2.6
matplotlib==3.10.6
seaborn==0.13.2
jupyterlab==4.4.7
```

Full list available in [`requirements.txt`](requirements.txt).

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source. Please add a license file if you intend to distribute or share this project publicly.

---

## 👤 Author
Built by [Helitha Praveen](https://www.helithasri.dev)
