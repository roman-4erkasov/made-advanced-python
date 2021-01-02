from argparse import Namespace
from unittest.mock import patch, call, MagicMock
from asset import (
    process_cli_arguments,
    do_busy_work,
    DEFAULT_SMALL_TIME_SLEEP,
    Asset
)
# from asset import


# @patch("asset.load_asset_from_file")
# def test_process_arguments_call_load_once(mock_load_asset_from_file):
def test_process_arguments_call_load_once():
    with patch("asset.load_asset_from_file") as mock_load_asset_from_file:
        with open("asset_example.txt") as fin:
            arguments = Namespace(
                asset_fin=fin,
                periods=[1,2,5],
            )
            process_cli_arguments(arguments)
            expected_calls = [
                call(fin),
                call().calculate_revenue(1),
                call().calculate_revenue(2),
                call().calculate_revenue(5),
            ]
            mock_load_asset_from_file.assert_called_once_with(fin)
            mock_load_asset_from_file.assert_has_calls(expected_calls, any_order=True)
        mock_load_asset_from_file.assert_called_once()
        assert [call(1), call(2), call(5)] == mock_load_asset_from_file.return_value.calculate_revenue.call_args_list


@patch("time.sleep")
def test_can_mock_time_sleep(mock_sleep):
    do_busy_work()
    mock_sleep.assert_called_once_with(DEFAULT_SMALL_TIME_SLEEP)


@patch("asset.Asset")
def test_asset_calculate_revenue_always_returns_100500(mock_asset_class,capsys):
    mick_asset_class = MagicMock(spec=Asset)
    mick_asset_class.calculate_revenue.return_value = 100500.0
    mick_asset_class.build_from_str.return_value = mock_asset_class
    with open("asset_example.txt") as fin:
        arguments = Namespace(
            asset_fin=fin,
            periods=[1, 2, 5],
        )
        process_cli_arguments(arguments)
        captured = capsys.readouterr()
        for line in captured.out.splitlines():
            assert "100500" in line
