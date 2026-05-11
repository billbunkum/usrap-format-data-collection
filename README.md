# format-dc.py

## NOTES
- “Format” script v2 works but needs to know what file to run against and which Cols/format to export.
- V2.1 will do this.
- V2.2 will provide a “log file” with Rows that have missing data.


## Format Data Collection
Takes a .csv exported from ArcGIS (after HIS data is included), converts all Data into ViDA codes.

## TESTING
- use _format-dc.py_
- file: _use-this-test-batch.csv_
- file: _use-this-test-spatial.csv_
- exports: _coded-file.csv_

## USAGE
- Need Python v3 downloaded
- Need two files in the same directory:
  - _format-dc.py_ and _whatever.csv_
  - Open Terminal (or CMD), navigate to the folder with: _format-dc.py_
  - Type: __python format-dc.py__
  - script runs and will export: _coded-file.csv_

## FUTURE FEATURES
- Will run with Python package (so user does not need to independently download)
- Input for file_name
- Exports various fields (depends on fields we need)