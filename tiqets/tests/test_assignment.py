import os
import pathlib
import unittest

from tiqets.assignment import ValidationError
from tiqets.assignment import get_duplicate_barcodes
from tiqets.assignment import get_orders_without_barcodes
from tiqets.assignment import get_top_customers
from tiqets.assignment import get_unused_barcodes
from tiqets.assignment import load_order_barcodes_mapping
from tiqets.assignment import validate_order_barcodes
from tiqets.assignment import write_combine_datasets


class ValidatorsTestCase(unittest.TestCase):
    """
    Unit tests for validators
    """

    def test_get_duplicate_barcodes(self):

        # test if get_duplicate_barcodes can detect the duplicate barcode
        barcodes = [
            ["duplicate", 1],
            ["duplicate", 2],
            ["duplicate", 3],
            ["duplicate", 4],
            ["not_duplicate", 5],
        ]
        expected = ["duplicate"]
        results = get_duplicate_barcodes(barcodes)
        assert results == expected

        # test with malformed data
        barcodes = [
            ["foo", 1],
            ["bar", 2],
            ["biz"],
            ["naz", 4],
        ]
        expected = []
        results = get_duplicate_barcodes(barcodes)
        assert results == expected

        barcodes = [
            ["duplicate", 1],
            ["duplicate", 2],
            ["biz"],
            ["naz", 4],
        ]
        expected = ["duplicate"]
        results = get_duplicate_barcodes(barcodes)
        assert results == expected

    def test_get_unused_barcodes(self):
        # test if get_unused_barcodes can detect unused barcodes
        barcodes = [
            ["foo", 1],
            ["bar", 2],
            ["biz", ""],
            ["naz", None],
        ]
        expected = ["biz", "naz"]
        results = get_unused_barcodes(barcodes)
        assert results == expected

        # test for malformed data raises ValidationError
        barcodes = [
            ["foo", 1],
            ["bar", 2],
            ["naz"],
        ]
        with self.assertRaises(ValidationError):
            get_unused_barcodes(barcodes)

    def test_get_orders_without_barcodes(self):
        # test if get_orders_without_barcode can detect unused barcodes
        barcodes = [
            ["", 1],
            [None, 2],
            ["biz", 3],
            ["naz", 4],
        ]
        expected = [1, 2]
        results = get_orders_without_barcodes(barcodes)
        assert results == expected

        # test if the function can deal with malformed data
        barcodes = [
            ["", ""],
            [None, None],
            ["biz", 3],
            ["naz", 4],
        ]
        expected = ["", None]
        results = get_orders_without_barcodes(barcodes)
        assert results == expected

    def test_validate_order_barcodes(self):
        barcodes = [
            ["foo", 1],
            ["biz", 2],
            ["biz", 3],
            [None, 4],
            ["baz", ""],
        ]
        expected = ["baz", "biz"], [4]
        results = validate_order_barcodes(barcodes)
        assert results == expected


class LoadWriteTestCase(unittest.TestCase):
    """
    Unit tests for Loaders and writers
    """

    def test_load_order_barcodes_mapping(self):
        file_path = pathlib.Path(__file__).parent / "barcodes_1.csv"
        assert file_path.exists()

        results = dict(load_order_barcodes_mapping(file_path.absolute()))
        expected = {
            "1": ["11111111111"],
            "2": ["11111111112"],
            "3": ["11111111113"],
            "4": ["11111111114"],
            "5": ["11111111115", "11111111118"],
        }
        assert results == expected

    def test_write_combine_datasets(self):
        this_path = pathlib.Path(__file__).parent
        output_file_path = this_path / "output_1.csv"
        barcodes_file_path = this_path / "barcodes_1.csv"
        orders_file_path = this_path / "orders_1.csv"

        result = write_combine_datasets(barcodes_file_path.absolute(), orders_file_path.absolute(), output_file_path.absolute())
        expected = [
            ["2", "1", ["11111111111"]],
            ["11", "2", ["11111111112"]],
            ["12", "3", ["11111111113"]],
            ["1", "4", ["11111111114"]],
            ["1", "5", ["11111111115", "11111111118"]],
        ]
        assert result == expected
        # clean up test output file
        os.remove(output_file_path.absolute())

    def test_get_top_customers(self):
        this_path = pathlib.Path(__file__).parent
        output_file_path = this_path / "output_2.csv"
        barcodes_file_path = this_path / "barcodes_2.csv"
        orders_file_path = this_path / "orders_2.csv"

        combined_dataset = write_combine_datasets(barcodes_file_path.absolute(), orders_file_path.absolute(), output_file_path.absolute())

        results = dict(get_top_customers(combined_dataset, 5))
        expected = {
            "99": 6,
            "88": 5,
            "77": 4,
            "66": 3,
            "55": 2,
        }
        assert results == expected
        # clean up test output file
        os.remove(output_file_path.absolute())
