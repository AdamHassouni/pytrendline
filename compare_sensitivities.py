"""
Compare different sensitivity levels for support/resistance detection
Generates 3 charts: tight, medium, and loose
"""
import pytrendline
from pytrendline import util
import pandas as pd
import time

# Define sensitivity presets
SENSITIVITY_PRESETS = {
    "tight": {
        "name": "Tight (Many small supports)",
        "max_error_multiplier": 0.06,
        "pivot_separation_multiplier": 0.2,
        "pivot_grouping_multiplier": 0.1,
        "min_points": 3,
    },
    "medium": {
        "name": "Medium (Balanced)",
        "max_error_multiplier": 0.12,
        "pivot_separation_multiplier": 0.4,
        "pivot_grouping_multiplier": 0.2,
        "min_points": 4,
    },
    "loose": {
        "name": "Loose (Few big supports)",
        "max_error_multiplier": 0.20,
        "pivot_separation_multiplier": 0.6,
        "pivot_grouping_multiplier": 0.3,
        "min_points": 5,
    },
}

# Load data
print("Loading data...")
candles_df = pd.read_csv('./data/aapl_3months_daily.csv')
candles_df.set_index('Idx')
candles_df['Date'] = pd.to_datetime(candles_df['Date'])

print(f"Loaded {len(candles_df)} candles")
print(f"Date range: {candles_df['Date'].iloc[0]} to {candles_df['Date'].iloc[-1]}")
print(f"Price range: ${candles_df['Low'].min():.2f} to ${candles_df['High'].max():.2f}\n")

candlestick_data = pytrendline.CandlestickData(
    df=candles_df,
    time_interval="1d",
    open_col="Open",
    high_col="High",
    low_col="Low",
    close_col="Close",
    datetime_col="Date"
)

# Run detection for each sensitivity level
print("="*70)
for sensitivity, preset in SENSITIVITY_PRESETS.items():
    print(f"\nProcessing: {preset['name']}")
    print(f"  - Tolerance: ±{preset['max_error_multiplier']*100:.0f}%")
    print(f"  - Min touches: {preset['min_points']}")

    # Configure
    custom_config = {
        "max_allowable_error_pt_to_trend": lambda candles, m=preset["max_error_multiplier"]: util.avg_candle_range(candles) * m,
        "pivot_seperation_threshold": lambda candles, m=preset["pivot_separation_multiplier"]: util.avg_candle_range(candles) * m,
        "pivot_grouping_threshold": lambda candles, m=preset["pivot_grouping_multiplier"]: util.avg_candle_range(candles) * m,
    }

    # Detect
    start = time.time()
    results = pytrendline.detect(
        candlestick_data=candlestick_data,
        trend_type=pytrendline.TrendlineTypes.BOTH,
        first_pt_must_be_pivot=False,
        last_pt_must_be_pivot=False,
        all_pts_must_be_pivots=False,
        trendline_must_include_global_maxmin_pt=False,
        min_points_required=preset["min_points"],
        scan_from_date=None,
        ignore_breakouts=True,
        config=custom_config
    )
    elapsed = time.time() - start

    # Summary
    n_support = len(results['support_trendlines']) if 'support_trendlines' in results else 0
    n_resistance = len(results['resistance_trendlines']) if 'resistance_trendlines' in results else 0
    print(f"  - Found {n_support} support + {n_resistance} resistance = {n_support + n_resistance} total")
    print(f"  - Time: {elapsed:.2f}s")

    # Plot
    outf = pytrendline.plot(
        results=results,
        filedir='.',
        filename=f'comparison_{sensitivity}.html',
    )
    print(f"  - Saved: {outf}")

print("\n" + "="*70)
print("\n✅ Generated 3 comparison charts:")
print("   - comparison_tight.html   (many small supports)")
print("   - comparison_medium.html  (balanced)")
print("   - comparison_loose.html   (few big supports)")
print("\nOpen them in your browser to compare!")
