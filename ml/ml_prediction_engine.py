import pandas as pd
import numpy as np

from sklearn.ensemble import (
    RandomForestClassifier
)

from sklearn.model_selection import (
    train_test_split
)

from sklearn.metrics import (
    accuracy_score
)

# =========================================================
# FEATURE COLUMNS
# =========================================================

FEATURE_COLUMNS = [

    "RSI",

    "MACD",

    "ADX",

    "Stoch RSI",

    "Institutional Score",

    "Alpha Score",

    "Volatility Score"
]

# =========================================================
# PREPARE DATASET
# =========================================================

def prepare_ml_dataset(df):

    ml_df = df.copy()

    ml_df = ml_df.dropna()

    # =====================================================
    # TARGET CREATION
    # =====================================================

    ml_df["Target"] = np.where(

        ml_df["Alpha Score"] >= 70,

        1,

        0
    )

    return ml_df

# =========================================================
# TRAIN MODEL
# =========================================================

def train_ml_model(df):

    ml_df = prepare_ml_dataset(df)

    if len(ml_df) < 50:

        return None, 0

    X = ml_df[
        FEATURE_COLUMNS
    ]

    y = ml_df["Target"]

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.2,

        random_state=42
    )

    model = RandomForestClassifier(

        n_estimators=200,

        max_depth=10,

        random_state=42
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    return model, round(
        accuracy * 100,
        2
    )

# =========================================================
# GENERATE PREDICTIONS
# =========================================================

def generate_predictions(model, df):

    prediction_df = df.copy()

    features = prediction_df[
        FEATURE_COLUMNS
    ].fillna(0)

    probabilities = model.predict_proba(
        features
    )[:, 1]

    prediction_df[
        "Buy Probability"
    ] = probabilities * 100

    prediction_df[
        "Sell Probability"
    ] = (
        1 - probabilities
    ) * 100

    prediction_df[
        "Prediction Confidence"
    ] = np.maximum(

        prediction_df[
            "Buy Probability"
        ],

        prediction_df[
            "Sell Probability"
        ]
    )

    prediction_df[
        "Predicted Trend"
    ] = np.where(

        prediction_df[
            "Buy Probability"
        ] >= 50,

        "Bullish",

        "Bearish"
    )

    prediction_df[
        "AI Signal"
    ] = np.where(

        prediction_df[
            "Buy Probability"
        ] >= 80,

        "Strong Buy",

        np.where(

            prediction_df[
                "Buy Probability"
            ] >= 60,

            "Buy",

            np.where(

                prediction_df[
                    "Buy Probability"
                ] >= 40,

                "Watch",

                "Avoid"
            )
        )
    )

    prediction_df[
        "ML Score"
    ] = round(

        prediction_df[
            "Buy Probability"
        ],

        2
    )

    return prediction_df