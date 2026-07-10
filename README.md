# format-dc.py
- Takes a .csv in 'spatial' format, i.e. exported from ArcGIS (after HIS data is included), converts all Data into ViDA codes.
- Changes Column names into ViDA format.

## NOTES
...
Maybe need 'Option 5 - Remove Missing' (for Spatial)???

## VERSION NOTES
- Still need to know what file to run against and which Cols/format to export:
    Think it will be the "spatial" file with combined Batch and ArcGIS Cols
- V2.1 should take this one file and parse out all needed info., format, and export into proper SR4D format.
- V2.1.1 Begins logging missing cells but does not discriminate yet.
- V2.1.2 minor differences to startup and error messages
- V2.1.3 creates .csv of rows with MISSING data, only Cols that 'matter', e.g. not Comments.
- V2.2 will provide a “log file” with Rows that ONLY have REQUIRED missing data.
- V2.2.1 Fixes 'Speed limit' logic
- V2.2.2 Fixes 'Number of Lanes' logic
- V2.2.3 Start changes to workflow & features, i.e. Options '1' and '2'.
  - DID NOT DO THIS - Removes references to 'sr4d'
    - NOTE_: present Functions have if/else concerning `file_format` == 'sr4d'; this is DEPRECATED.
    - Begins internal work for 2.2.4, testing 
  - Option '1' to CHECK Spatial for Missing
    - USAGE_: Outputs a single Missing Log .csv
      - OUTPUT-ConvertSpatial--someFilename-MissingCellsLog.csv
    - User then needs to correct Missing Cells within a Spatial file
  - Option '2' to 'CONVERT Spatial to ViDA'
    - USAGE_: Outputs two .csv; 1 Missing Log, 1 CSV prepared for ViDA upload
    - will take a Spatial .csv as INPUT and OUTPUT a someFile.csv
    - if Missing Cells (in necessary Rows), will OUTPUT a 'Missing Cell Log' file + Warning Message (ViDA RPS will fail. Missing Rows. See Log file.)
- v2.3 Add workflow Feature, i.e. adds Option '3'.
  - Option '3' to 'CLEAN Spatial'
    - Removes unneeded Cols from Spatial file.
      - Workflow requires User to work from a Spatial file to make corrections, e.g. missing cells, incorrect data, etc., *not* a ViDA file.
- V2.3.1 Adds Option '4' to create a CSV with only Rows with Missing Cells
  - Only check for necessary Cols
  - Works with other options EXCEPT for Option '1' Check Spatial for Missing Cells

- V2.3.2 Addresses issues found during first real test with 056-spatial.csv
  - [ ] Might need dummy info for:
    - [ ] Coding Date??? (add Code for "today's" date???) --> TBD
    - [ ] Section??? --> TBD
  - [X] Ignore certain Fields for Option 1 'Check for Missing' when file_format is 'check_spatial'
    - [X] Area Type => derived from Urban_Area_Census
  - [X] Urban_Area_Census issues
    - [ ] FIX 1: May need a TEST block which checks for appropriate Data, not just Blank Fields
        Sometimes, HIS uses entry other than 'Rural' and 'Urban', e.g. `Louisville/Jefferson County etc.`
        This causes issue with Option 2 'Convert Spatial' as it thinks the Field is Blank.
        --> TBD
      [X] FIX 2: Auto-decide a DEFAULT value (ASK ALEX ON THIS) # ANCHOR / WORKING: Need Instruction
        Currently, default is 'Urban' if Field is not 'Rural'
      [X] ASK ALEX ABOUT FIX 2
  - [] SETUP needs REFACTOR into various DEF calls --> TBD

- V2.3.3 Fixing MISSING LOG
  - [X] Should include RT_UNIQUE ( Road Name)
  - [X] Should include Image Reference
'''

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
