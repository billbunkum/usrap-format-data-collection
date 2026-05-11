# format-dc.py
- Takes a .csv in 'spatial' format, i.e. exported from ArcGIS (after HIS data is included), converts all Data into ViDA codes.
- Changes Column names into ViDA format.

## NOTES
- V2.1 should take this one file and parse out all needed info., format, and export into proper SR4D format.
- V2.1.1 Begins logging missing cells but does not discriminate yet.
- V2.1.2 minor differences to startup and error messages
- V2.1.3 creates .csv of rows with MISSING data, only Cols that 'matter', e.g. not Comments.
- V2.2 will provide a “log file” with Rows that ONLY have REQUIRED missing data.

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
- Input for file\_name
- Exports various fields (depends on fields we need)
