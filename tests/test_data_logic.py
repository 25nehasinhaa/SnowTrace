import unittest
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from lib.data import _aggregate_period, _classify_drift, _confidence_level, _pct_change, _recommended_action


class DataLogicTests(unittest.TestCase):
    def test_percent_change_handles_zero_baseline(self):
        result = _pct_change(pd.Series([120.0, 10.0]), pd.Series([100.0, 0.0]))
        self.assertEqual(result.iloc[0], 20.0)
        self.assertTrue(pd.isna(result.iloc[1]))

    def test_missing_period_is_insufficient_data(self):
        row = pd.Series({"BASELINE_VOLUME": 10, "CURRENT_VOLUME": pd.NA})
        self.assertEqual(_classify_drift(row), "INSUFFICIENT_DATA")
        self.assertEqual(_confidence_level(row), "Low")

    def test_material_revenue_change_is_drift(self):
        row = pd.Series(
            {
                "BASELINE_VOLUME": 100,
                "CURRENT_VOLUME": 100,
                "PRICE_CHANGE_PCT": 0.0,
                "VOLUME_CHANGE_PCT": 0.0,
                "REVENUE_CHANGE_PCT": -25.0,
                "REVIEW_SCORE_CHANGE": 0.0,
            }
        )
        self.assertEqual(_classify_drift(row), "DRIFT")

    def test_revenue_and_volume_decline_recommends_demand_review(self):
        row = pd.Series(
            {
                "DRIFT_STATUS": "DRIFT",
                "REVENUE_CHANGE_PCT": -25.0,
                "VOLUME_CHANGE_PCT": -20.0,
                "PRICE_CHANGE_PCT": 0.0,
                "REVIEW_SCORE_CHANGE": 0.0,
                "DELIVERY_DAYS_CHANGE": 0.0,
            }
        )
        self.assertIn("Review demand generation", _recommended_action(row))

    def test_empty_period_preserves_expected_metric_columns(self):
        fact = pd.DataFrame(
            columns=["ORDER_DATE", "DIVISION", "DEPARTMENT", "order_item_id", "REVENUE", "price", "review_score", "DELIVERY_DAYS"]
        )
        result = _aggregate_period(fact, pd.Timestamp("2020-01-01").date(), pd.Timestamp("2020-01-31").date(), "baseline")
        self.assertTrue(result.empty)
        self.assertIn("BASELINE_REVENUE", result.columns)


if __name__ == "__main__":
    unittest.main()
