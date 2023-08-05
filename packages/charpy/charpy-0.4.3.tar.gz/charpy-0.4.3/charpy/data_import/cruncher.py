from charpy.data_import.io_import import get_csv_data, DATA_PATH, ROOT_PATH
from charpy.data_import.converter import csv_semicolon_to_comma
import os

if __name__ == "__main__":  # pragma: no cover
    data = os.path.join(DATA_PATH, "pcbanking.csv")
    #csv_semicolon_to_comma(data)
    print(get_csv_data(data, transposed=True))
