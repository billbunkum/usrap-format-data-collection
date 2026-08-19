# format-dc.py
- Takes a .csv in 'spatial' format, i.e. exported from ArcGIS (after HIS data is included), converts all Data into ViDA codes.
- Changes Column names into ViDA format.

## NOTES
...

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

- V2.3.4 BETA
  - [X] !!!Critical Bug - Option 5 is killing 'Image Reference' somehow!!!
  - [X] Fix Col name Errors shown by ViDA
  - [X] Deal with Col names ViDA claims need values - might be User error with ViDA site in choosing Dataset
  - [X] Correct Col 38 'Intersecting Road Volume' - add ViDA calc (we missed)
  - [X] Add Option 5 'Strip Missing Rows for ViDA'
    - [-] IDEA 1: read in 'missing-only' CSV as a 2nd batch();  a DEF uses the 'Image reference' to create a Mask; remove these Rows and OUTPUT a 'stripped' CSV
    - [X] IDEA 2: add onto `whitelist_cols()` with a `file_format` IF/ELSE clause; create a Mask with `.isna()` based on Whitelisted `keys`
  - [] SETUP needs REFACTOR into various DEF calls --> TBD
  - [X] Roads Cars Can Read set to ViDA Code '1' => Meets Specifications
  - [X] TEST - Make sure that Option 4 'create missing only' matches up with Option 1 'check spatial for missing log' and Option 2 'missing log'
    - RESULT 1 - Option 1 and 4 MATCH; they are both 'spatial' format
      Option 2 does NOT match and also only shows 'Number of Lanes' and 'AADT' because it is 'vida' format
      - [X] Check to see if Option 2 is catching everything it should
  - [] Option 5 'strip missing' does NOT strip 'Number of Lanes' (maybe others)
  - [X] Feature => check 'Median_type' to determine 'Median_Type_of_Roadway' if the latter is Missing.

- V2.4
  - [] Default value of 6 for: "...star target" Fields
  - [] Default value of 1 for 'Annual Fatality...' Field
  - [] Feature --> extrapolate any missing 'Speed...' Field
      - Use RT_UNIQUE, if same previous/proceeding
  - [] Feature --> extrapolate missing 'Lane Width...' Field
      - Use RT_UNIQUE, if same previous/proceeding
  - [] Reconfigure --> 'Intersection...' Fields to favor 'Intersection Type'
      - If 'Intersection Type' is None (12?) then convert 'AADT', 'Intersection Quality', 'Intersection Channelisation' to None (???) as well
  - [] CHECK --> Option 5 'strip missing' strips
      - 'Number of Lanes'
      - 'Lane Width'
      - 'AADT'
      - 'Speed limit'
  - [] CHECK --> Bug in 'Speed limit' value, Validation Report says value '35' needed when it exists; maybe Typer Error? with Pandas?

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
- Script is inteded to take a .CSV in 'spatial' format and to work from there until Option 2 'Convert Spatial (into ViDA)' is used.

## SCRIPT BREAKDOWN
1. v2.3.4 - There are 4 Options:
- 1 - check spatial (for missing cells)
- 2 - convert spatial
- 3 - clean spatial
- 4 - create 'missing only' CSV

2. These Options entirely dictate the Script - they determine 1 or 2 global variables used in If/Else clauses throughout.
- user_choice -> the option number
- file_format -> `vida` or `spatial`
- filetype_user_input -> used in Option 4 (create missing)
  - This is due to current Refactoring, the ability to reuse `whitelist_cols()` 
- user_input -> used to ensure a .CSV and also to dynamically name OUTPUT files

3. The main function of the Script is to format 'spatial' Column names into 'vida' naming, and also to format values into 'vida code.' This is done with Option 2 'Convert Spatial' and is accomplished by taking a .CSV spreadsheet as `batch`; it then converts values from it to `vida_batch`
- The other Options are for 'workflow', as Option 2 is the last step before achieving an RPS from the vida website.
    Of course, there will likely be Errors returned, hence the other Options so the User can investigate/troubleshoot those Errors more easily.
- To avoid certain Bugs/Errors inherent with Pandas, a function may `.copy()` this `batch` df as needed

### convert spatial
- runs most of the function calls

## FUTURE FEATURES
- Will run with Python package (so user does not need to independently download)
- Input for file\_name
- Exports various fields (depends on fields we need)
