# IsolationForest Model

def IsolationForest_Model(X):
    # Work on a copy to avoid modifying original input
    X_model = X.copy()

    # Fit model on clean features only
    iso_forest = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    iso_forest.fit(X_model)

    # Predict anomaly
    scores_iso = iso_forest.decision_function(X_model)
    predictions_iso = iso_forest.predict(X_model)

    # Attach results to output DataFrame
   # X_model['FraudScore'] = predictions_iso
    #X_model['IsFraud'] = (X_model['FraudScore'] == -1).astype(int)

    return X_model, scores_iso, predictions_iso

X_scaled=Data_upsampling.scale_X()
X_iso, scores_iso, predictions_iso = IsolationForest_Model(X_scaled)

# You can inspect the distribution of scores
plt.hist(scores_iso, bins=10)
plt.title("Anomaly Score Distribution")
plt.show()

threshold = 0.10
anomalies = scores_iso > threshold
print(f"Number of anomalies: {sum(anomalies)}")

sil_score = silhouette_score(X_iso, predictions_iso)
sil_score