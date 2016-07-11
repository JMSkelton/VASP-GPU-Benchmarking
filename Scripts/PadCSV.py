#PadCSV.py by J. M. Skelton


import argparse;
import csv;
import os;


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Rewrite CSV files to pad rows to a consistent length; original files are renamed to *.old.*.");
    
    parser.set_defaults(
        OverwriteOriginal = False
        );
    
    parser.add_argument(
        metavar = "csv_file", type = str, nargs = '+',
        dest = 'CSVFiles',
        help = "CSV files to process"
        );
    
    parser.add_argument(
        "--overwrite_original",
        dest = "OverwriteOriginal", action = 'store_true',
        help = "Directly overwrite original files, rather than renaming *.* -> *.old.* (default: False)"
        );
    
    args = parser.parse_args();
    
    for csvFile in args.CSVFiles:
        csvRows = None;

        with open(csvFile, 'r') as inputReader:
            csvRows = [row for row in csv.reader(inputReader)];
    
        if not args.OverwriteOriginal:
            head, tail = os.path.split(csvFile);
            root, ext = os.path.splitext(tail);

            os.rename(
                csvFile,
                os.path.join(head, "{0}.old.{1}".format(root, ext[1:]))
                );

        maxRowLength = max(len(row) for row in csvRows);

        with open(csvFile, 'w') as outputWriter:
            outputWriterCSV = csv.writer(outputWriter, delimiter = ',', quotechar = '\"', quoting = csv.QUOTE_ALL);

            for row in csvRows:
                outputWriterCSV.writerow(
                    row + [""] * (maxRowLength - len(row))
                    );
