"""Transparent, classical time-series forecasting (no deep learning).

Candidate models: naive last-value, naive drift, linear trend, Holt
exponential smoothing, and ARIMA when there is enough data. Model
selection uses chronological walk-forward backtesting (never a random
shuffle) against a naive baseline, comparing MAE/MAPE. Requires at least
`MIN_OBSERVATIONS` valid points; forecasts default to a 3-year horizon;
every result is labeled an experimental estimate with a reliability level,
never presented as an official statistic.
"""

from __future__ import annotations

from dataclasses import dataclass, field

MIN_OBSERVATIONS = 8
LIMITED_DATA_THRESHOLD = 15
DEFAULT_HORIZON = 3


class InsufficientObservationsError(ValueError):
    def __init__(self, count: int):
        super().__init__(f"Need at least {MIN_OBSERVATIONS} observations, got {count}.")
        self.count = count


@dataclass
class ModelForecast:
    model_name: str
    predictions: list[float]  # length == horizon, chronological
    backtest_mae: float | None
    backtest_mape: float | None


@dataclass
class ForecastResult:
    model_name: str
    baseline_model: str
    horizon_years: list[int]
    predicted_values: list[float]
    lower_bounds: list[float]
    upper_bounds: list[float]
    mae: float | None
    mape: float | None
    baseline_mae: float | None
    baseline_mape: float | None
    reliability: str  # low | moderate | high
    limited_data_warning: bool
    observation_count: int
    clamped_to_zero: bool


def _naive_last_value(train_values: list[float], horizon: int) -> list[float]:
    return [train_values[-1]] * horizon


def _naive_drift(train_values: list[float], horizon: int) -> list[float]:
    n = len(train_values)
    if n < 2:
        return _naive_last_value(train_values, horizon)
    slope = (train_values[-1] - train_values[0]) / (n - 1)
    return [train_values[-1] + slope * step for step in range(1, horizon + 1)]


def _linear_trend(train_years: list[int], train_values: list[float], horizon: int) -> list[float]:
    import numpy as np

    coeffs = np.polyfit(train_years, train_values, deg=1)
    poly = np.poly1d(coeffs)
    last_year = train_years[-1]
    return [float(poly(last_year + step)) for step in range(1, horizon + 1)]


def _holt(train_values: list[float], horizon: int) -> list[float] | None:
    if len(train_values) < 4:
        return None
    try:
        from statsmodels.tsa.holtwinters import Holt

        model = Holt(train_values, initialization_method="estimated").fit(optimized=True)
        forecast = model.forecast(horizon)
        return [float(v) for v in forecast]
    except Exception:
        return None


def _arima(train_values: list[float], horizon: int) -> list[float] | None:
    if len(train_values) < 12:
        return None
    try:
        from statsmodels.tsa.arima.model import ARIMA

        model = ARIMA(train_values, order=(1, 1, 0)).fit()
        forecast = model.forecast(horizon)
        return [float(v) for v in forecast]
    except Exception:
        return None


def _mae(errors: list[float]) -> float:
    return sum(abs(e) for e in errors) / len(errors)


def _mape(actuals: list[float], errors: list[float]) -> float | None:
    pct_errors = [abs(e) / abs(a) for e, a in zip(errors, actuals) if a != 0]
    if not pct_errors:
        return None
    return (sum(pct_errors) / len(pct_errors)) * 100


def _backtest(
    years: list[int], values: list[float], model_fn, min_train_size: int
) -> tuple[float | None, float | None]:
    """Rolling-origin one-step-ahead backtest: for each held-out point after
    min_train_size, fit on all prior points only (chronological, never
    shuffled) and predict one step ahead."""
    errors: list[float] = []
    actuals: list[float] = []
    for cut in range(min_train_size, len(values)):
        train_years, train_values = years[:cut], values[:cut]
        actual = values[cut]
        try:
            prediction = model_fn(train_years, train_values, 1)
            if not prediction:
                continue
            pred = prediction[0]
        except Exception:
            continue
        errors.append(pred - actual)
        actuals.append(actual)
    if not errors:
        return None, None
    return _mae(errors), _mape(actuals, errors)


