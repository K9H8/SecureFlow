import sqlite3
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

# Step 1: Connect to the SQLite database
db_path = "system_metrics.db"  # Path to your local database file
connection = sqlite3.connect(db_path)

# Step 2: Query the database
query = "SELECT * FROM minute_averages;"  # Replace with your table name
data = pd.read_sql_query(query, connection)

# Close the connection
connection.close()

# Step 3: Select numerical features for analysis
features = ["avg_cpu_percent", "avg_ram_percent", "avg_upload_speed", "avg_download_speed", "avg_disk_read_speed", "avg_disk_write_speed"]
data_features = data[features]

# Step 4: Scale the features
scaler = StandardScaler()
data_scaled = scaler.fit_transform(data_features)

# Step 5: Train the Isolation Forest model
iso_forest = IsolationForest(contamination=0.05, random_state=42)
iso_forest.fit(data_scaled)

# Step 6: Predict anomalies (1 = normal, -1 = anomaly)
predictions = iso_forest.predict(data_scaled)

# Add predictions to the original DataFrame
data["anomaly"] = predictions

# Step 7: Check anomalies and provide reasons
anomalies = data[data["anomaly"] == -1]  # Rows flagged as anomalies
if not anomalies.empty:
    for index, row in anomalies.iterrows():
        print(f"Anomaly detected at index {index}:")
        for feature in features:
            if row[feature] > data[feature].mean() + 3 * data[feature].std() or row[feature] < data[feature].mean() - 3 * data[feature].std():
                print(f" - {feature} = {row[feature]} (out of expected range)\n")

# Step 8: Predict on a sample data point
sample = {
    "avg_cpu_percent": 40.0,       # Replace with actual values
    "avg_ram_percent": 40.0,
    "avg_upload_speed": 100.0,
    "avg_download_speed": 20000000.0,
    "avg_disk_read_speed": 3000.0,
    "avg_disk_write_speed": 3000.0
}

# Convert sample to DataFrame and scale it
sample_df = pd.DataFrame([sample])
sample_scaled = scaler.transform(sample_df)

# Predict if the sample is an anomaly
sample_prediction = iso_forest.predict(sample_scaled)

# Interpret the prediction
if sample_prediction[0] == -1:
    print("The sample is an anomaly.")
    # Provide reasoning for the anomaly
    for feature in sample:
        if sample[feature] > data[feature].mean() + 3 * data[feature].std() or sample[feature] < data[feature].mean() - 3 * data[feature].std():
            print(f" - {feature} = {sample[feature]} (out of expected range)")
else:
    print("The sample is normal.")

# Save the DataFrame with predictions to a CSV file
output_file = "trained_data_with_predictions.csv"
data.to_csv(output_file, index=False)
print(f"Trained data with predictions saved to {output_file}")
