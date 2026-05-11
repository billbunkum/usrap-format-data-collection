# FORMAT SPECIFIC FIELDS POST DATA COLLECTION INTO ViDA CODES

#############################################################################
# NOTES
#############################################################################

'''
1. Number_of_lanes -> how to deal with Undivided 3&2, 2&1 ???
2. Check Column names needed for ViDA
  - Currently using Column names form HIS Export, e.g. lots of __
3. Check EXPORT .csv for proper Column names

'''

#############################################################################
# IMPORTS
#############################################################################

import argparse # allows terminal commands, e.g. --test, --help
import csv
import numpy as np # type: ignore # this allows NaN args, e.g. np.nan
import sys # for passing terminal arguments

# PANDAS Docs: https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html
import pandas as pd # type: ignore

#############################################################################
# SETUP
#############################################################################

# Read in User's input file.csv as Panda dataframe -> batch
def get_batch():
  print("Type 'q' to quit to exit")
  
  while True:
    user_input = input('Enter .csv filename: ').strip()

    if user_input.lower() == 'q':
      print('Exiting program...')
      sys.exit()

    # Ensure .csv extension
    if not user_input.lower().endswith('.csv'):
      print('Remember the .csv extension')
      continue
    
    try:
      df = pd.read_csv(f'{user_input}', header='infer', skip_blank_lines=False, low_memory=False)
      print('File loaded and running')  
      return df
    except FileNotFoundError:
      print(f'File {user_input} not found. Try again.')

batch = get_batch()

#  batch = pd.read_csv('use-this-test-spatial.csv', header='infer', skip_blank_lines=False, low_memory=False)
##   batch = pd.read_csv('use-this-test-batch.csv', header='infer', skip_blank_lines=False, low_memory=False)

# Create copy of BATCH to avoid destructive changes
vida_batch = batch.copy()

#############################################################################
# FUNCTIONS CONVERT HIS FORMAT INTO ViDA NUMBERICAL CODES
#############################################################################

  # Letters are the corresponding Columns in the Excel sheets
  # Name is the HIS version of the ViDA name, e.g. Urban_Area_Census (HIS), Area_type (???)

# DUMMY data -> can add as Input
def coder_name():
  coder = 'Coder_name'
  vida_batch[f'{coder}'] = 'foo@gmail.com'

# DUMMY Data -> can add as Input
def road_survey_date():
  survey = 'Road_survey_date'
  vida_batch[f'{survey}'] = '20260420'

# DUMMY Data -> can add as Input
def landmark():
  landmark = 'Landmark'
  vida_batch[f'{landmark}'] = 'some landmark'

def area_type():
  # V: Urban_Area_Census -> gives info. as 'Rural' or 'Urban'
  area = 'Urban_Area_Census'
##  area = 'Area_type'
  mapping = {'Rural': 1, 'Urban': 2}
  vida_batch[f'{area}'] = vida_batch[f'{area}'].map(mapping)

def speed_limit():
  # W: Speed_Limit_Posted_MPH
  speed = 'Speed_Limit_Posted_MPH'
  limit = 'Speed_limit'

  vida_batch[f'{speed}'] = batch[f'{speed}'] 
  vida_batch[f'{limit}'] = batch[f'{speed}']
  series1 = vida_batch[f'{speed}']
  series2 = vida_batch[f'{limit}']

  speed_to_code(speed, series1)
  speed_to_code(limit, series2)

def motorcycle_speed_limit():
# X: as Speed limit
  speed = 'Speed_Limit_Posted_MPH'
  moto = 'Motorcycle_speed_limit'

  num = batch[f'{speed}']
  vida_batch[f'{moto}'] = num
  speed_to_code(moto, num)

def truck_speed_limit():
# Y: as Speed limit (unless listed)
  speed = 'Speed_Limit_Posted_MPH'
  truck = 'Truck_speed_limit'

  num = batch[f'{speed}']
  vida_batch[f'{truck}'] = num
  speed_to_code(truck, num)

def operating_speed_85th():
  # BQ: as Speed limit
  speed = 'Speed_Limit_Posted_MPH'
  operating = 'Operating_Speed__85th_percentile_'

  num = batch[f'{speed}']
  vida_batch[f'{operating}'] = num 
  speed_to_code(operating, num)

def operating_speed_mean():
  # BR: as Speed limit
  speed = 'Speed_Limit_Posted_MPH'
  mean = 'Operating_Speed__mean_'

  num = batch[f'{speed}']
  vida_batch[f'{mean}'] = num 
  speed_to_code(mean, num)

