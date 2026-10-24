# format-dc.py

[Dropbox][1]<link here>

Format dc => format Data Collection, a.k.a. "format script"
"DC" => Data Collection

Takes a .csv in 'spatial' format, i.e. exported from ArcGIS (after HIS data is included).
Converts all Data into ViDA codes.
Extrapolates some data from neighboring Rows with identical RT_Unique (Road name) and fills in eligible missing fields.
Exports various .CSVs to aid in workflow for correcting ERRORS during Data Collection and also for data missing from HIS.
Changes Column names into ViDA format.
Outputs a .CSV in "ViDA" format which can be uploaded to the ViDA site to gain SRS.


## USAGE
- Need Python v3 downloaded
- Need two files in the same directory:
  - _format-dc.py_ and _file-you're-working-on.csv_

- Open Terminal (or CMD), navigate to the folder with: _format-dc.py_
- Type: `python format-dc.py`
- script runs and will export: _OPTION-chosen-filename.csv_ and sometimes a second file.
  Filenames will begin with the "Option" you just selected. In this way, you can track your progress.

- **ATTENTION**:
  Script is inteded to take a .CSV in 'spatial' format and to work from there until Option 2 'Convert Spatial (into ViDA)' is used.

- Use in tandem with _street-view-viewer.py_
  [Github][1]<link here>
  [Dropbox][2]<link here>
  This CLI script will ingest the .CSV output from Option 1 Check Spatial for Missing and allow the User to easily open Google Street View for those missing Rows.

## WORKFLOW
Use the Script in the following fashion:

STEPS:
- Option 3: clean spatial

- Option 6: guess missing*
  - No "guessing" actually occurs, see "NOTES" below.

- Option 1: check spatial for missiing
  - User can add 'missing data' to this file and then easily copy/paste it to 'Option-6...WORKFILE' before steps 4 and 2.

- Option 4: create missing only CSV

- Option 2: convert spatial to ViDA format
  - The last step. "Format-dc" only works with files in 'spatial' format.

- Option 5*: strip missing -> **under construction**

## MANUAL POSTPROCESSING
This step is needed, e.g. when HIS does not have Speed data, Number of Lanes, etc.
Manual edits should be done in the _spatial_ formats and "Work files", then the Option 2 "Convert Spatial to ViDA" will operate correctly.
If you edit a file in ViDA format, that is okay as well, but _never_ edit the Column names.

Some fields can be _defaulted_ values:
- Urban_Area_Census: Urban
- ...

Most "default" fields are handled by script, e.g. Coding Date

Uncertain what to do if there is no GOOGLE STREET VIEW or PHOTOLOG VIEW

## NOTES
### convert spatial
- runs most of the function calls
- Option 5 'Strip Missing' takes care of MISSING Fields (WiP)
- Option 6 'Guess Missing' -> does not actually "guess" anything. 
  It finds Missing Fields and looks at the preceeding RT_UNIQUE, if it's the same, it will use that value (or will base a value off the Fields there, e.g. Intersection Type 12 'None' will make Vehicle Flow (AADT) 0). If the preceeding RT_UNIQUE is different, it will look at the proceeding RT_UNIQUE and do it that way. The Option fails if the Row is unique.
- Despite Option 6 'Guess Missing' there may be MISSING Fields as well as ERRONEOUS Combinations.
- 'intersection_checks()' bases several things off Intersection Type = 12 'None'. Some will fail (not throw an Error) if there an Intersection Type was coded, i.e. not 12, but HIS had no data for 'Intersecting_road_volume' - that is, the code will work properly but does not yet account for 'Intersection Type' other than 12 'None'.
- To avoid certain Bugs/Errors inherent with Pandas, a function may `.copy()` this `batch` df as needed

### WiP NOTES
- [X] Option 6 Guess 'Number_of_lanes'
  - Median_Type_of_Roadway: "Divided Highway" -> Lanes_Number_Cardinal
  - Median_Type_of_Roadway: "Undivided Highway" -> Lands_Total_Number_Driving

- [] Option 5 'Strip Missing' - failing to eliminate 'Number_of_lanes'
  **NOTE**:
  This option is not working correctly as of V2.5

