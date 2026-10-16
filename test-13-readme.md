# Test 13 Readme

...'Image Reference' aka RT_Unique is corrupted...should not matter but is something to note about switching data types, .csv and .xlsx

## Take Aways
...
- If RT_Unique is same for Rows with missing data, there's no way to get extrapolate that data (see [Issue #1 below][1]).
  - Fix? Potentially a _default_ value for columns like, e.g. Lane_Width_Feet

## Attempt 1
Testing `SHIFT2026NewRutRegional-control-TESTING-20261015.csv` (called `newrut-1.csv` in main dir for ease).

1. Option 3 "Clean Spatial"
Immediately throws `KeyError` on several columns:
`
KeyError: "['Coder_name', 'Lane_Width_Feet', 'Lanes_Number_Cardinal', 'Lanes_Total_Number_Driving', 'Median_Type_of_Roadway', 'Median_Width_Feet', 'Speed_Limit_Posted_MPH', 'Traffic_Last_Count', 'Urban_Area_Census'] not in index"
`

'Coder_name' is present, but Pandas is skipping it for "index" crap.
Other cols are not present.

### FIX
Manually enter _all_ of the cols (including a second 'Coder_name').

2. Option 6 "Guess Missing"
Works but...there is no HIS data, so the original file _won't work_. Whoops.

## Attempt 2
Changing file to `SHIFT2026NewRutRegional_SpatialJoin_Flatten-withHIS-TESTEFILE.csv` as it _has_ HIS data and thus the correct Columns. Changing name to `newrut-2.csv` for ease.

1. Option 3 "Clean Spatial"
- No errors!

2. Option 6 "Guess Missing"
- No errors!
- **[ISSUE #1][1]** Looks like a _missing_ 'Lane_Width_Feet' at 16934 and 16935: guessing missed this because...
  - RT_Unique for both rows, 16934 and 16935, are the _same_: `008-I -0075  -531`, so "guessing" logic will not make up values; it would grab the previous or proceeding, but if those are the only two Rows in that RT_Unique, then the information is simply _not there_.

3. Option 1 "Check Spatial for Missing Cells"
- No errors!
- Showing 1720 missing fields (out of 17441 rows, i.e. well over 1,249,042 fields...lots!)
  - Lanes_Number_Cardinal
  - Lanes_Total_Number_Driving
  - Median_Width_Feet
  - Median_Type_of_Roadway
  - Lane_Width_Feet
  - Distance
  - Speed_Limit_Posted_MPH
  - Traffic_Last_Count

4. Option 4 "Create Missing Only"
- No errors!
- Looks solid.

5. Option 2 "Convert Spatial to ViDA"
- TypeError, looks like on `intersecting_road_volume()`
  - "Traffic_Last_Count" has both _blanks_ and `0`s - this may be the issue because there is a division by 2 here.
  A more likely culprit is the "data type" is something other than a `Float`.
  - **FIX**. In `intersecting_road_volume()`, I used `.round().astype('Int64')`

- In the "WORK-FILE" generated:
  - Finding more "pairs of fields" with the same RT_Unique's and missing fields:
    - Motorcycle__
    - Median_Width_Feet
    - Median_Type_of_Roadway
    - Lane_width (no problem)
    - Speed_Limit_Posted_MPH
  ***
    - The disconcerting thing is, the other "speed limit" fields are filled...which should be based off the Speed_Limit_Posted_MPH???

  - Oddly, a single Row missing:
    - Lanes_Number_Cardinal
    - Lanes_Total_Number_Driving

- In the "LOG-MISSING-CELLS" generated:
  - Speed limit
  - Motorcycle speed limit
  - Truck speed limit
  - Operating Speed (85th percentile)
  - Operating Speed (mean)
  - Distance
  - Lane width
  - Vehicle flow (AADT) -> mostly same RT_Uniques
  - Number of lanes -> all the same RT_Uniques

  - QUESTIONS:
    - Row: 14565 does not have "Vehicle flow (AADT)" yet previous Rows with same RT_Unique do, and they also don't have "Traffic_Last_Count"
    BUT! It is the _last_ Row before the RT_Unique changes...this points to the way `guess_missing` works. It may be over-riding itself at the proceeding Row.