# CONVERT MPH speed etc into ViDA code
def speed_to_code(col, num):
  vida_batch[col] = np.select(
    [
      num >= 90,
      num >= 80,
      num >= 70,
      num >= 60,
      num >= 50,
      num >= 40,
      num >= 30,
      num < 30
    ],
    [45, 43, 41, 39, 37, 35, 33, 31]
  )

def differential_speed_limits():
  # Z: as Speed limit (unless listed)
  # code is either '1' (not present) or '2' (present)
  diff = 'Differential_speed_limits'
  # EXPLAIN: Replace empty Strings with NaN (Pandas doesn't treat '' as Missing)
  vida_batch[f'{diff}'] = vida_batch[f'{diff}'].replace('', np.nan)
  # EXPLAIN: .notna() -> True if value exists; .astype(int) -> True = 1, False = 0
    # +1 -> 0-1 not present; 1-2 present
  vida_batch[f'{diff}'] = vida_batch[f'{diff}'].notna().astype(int) + 1

def number_of_lanes(): # WORKING HERE
  # AO: 
  #  if Median_Type_of_Roadway = "Divided Highway" -> Lanes_Number_Cardinal
  #  if Median_Type_of_Roadway = "Undivided Highway" -> Lanes_Total_Number_Driving
  col = 'Number_of_lanes'
  cardinal = 'Lanes_Number_Cardinal'
  total_num = 'Lanes_Total_Number_Driving'
  median = 'Median_Type_of_Roadway'

  # Build filters for Divided and Undivided rows
  mask1 = batch[f'{median}'] == 'Divided Highway'
  mask2 = batch[f'{median}'] == 'Undivided Highway'
  
 # Apply correct fields from 'batch' to 'vida_batch'
  vida_batch.loc[mask1, f'{col}'] = batch.loc[mask1, f'{cardinal}']
  vida_batch.loc[mask2, f'{col}'] = batch.loc[mask2, f'{total_num}']

  number_of_lanes_to_code(col)

def number_of_lanes_to_code(col):
  # Assign ViDA CODES to fields in 'vida_batch'
  # Only Undivided (mask2) can gain code '5' and '6'

  series = vida_batch[col]
  # Only overwrite valid fields, e.g. not NaN or blank
  
  vida_batch[col] = np.select(
    [
      series >= 4,
      series == 3,
      series == 2,
      series == 1
    ],
    [4, 3, 2, 1],
    default = np.nan # Preserves Blanks from np.select assigning '0'
  )
  
''' number of lanes
4	four or more
3	three
6	three and two
2	two   
5	two and one
1	one
'''
 
def lane_width():
  # ap: lane_width_feet 
#  lane = 'lane_width' # for vida
  col = 'Lane_Width_Feet' # for export from arcgis
  lane_width = 'Lane_width'
  vida_batch[f'{lane_width}'] = batch[f'{col}']
  mask = vida_batch[f'{lane_width}']

  lane_width_to_code(lane_width, mask)

# convert lane_width_feet into vida code and place into 'lane_width'
def lane_width_to_code(col, mask):
  vida_batch[col] = np.select(
    [
      mask >= 10.66,
      mask >= 9.02,
      mask >= 0
    ],
    [1, 2, 3]
  )

'''
3	narrow (≥ 0m to < 2.75m) -> >= 0ft to < 9.02ft
2	medium (≥ 2.75m to < 3.25m) -> >= 9.02ft to < 10.66ft
1	wide (≥ 3.25m) -> >= 10.66ft

'''

def vehicle_flow(): # a.k.a. aadt
  # bk: traffic_last_count
  # the code for this is the number
  flow = 'Vehicle_flow__AADT_'
#  print(f'batch {flow} is: ', batch[f'{flow}'][5])
  mask = batch[f'{flow}'].notna()
  vida_batch.loc[mask, f'{flow}'] = batch.loc[mask, f'{flow}'] 
#  print(f'vida {flow} is: ', vida_batch[f'{flow}'][5])

