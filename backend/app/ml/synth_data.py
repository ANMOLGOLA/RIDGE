import numpy as np
import pandas as pd
from app.ml.features import FEATURE_NAMES

def generate_synthetic_training_data(n_samples: int = 3000, random_state: int = 42) -> pd.DataFrame:
    """
    Synthesizes realistic training data grounded in real geomorphology and weather features:
    - High rainfall (> 60mm) + steep slope (> 15 deg) + river proximity (< 100m) heavily correlates with landslide disruption.
    - Historical frequency and live reports provide Bayesian updates.
    - Gaussian noise is added to reflect real-world variance.
    """
    np.random.seed(random_state)

    # 1. Weather features
    rain_past = np.random.gamma(shape=2.5, scale=25.0, size=n_samples) # 0 to 200 mm
    rain_forecast = rain_past * np.random.uniform(0.7, 1.4, size=n_samples)

    # 2. Geomorphological features
    slope = np.random.uniform(1.0, 32.0, size=n_samples)
    river_prox = np.random.exponential(scale=200.0, size=n_samples)
    landslide_zone = (slope > 14.0) & (np.random.rand(n_samples) > 0.35)
    historical_count = np.random.poisson(lam=np.where(landslide_zone, 8, 2), size=n_samples)

    # 3. Live intelligence features
    live_incidents = np.random.poisson(lam=np.where(rain_past > 70, 1.8, 0.2), size=n_samples)
    season_monsoon = np.random.choice([0.0, 1.0], p=[0.25, 0.75], size=n_samples)

    # Calculate Disruption Probability via domain sigmoid function + noise
    # Logit calculation
    z = (
        -3.8 +
        0.028 * rain_past +
        0.022 * rain_forecast +
        0.085 * slope -
        0.003 * np.minimum(river_prox, 500) +
        1.25 * landslide_zone.astype(float) +
        0.08 * historical_count +
        1.10 * np.minimum(live_incidents, 3) +
        0.50 * season_monsoon +
        np.random.normal(0, 0.45, size=n_samples)
    )

    prob = 1.0 / (1.0 + np.exp(-z))
    # Binary label: 1 if disrupted (blocked or severe risk), 0 otherwise
    target = (prob > 0.50).astype(int)

    df = pd.DataFrame({
        "rain_past_24h_mm": rain_past,
        "rain_forecast_24h_mm": rain_forecast,
        "slope_deg": slope,
        "river_proximity_m": river_prox,
        "landslide_zone": landslide_zone.astype(float),
        "historical_incident_count": historical_count.astype(float),
        "live_incidents_nearby": live_incidents.astype(float),
        "season_monsoon": season_monsoon,
        "disruption_label": target
    })

    return df

if __name__ == "__main__":
    df = generate_synthetic_training_data()
    print("Generated synthetic dataset:", df.shape)
    print("Class balance:\n", df["disruption_label"].value_counts(normalize=True))
