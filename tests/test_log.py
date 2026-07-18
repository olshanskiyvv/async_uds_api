from async_uds_api.log import SENSITIVE_PARAMS, mask_params, mask_value


class TestMaskValue:
    def test_keeps_last_four_characters(self):
        assert mask_value("+79991234567") == "***4567"

    def test_masks_short_value_completely(self):
        assert mask_value("1234") == "***"

    def test_masks_empty_value_completely(self):
        assert mask_value("") == "***"

    def test_converts_non_string_before_masking(self):
        assert mask_value(79991234567) == "***4567"

    def test_masks_uuid_tail(self):
        assert mask_value("9f8b1c2d-4e5f-6a7b-8c9d-0e1f2a3ba97e") == "***a97e"


class TestMaskParams:
    def test_masks_sensitive_keys(self):
        result = mask_params({"phone": "+79991234567", "uid": "abcd1234"})

        assert result == {"phone": "***4567", "uid": "***1234"}

    def test_keeps_other_keys_untouched(self):
        result = mask_params({"max": 50, "cursor": "abc"})

        assert result == {"max": 50, "cursor": "abc"}

    def test_masks_code(self):
        assert mask_params({"code": "998877"}) == {"code": "***8877"}

    def test_returns_none_for_none(self):
        assert mask_params(None) is None

    def test_does_not_mutate_input(self):
        source = {"phone": "+79991234567"}

        mask_params(source)

        assert source == {"phone": "+79991234567"}

    def test_sensitive_params_content(self):
        assert SENSITIVE_PARAMS == frozenset({"phone", "uid", "code"})