def intersecting_road_volume():  
  # al: traffic_last_count / 2 (calculation)
    # in other words: vehicle_flow / 2
  vol = 'Intersecting_road_volume'
  flow = 'Vehicle_flow__AADT_'
  # explain: 'mask' becomes the series, can use .loc for if, or np.where(cond, true, false) for if/else
    # python if/else  won't work cos these are series' not singular values
  mask = batch[f'{flow}'].notna()
  # calculate vehicle flow (aadt) / 2 for each cell in intersecting road volume
  vida_batch.loc[mask, f'{vol}'] = batch.loc[mask, f'{flow}'] / 2
'''
## testing
  if vida_batch[f'{vol}'][0] == batch[f'{flow}'][0] / 2:
    print('worked!')
  else:
    print('did not work!')
'''

def motorcycle_percentile(): 
  # bl: code '0'
  moto = 'Motorcycle__'
  vida_batch[f'{moto}'] = 0

#############################################################################
# FUNCTION CALLS
#############################################################################

## dummy defs
coder_name()
road_survey_date()
landmark()

## real defs
area_type()
speed_limit() 
motorcycle_speed_limit() 
differential_speed_limits()
lane_width()
vehicle_flow()
intersecting_road_volume()
truck_speed_limit()
operating_speed_85th()
operating_speed_mean()
motorcycle_percentile()
number_of_lanes() ## QUESTION about Code 5 and 6 (Undivided) 

# export to .csv
vida_batch.to_csv('coded-file.csv', index=False)



#############################################################################
# PLAYGROUND
##############################################################################
'''
# trying to setup terminal feature for --test, --help, etc.
parser = argparse.argumentparser()
parser.add_argument("--test")
args = parser.parse_args()
'''

# column names from arcgis (some changed, e.g. area_type is urban_area_census)
arc_col_names = [
                 'coder_name',
                 'coding_date',
                 'road_survey_date',
                 'image_reference',
                 'road_name',
                 'section',
                 'distance',
                 'length',
                 'latitude',
                 'longitude',
                 'landmark',
                 'comments',
                 'carriageway',
                 'upgrade_cost',
                 'motorcycle_observed_flow',
                 'bicycle_observed_flow',
                 'pedestrian_observed_flow_across_the_road',
                 'pedestrian_observed_flow_along_the_road_driver_side',
                 'pedestrian_observed_flow_along_the_road_passenger_side',
                 'land_use___driver_side',
                 'land_use___passenger_side',
                 'area_type',
                 'speed_limit',
                 'motorcycle_speed_limit',
                 'truck_speed_limit',
                 'differential_speed_limits',
                 'median_type',
                 'centreline_rumble_strips',
                 'roadside_severity___driver_side_distance',
                 'roadside_severity___driver_side_object',
                 'roadside_severity___passenger_side_distance',
                 'roadside_severity___passenger_side_object',
                 'shoulder_rumble_strips',
                 'paved_shoulder___driver_side',
                 'paved_shoulder___passenger_side',
                 'intersection_type',
                 'intersection_channelisation',
                 'intersecting_road_volume',
                 'intersection_quality',
                 'property_access_points',
                 'number_of_lanes',
                 'lane_width',
                 'curvature',
                 'quality_of_curve',
                 'grade',
                 'road_condition',
                 'skid_resistance___grip',
                 'delineation',
                 'street_lighting',
                 'pedestrian_crossing_facilities___inspected_road',
                 'pedestrian_crossing_quality',
                 'pedestrian_crossing_facilities___intersecting_road',
                 'pedestrian_fencing',
                 'speed_management___traffic_calming',
                 'vehicle_parking',
                 'sidewalk___driver_side',
                 'sidewalk___passenger_side',
                 'service_road',
                 'facilities_for_motorised_two_wheelers',
                 'facilities_for_bicycles',
                 'roadworks',
                 'sight_distance',
                 'vehicle_flow__aadt_',
                 'motorcycle__',
                 'pedestrian_peak_hour_flow_across_the_road',
                 'pedestrian_peak_hour_flow_along_the_road_driver_side',
                 'pedestrian_peak_hour_flow_along_the_road_passenger_side',
                 'bicycle_peak_hour_flow',
                 'operating_speed__85th_percentile_',
                 'operating_speed__mean_',
                 'roads_that_cars_can_read',
                 'vehicle_occupant_star_rating_policy_target',
                 'Motorcycle_Star_Rating_Policy_Target',
                 'Pedestrian_Star_Rating_Policy_Target',
                 'Bicycle_Star_Rating_Policy_Target',
                 'Annual_Fatality_Growth_Multiplier',
                 'School_zone_warnin',
                 'School_zone_crossing_superviso',
                ]