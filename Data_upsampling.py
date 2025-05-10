df = Data_Preprocessing.preprocessing_data(df)
df_features = Data_Preprocessing.drop_columns(df)

# Upsampling using perturb
# Define a function to perturb data slightly
def perturb_data(df):
    df_copy = df.copy()
    # Randomly perturb transaction amounts
    df_copy['TransactionAmount'] = df_copy['TransactionAmount'] * random.uniform(0.9, 1.1)
    # Randomly change other features slightly (like duration)
    df_copy['TransactionDuration'] = df_copy['TransactionDuration'] * random.uniform(0.95, 1.05)
    return df_copy

def prepare_X(df_features):
    # Generate synthetic data
    perturbed_df = perturb_data(df_features)

    # Combine original and perturbed data
    df_model = pd.concat([df_features, perturbed_df], ignore_index=True)
    # Fill any remaining NaNs
    X = df_model.fillna(0)

    return X

X = prepare_X(df_features)

# 5. Scale the data
def scale_X(X):

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled


