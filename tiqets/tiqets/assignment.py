import csv
import logging
import sys
import typing
from collections import Counter
from collections import defaultdict
from itertools import groupby
from pathlib import Path
from typing import Any
from typing import Sequence

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ValidationError(Exception):
    """Custom validation exception, So it's easy to catch and differentiate from other exceptions"""


def get_duplicate_barcodes(barcodes: list[list[str]]) -> list[str]:
    # Group dataset on barcodes to detect duplicates
    duplicates = []
    for barcode, orders in groupby(barcodes, lambda x: x[0]):
        if len(list(orders)) > 1:
            duplicates.append(barcode)
    return duplicates


def get_unused_barcodes(barcodes: list[list[str]]) -> list[str]:
    # Return all rows where the order_id is missing
    try:
        return [barcode for barcode, _ in filter(lambda x: not x[1], barcodes)]
    except IndexError as exc:
        raise ValidationError("Barcode data is malformed, please use correct barcodes.") from exc


def get_orders_without_barcodes(barcodes: list[list[str]]) -> list[str]:
    # Return all rows where the barcodes is missing
    return [order_id for _, order_id in filter(lambda x: not x[0], barcodes)]


def validate_order_barcodes(barcode_order_id: list[list[str]]) -> tuple[list[str], list[str]]:
    # Identify any unused barcodes
    unused_barcodes = get_unused_barcodes(barcode_order_id)
    if unused_barcodes:
        logger.info("(%s) Unused barcodes will not be used for customer data: %s", len(unused_barcodes), unused_barcodes)

    # Identify any duplicate barcodes
    duplicate_barcodes = get_duplicate_barcodes(barcode_order_id)
    if duplicate_barcodes:
        logger.error("(%s) Duplicated barcodes will not be used for customer data: %s", len(duplicate_barcodes), duplicate_barcodes)

    # Find any orders without a barcode
    orders_without_barcodes = get_orders_without_barcodes(barcode_order_id)
    if orders_without_barcodes:
        logger.error("(%s) Orders without barcodes will not be used for customer data: %s", len(orders_without_barcodes), orders_without_barcodes)

    return unused_barcodes + duplicate_barcodes, orders_without_barcodes


def load_order_barcodes_mapping(file_path: Path) -> dict[str, list[str]]:
    # validate the data and map order_id to list of barcodes
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        # Open file, skip the headers and create a list of the iterator
        barcode_reader = csv.reader(csvfile, delimiter=",")
        next(barcode_reader, None)
        barcode_order_id = list(barcode_reader)

        # Create a order_id: [barcode,..] mapping without any duplicates and unused barcodes
        invalid_barcodes, invalid_order_ids = validate_order_barcodes(barcode_order_id)
        order_id_barcodes = defaultdict(list)
        for barcode, order_id in barcode_order_id:
            if barcode in invalid_barcodes or order_id in invalid_order_ids:
                continue
            order_id_barcodes[order_id].append(barcode)
        return order_id_barcodes


def write_combine_datasets(barcodes_file_path: Path, orders_file_path: Path, output_file_path: Path) -> list[list[typing.Sequence[str]]]:
    order_barcodes_mapping = load_order_barcodes_mapping(barcodes_file_path)
    combined = []
    empty_orders = []

    with (open(orders_file_path, newline="", encoding="utf-8") as csvfile, open(output_file_path, "w", encoding="utf-8") as output):
        # Open file, skip the headers and create a list of the iterator
        orders_reader = csv.reader(csvfile, delimiter=",")
        next(orders_reader, None)

        for order_id, customer_id in orders_reader:

            if order_id not in order_barcodes_mapping:
                # Since the validation of empty orders in orders.csv dataset is dependent of
                # the orders.csv dataset. I do the validation here when I have access to both
                # datasets.
                empty_orders.append(order_id)
                continue

            barcodes = order_barcodes_mapping[order_id]
            output.write(f"{customer_id}, {order_id}, {barcodes}\n")
            combined.append([customer_id, order_id, barcodes])

    if empty_orders:
        logger.error("(%s) Empty orders without barcodes, will not be used for customer data: %s", len(empty_orders), empty_orders)

    logger.info("Output file written")
    return combined


def get_top_customers(combined_dataset: list[list[Sequence[str]]], nr_of_customers: int) -> list[tuple[Any, int]]:
    # group the dataset on customer_id, use a Counter to keep track of how many
    # barcodes each customer have.
    # Returns top nr_of_customers as a dict, log results
    customers_barcode_counter = Counter()  # type: Counter
    for customer_id, customers in groupby(combined_dataset, lambda x: x[0]):
        for _, _, barcodes in list(customers):
            customers_barcode_counter[customer_id] += len(barcodes)

    top_customers = customers_barcode_counter.most_common(nr_of_customers)
    results = "\n".join([f"{customer_id}, {amount_of_tickets}" for customer_id, amount_of_tickets in top_customers])
    logger.info("Top %s customers and amount of tickets:\n%s", nr_of_customers, results)
    return top_customers


def main() -> int:
    this_path = Path(__file__).parent
    output_file_path = this_path / "output.csv"
    barcodes_file_path = this_path / "barcodes.csv"
    orders_file_path = this_path / "orders.csv"

    combined_dataset = write_combine_datasets(
        barcodes_file_path.absolute(),
        orders_file_path.absolute(),
        output_file_path.absolute(),
    )
    get_top_customers(combined_dataset, nr_of_customers=5)
    return 0


if __name__ == "__main__":
    sys.exit(main())