def _reliability(observation_count: int, mape: float | None) -> tuple[str, bool]:
    limited_data_warning = observation_count < LIMITED_DATA_THRESHOLD
    if mape is None:
        return "low", limited_data_warning
    if mape < 8 and not limited_data_warning:
        return "high", limited_data_warning
    if mape < 20:
        return "moderate", limited_data_warning
    return "low", limited_data_warning


def generate_forecast(
    series: dict[int, float],
    horizon: int = DEFAULT_HORIZON,
    non_negative: bool = True,
    preferred_model: str | None = None,
) -> ForecastResult:
    if horizon < 1 or horizon > 3:
        raise ValueError("horizon must be between 1 and 3")
    observation_count = len(series)
    if observation_count < MIN_OBSERVATIONS:
        raise InsufficientObservationsError(observation_count)

    years = sorted(series)
    values = [series[y] for y in years]
    min_train_size = max(4, len(values) - 5)  # backtest on the last few points

    candidates: dict[str, callable] = {
        "naive_last_value": lambda ty, tv, h: _naive_last_value(tv, h),
        "naive_drift": lambda ty, tv, h: _naive_drift(tv, h),
        "linear_trend": lambda ty, tv, h: _linear_trend(ty, tv, h),
    }
    holt_result = _holt(values, 1)
    if holt_result is not None:
        candidates["holt_exponential_smoothing"] = lambda ty, tv, h: _holt(tv, h)
    arima_result = _arima(values, 1)
    if arima_result is not None:
        candidates["arima"] = lambda ty, tv, h: _arima(tv, h)

    if preferred_model is not None and preferred_model not in candidates:
        raise ValueError(f"Preferred model '{preferred_model}' is not available for this series.")

    baseline_mae, baseline_mape = _backtest(years, values, candidates["naive_last_value"], min_train_size)

    best_name, best_mae, best_mape = "naive_last_value", baseline_mae, baseline_mape
    for name, fn in candidates.items():
        if name == "naive_last_value":
            continue
        mae, mape = _backtest(years, values, fn, min_train_size)
        if mae is None:
            continue
        current_best = best_mape if best_mape is not None else best_mae
        candidate_score = mape if mape is not None else mae
        best_score = best_mape if best_mape is not None else best_mae
        if best_score is None or (candidate_score is not None and candidate_score < best_score):
            best_name, best_mae, best_mape = name, mae, mape

    if preferred_model is not None:
        best_name = preferred_model
        best_mae, best_mape = _backtest(years, values, candidates[best_name], min_train_size)

    final_fn = candidates[best_name]
    predictions = final_fn(years, values, horizon)
    if predictions is None:
        best_name = "naive_last_value"
        predictions = _naive_last_value(values, horizon)

    reliability, limited_data_warning = _reliability(observation_count, best_mape)

    margin = best_mae if best_mae is not None else (max(values) - min(values)) * 0.1
    lower = [p - margin for p in predictions]
    upper = [p + margin for p in predictions]

    clamped = False
    if non_negative:
        new_lower = []
        for lo in lower:
            if lo < 0:
                clamped = True
                new_lower.append(0.0)
            else:
                new_lower.append(lo)
        lower = new_lower
        predictions = [max(p, 0.0) for p in predictions]

    horizon_years = [years[-1] + step for step in range(1, horizon + 1)]

    return ForecastResult(
        model_name=best_name,
        baseline_model="naive_last_value",
        horizon_years=horizon_years,
        predicted_values=predictions,
        lower_bounds=lower,
        upper_bounds=upper,
        mae=best_mae,
        mape=best_mape,
        baseline_mae=baseline_mae,
        baseline_mape=baseline_mape,
        reliability=reliability,
        limited_data_warning=limited_data_warning,
        observation_count=observation_count,
        clamped_to_zero=clamped,
    )
