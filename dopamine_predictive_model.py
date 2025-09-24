import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, learning_curve
from sklearn.metrics import (
    classification_report, accuracy_score, confusion_matrix,
    roc_auc_score, log_loss, precision_score, recall_score, f1_score, matthews_corrcoef
)
import shap

warnings.filterwarnings("ignore", category=FutureWarning)

print("[1] Loading & preparing dataset...")
df = pd.read_csv("Dopamine_Data.csv")
df_clean = df.dropna(subset=["dopamine_label"]).copy()

if "view_count" in df_clean.columns:
    df_clean["log_view_count"] = np.log1p(df_clean["view_count"])

if "date_published" in df_clean.columns:
    df_clean['date_published'] = pd.to_datetime(df_clean['date_published'], format='%d-%m-%Y', errors='coerce')
    df_clean["publish_year"] = df_clean["date_published"].dt.year
    df_clean["publish_month"] = df_clean["date_published"].dt.month
    df_clean["publish_dayofweek"] = df_clean["date_published"].dt.dayofweek
    df_clean["is_weekend"] = df_clean["publish_dayofweek"].isin([5, 6]).astype(int)

cols_to_drop = ["dopamine_label", "video_id", "channel_name", "video_title", "date_published", "view_count"]
X = df_clean.drop(columns=cols_to_drop, errors="ignore")
y = df_clean["dopamine_label"]

categorical_features = X.select_dtypes(include=["object", "category"]).columns.tolist()
numerical_features = X.select_dtypes(include=np.number).columns.tolist()

for col in categorical_features:
    X[col] = X[col].fillna("missing_value").astype(str)
for col in numerical_features:
    X[col] = X[col].fillna(X[col].median())

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

print("[2] Initializing CatBoost with best params...")

best_params = {
    "iterations": 233,
    "learning_rate": 0.010233450512719894,
    "depth": 4,
    "l2_leaf_reg": 1.4970339664427752
}

final_model = CatBoostClassifier(
    **best_params,
    cat_features=categorical_features,
    random_seed=42,
    verbose=0
)

print("[3] Running cross-validation with tuned CatBoost...")

CV_SPLITS = 5
cv_strategy = StratifiedKFold(n_splits=CV_SPLITS, shuffle=True, random_state=42)

results_df = pd.DataFrame(columns=['Fold', 'Accuracy', 'ROC_AUC', 'F1-Score', 'Precision', 'Recall', 'MCC', 'LogLoss'])

for fold_num, (train_idx, val_idx) in enumerate(cv_strategy.split(X_train, y_train), 1):
    X_fold_train, X_fold_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
    y_fold_train, y_fold_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
    final_model.fit(X_fold_train, y_fold_train)
    y_pred = final_model.predict(X_fold_val)
    y_proba = final_model.predict_proba(X_fold_val)[:, 1]

    metrics = {
        'Fold': fold_num,
        'Accuracy': accuracy_score(y_fold_val, y_pred),
        'ROC_AUC': roc_auc_score(y_fold_val, y_proba),
        'F1-Score': f1_score(y_fold_val, y_pred),
        'Precision': precision_score(y_fold_val, y_pred),
        'Recall': recall_score(y_fold_val, y_pred),
        'MCC': matthews_corrcoef(y_fold_val, y_pred),
        'LogLoss': log_loss(y_fold_val, y_proba)
    }
    results_df = pd.concat([results_df, pd.DataFrame([metrics])], ignore_index=True)

cv_summary = results_df.agg(
    Avg_Accuracy=('Accuracy', 'mean'),
    Avg_ROC_AUC=('ROC_AUC', 'mean'),
    Avg_F1_Score=('F1-Score', 'mean'),
    Avg_Precision=('Precision', 'mean'),
    Avg_Recall=('Recall', 'mean'),
    Avg_MCC=('MCC', 'mean')
)

print("\nCross-Validation Summary:")
print(cv_summary.to_string(index=False))

print("[4] Training on full train set and evaluating on test set...")

final_model.fit(X_train, y_train)
y_pred_final = final_model.predict(X_test)
y_pred_proba_final = final_model.predict_proba(X_test)[:, 1]

print("\n=== CatBoost Test Set Evaluation (Best Params) ===")
print(f"Accuracy: {accuracy_score(y_test, y_pred_final):.4f}, ROC AUC: {roc_auc_score(y_test, y_pred_proba_final):.4f}")
print(classification_report(y_test, y_pred_final))

cm = confusion_matrix(y_test, y_pred_final)
sns.heatmap(cm, annot=True, fmt="d", cmap="viridis", cbar=False)
plt.title("Confusion Matrix - CatBoost (Best Params)")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

print("[5] Running SHAP interpretability...")

explainer = shap.TreeExplainer(final_model)
shap_values = explainer(X_test)

shap.summary_plot(shap_values, X_test, plot_type="bar")
shap.summary_plot(shap_values, X_test)

print("[6] Plotting learning curve...")

def plot_learning_curve(estimator, X, y, title):
    sizes, train_scores, val_scores = learning_curve(
        estimator, X, y, cv=cv_strategy, scoring='roc_auc', n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 10)
    )
    plt.plot(sizes, train_scores.mean(axis=1), label='Train')
    plt.plot(sizes, val_scores.mean(axis=1), label='Validation')
    plt.fill_between(sizes, train_scores.mean(axis=1) - train_scores.std(axis=1),
                     train_scores.mean(axis=1) + train_scores.std(axis=1), alpha=0.1)
    plt.fill_between(sizes, val_scores.mean(axis=1) - val_scores.std(axis=1),
                     val_scores.mean(axis=1) + val_scores.std(axis=1), alpha=0.1)
    plt.title(f"Learning Curve - {title}")
    plt.xlabel("Training Samples")
    plt.ylabel("ROC AUC")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

plot_learning_curve(final_model, X_train, y_train, "CatBoost")
