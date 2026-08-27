import unittest

from app.decimal_number_input_v2 import (
    _get_renderer,
    is_full_mobile_v2_key,
    mobile_decimal_v2_available,
)


class DecimalNumberInputV2Tests(unittest.TestCase):
    def test_v2_is_available_with_current_streamlit(self):
        self.assertTrue(mobile_decimal_v2_available())
        self.assertTrue(callable(_get_renderer()))

    def test_v2_scope_is_full_mobile_only(self):
        for key in (
            "mortem_decimal_rt_val",
            "mortem_decimal_tm_val",
            "mortem_decimal_peso",
            "mortem_decimal_ta_base_val",
            "mortem_decimal_ta_other_val",
            "mortem_decimal_fattore_correzione",
            "mortem_decimal_fc_min_val",
            "mortem_decimal_fc_other_val",
        ):
            self.assertTrue(is_full_mobile_v2_key(key))

        for key in (
            "mortem_decimal_rt_val_widget",
            "mortem_decimal_ta_base_val_widget",
            "mortem_decimal_peso_widget",
            None,
        ):
            self.assertFalse(is_full_mobile_v2_key(key))


if __name__ == "__main__":
    unittest.main()
