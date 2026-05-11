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

file_format = None

# Read in User's input file.csv as Panda dataframe -> batch
def get_batch():
  global file_format
  print("Type 'q' to quit to exit")

  while True:
    user_choice = input('What format: choose (1) SR4D or (2) Spatial: ')
    if user_choice == '1':
      file_format = 'sr4d'
      
    elif user_choice == '2':
      file_format = 'spatial'

    else:
      print('That is not a format used.')
      sys.exit()
    
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
  if file_format == 'sr4d':
    coder = 'Coder name'
  else:
    coder = 'Coder_name'

  vida_batch[f'{coder}'] = 'foo@gmail.com'

# DUMMY Data -> can add as Input
def road_survey_date():
  if file_format == 'sr4d':
    survey = 'Road survey date'
  else:
    survey = 'Road_survey_date'

  vida_batch[f'{survey}'] = '20260420'

# DUMMY Data -> can add as Input
def landmark():
  landmark = 'Landmark'
  vida_batch[f'{landmark}'] = 'some landmark'

def area_type():
  # V: Urban_Area_Census -> gives info. as 'Rural' or 'Urban'
  if file_format == 'sr4d':
    area = 'Area type'
  else:
    area = 'Urban_Area_Census'

  mapping = {'Rural': 1, 'Urban': 2}
  vida_batch[f'{area}'] = vida_batch[f'{area}'].map(mapping)

def speed_limit():
  # W: Speed_Limit_Posted_MPH
  if file_format == 'sr4d':
    speed = 'Speed limit'
  else:
    speed = 'Speed_Limit_Posted_MPH'
    limit = 'Speed_limit'
    vida_batch[f'{limit}'] = batch[f'{speed}']
    series2 = vida_batch[f'{limit}']

    speed_to_code(limit, series2)

  vida_batch[f'{speed}'] = batch[f'{speed}'] 
  series1 = vida_batch[f'{speed}']

  speed_to_code(speed, series1)
 
def motorcycle_speed_limit():
# X: as Speed limit

  if file_format == 'sr4d':
    moto = 'Motorcycle speed limit'
    speed = 'Speed limit'

  else:
    moto = 'Motorcycle_speed_limit'
    speed = 'Speed_Limit_Posted_MPH'

  num = batch[f'{speed}']
  vida_batch[f'{moto}'] = num
  speed_to_code(moto, num)

def truck_speed_limit():
# Y: as Speed limit (unless listed)

  if file_format == 'sr4d':
    truck = 'Truck speed limit'
    speed = 'Speed limit'

  else:
    truck = 'Truck_speed_limit'
    speed = 'Speed_Limit_Posted_MPH'

  num = batch[f'{speed}']
  vida_batch[f'{truck}'] = num
  speed_to_code(truck, num)

def operating_speed_85th():
  # BQ: as Speed limit

  if file_format == 'sr4d':
    operating = 'Operating Speed (85th percentile)'
    speed = 'Speed limit'

  else:
    operating = 'Operating_Speed__85th_percentile_'
    speed = 'Speed_Limit_Posted_MPH'

  num = batch[f'{speed}']
  vida_batch[f'{operating}'] = num 
  speed_to_code(operating, num)

def operating_speed_mean():
  # BR: as Speed limit

  if file_format == 'sr4d':
    mean = 'Operating Speed (mean)'
    speed = 'Speed limit'

  else:
    mean = 'Operating_Speed__mean_'
    speed = 'Speed_Limit_Posted_MPH'

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
  if file_format == 'sr4d':
    diff = 'Differential speed limits'

  else:
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
  if file_format == 'sr4d':
    col = 'Number of lanes'
    cardinal = 'Lanes_Number_Cardinal'# This column needs to be added to SR4D
    total_num = 'Lanes_Total_Number_Driving' # This column needs to be added to SR4D
    median = 'Median type'

  else:
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
  if file_format == 'sr4d':
    col = 'Lane width'
    lane_width = 'Lane width'

  else:
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
  if file_format == 'sr4d':
    flow = 'Vehicle flow (AADT)'

  else:
    flow = 'Vehicle_flow__AADT_'
    #flow = 'Vehicle_flow'

  mask = batch[f'{flow}'].notna()
  vida_batch.loc[mask, f'{flow}'] = batch.loc[mask, f'{flow}'] 

def intersecting_road_volume():  
  # al: traffic_last_count / 2 (calculation)
    # in other words: vehicle_flow / 2
  if file_format == 'sr4d':
    vol = 'Intersecting road volume'
    flow = 'Vehicle flow (AADT)'

  else:
    vol = 'Intersecting_road_volume'
    flow = 'Vehicle_flow__AADT_'

  # explain: 'mask' becomes the series, can use .loc for if, or np.where(cond, true, false) for if/else
    # python if/else  won't work cos these are series' not singular values
  mask = batch[f'{flow}'].notna()
  # calculate vehicle flow (aadt) / 2 for each cell in intersecting road volume
  vida_batch.loc[mask, f'{vol}'] = batch.loc[mask, f'{flow}'] / 2

def motorcycle_percentile(): 
  # bl: code '0'
  if file_format == 'sr4d':
    moto = 'Motorcycle %'
  else:
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

# SR4D paired with ArcGIS col names:
sr4d_with_arcgis = {
    'Coder name': 'Coder_name',
    'Coding date': 'Coding_date',
    'Road survey date': 'Road_survey_date',
    'Image reference': 'Image_reference',
    'Road name': 'Road_name',
    'Section': 'Section',
    'Distance': 'Distance',
    'Length': 'Length',
    'Latitude': 'Latitude',
    'Longitude': 'Longitude',
    'Landmark': 'Landmark',
    'Comments': 'Comments',
    'Carriageway': 'Carriageway',
    'Upgrade cost': 'Upgrade_cost',
    'Motorcycle observed flow': 'Motorcycle_observed_flow',
    'Bicycle observed flow': 'Bicycle_observed_flow',
    'Pedestrian observed flow across the road': 'Pedestrian_observed_flow_across_the_road',
    'Pedestrian observed flow along the road driver-side': 'Pedestrian_observed_flow_along_the_road_driver_side',
    'Pedestrian observed flow along the road passenger-side': 'Pedestrian_observed_flow_along_the_road_passenger_side',
    'Land use - driver-side': 'Land_use___driver_side',
    'Land use - passenger-side': 'Land_use___passenger_side',
    'Area type': 'Urban_Area_Census',
    'Speed limit': 'Speed_limit',
    'Motorcycle speed limit': 'Motorcycle_speed_limit',
    'Truck speed limit': 'Truck_speed_limit',
    'Differential speed limits': 'Differential_speed_limits',
    'Median type': 'Median_type',
    'Centreline rumble strips': 'Centreline_rumble_strips',
    'Roadside severity - driver-side distance': 'Roadside_severity___driver_side_distance',
    'Roadside severity - driver-side object': 'Roadside_severity___driver_side_object',
    'Roadside severity - passenger-side distance': 'Roadside_severity___passenger_side_distance',
    'Roadside severity - passenger-side object': 'Roadside_severity___passenger_side_object',
    'Shoulder rumble strips': 'Shoulder_rumble_strips',
    'Paved shoulder - driver-side': 'Paved_shoulder___driver_side',
    'Paved shoulder - passenger-side': 'Paved_shoulder___passenger_side',
    'Intersection type': 'Intersection_type',
    'Intersection channelisation': 'Intersection_channelisation',
    'Intersecting road volume': 'Intersecting_road_volume',
    'Intersection quality': 'Intersection_quality',
    'Property access points': 'Property_access_points',
    'Number of lanes': 'Number_of_lanes',
    'Lane width': 'Lane_width',
    'Curvature': 'Curvature',
    'Quality of curve': 'Quality_of_curve',
    'Grade': 'Grade',
    'Road condition': 'Road_condition',
    'Skid resistance / grip': 'Skid_resistance___grip',
    'Delineation': 'Delineation',
    'Street lighting': 'Street_lighting',
    'Pedestrian crossing facilities - inspected road': 'Pedestrian_crossing_facilities___inspected_road',
    'Pedestrian crossing quality': 'Pedestrian_crossing_quality',
    'Pedestrian crossing facilities - intersecting road': 'Pedestrian_crossing_facilities___intersecting_road',
    'Pedestrian fencing': 'Pedestrian_fencing',
    'Speed management / traffic calming': 'Speed_management___traffic_calming',
    'Vehicle parking': 'Vehicle_parking',
    'Sidewalk - driver-side': 'Sidewalk___driver_side',
    'Sidewalk - passenger-side': 'Sidewalk___passenger_side',
    'Service road': 'Service_road',
    'Facilities for motorised two wheelers': 'Facilities_for_motorised_two_wheelers',
    'Facilities for bicycles': 'Facilities_for_bicycles',
    'Roadworks': 'Roadworks',
    'Sight distance': 'Sight_distance',
    'Vehicle flow (AADT)': 'Vehicle_flow__AADT_',
    'Motorcycle %': 'Motorcycle__',
    'Pedestrian peak hour flow across the road': 'Pedestrian_peak_hour_flow_across_the_road',
    'Pedestrian peak hour flow along the road driver-side': 'Pedestrian_peak_hour_flow_along_the_road_driver_side',
    'Pedestrian peak hour flow along the road passenger-side': 'Pedestrian_peak_hour_flow_along_the_road_passenger_side',
    'Bicycle peak hour flow': 'Bicycle_peak_hour_flow',
    'Operating Speed (85th percentile)': 'Operating_Speed__85th_percentile_',
    'Operating Speed (mean)': 'Operating_Speed__mean_',
    'Roads that cars can read': 'Roads_that_cars_can_read',
    'Vehicle Occupant Star Rating Policy Target': 'Vehicle_Occupant_Star_Rating_Policy_Target',
    'Motorcycle Star Rating Policy Target': 'Motorcycle_Star_Rating_Policy_Target',
    'Pedestrian Star Rating Policy Target': 'Pedestrian_Star_Rating_Policy_Target',
    'Bicycle Star Rating Policy Target': 'Bicycle_Star_Rating_Policy_Target',
    'Annual Fatality Growth Multiplier': 'Annual_Fatality_Growth_Multiplier',
    'School zone warning': 'School_zone_warning',
    'School zone crossing supervisor': 'School_zone_crossing_supervisor'
}

# SR4D col names
sr4d_col_names = { 
  'Coder name': ...,
  'Coding date': ...,
  'Road survey date': ...,
  'Image reference': ...,	
  'Road name': ...,	
  'Section': ...,	
  'Distance': ...,
  'Length': ...,
  'Latitude': ...,
  'Longitude': ...,
  'Landmark': ...,
  'Comments': ...,
  'Carriageway': ...,
  'Upgrade cost': ...,
  'Motorcycle observed flow': ...,
  'Bicycle observed flow': ...,
  'Pedestrian observed flow across the road': ...,
  'Pedestrian observed flow along the road driver-side': ...,
  'Pedestrian observed flow along the road passenger-side': ...,	
  'Land use - driver-side': ...,
  'Land use - passenger-side': ...,	
  'Area type': ...,	
  'Speed limit': ...,	
  'Motorcycle speed limit': ...,
  'Truck speed limit': ...,	
  'Differential speed limits': ...,
  'Median type': ...,	
  'Centreline rumble strips': ...,
  'Roadside severity - driver-side distance': ...,	
  'Roadside severity - driver-side object': ...,
  'Roadside severity - passenger-side distance': ...,
  'Roadside severity - passenger-side object': ...,	
  'Shoulder rumble strips': ...,
  'Paved shoulder - driver-side': ...,	
  'Paved shoulder - passenger-side': ...,	
  'Intersection type': ...,	
  'Intersection channelisation': ...,	
  'Intersecting road volume': ...,	
  'Intersection quality': ...,	
  'Property access points': ...,	
  'Number of lanes': ...,	
  'Lane width': ...,	
  'Curvature': ...,	
  'Quality of curve': ...,	
  'Grade': ...,
  'Road condition': ...,
  'Skid resistance / grip': ...,	
  'Delineation': ...,	
  'Street lighting': ...,	
  'Pedestrian crossing facilities - inspected road': ...,	
  'Pedestrian crossing quality': ...,	
  'Pedestrian crossing facilities - intersecting road': ...,	
  'Pedestrian fencing': ...,	
  'Speed management / traffic calming': ...,	
  'Vehicle parking': ...,	
  'Sidewalk - driver-side': ...,	
  'Sidewalk - passenger-side': ...,	
  'Service road': ...,	
  'Facilities for motorised two wheelers': ...,	
  'Facilities for bicycles': ...,	
  'Roadworks': ...,	
  'Sight distance': ...,	
  'Vehicle flow (AADT)': ...,	
  'Motorcycle %': ...,	
  'Pedestrian peak hour flow across the road': ...,	
  'Pedestrian peak hour flow along the road driver-side': ...,
  'Pedestrian peak hour flow along the road passenger-side': ...,	
  'Bicycle peak hour flow': ...,	
  'Operating Speed (85th percentile)': ...,	
  'Operating Speed (mean)': ...,	
  'Roads that cars can read': ...,	
  'Vehicle Occupant Star Rating Policy Target': ...,	
  'Motorcycle Star Rating Policy Target': ...,	
  'Pedestrian Star Rating Policy Target': ...,	
  'Bicycle Star Rating Policy Target': ...,	
  'Annual Fatality Growth Multiplier': ...,	
  'School zone warning': ...,	
  'School zone crossing supervisor': ...
}

'''
# spatial_cols

  'OBJECTID'
  'Join_Count'
  'DISTANCE2'
  'TARGET_FID'
  'Coder_name'
  'Coding_date'
  'Road_survey_date'
  'Image_reference'
  'Road_name'
  'Section'
  'Distance'
  'Length'
  'Latitude'
  'Longitude'
  'Landmark'
  'Comments'
  'Carriageway'
  'Upgrade_cost'
  'Motorcycle_observed_flow'
  'Bicycle_observed_flow'
  'Pedestrian_observed_flow_across_the_road'
  'Pedestrian_observed_flow_along_the_road_driver_side'
  'Pedestrian_observed_flow_along_the_road_passenger_side'
  'Land_use___driver_side'
  'Land_use___passenger_side'
  'Area_type'
  'Speed_limit'
  'Speed_Limit_Posted_MPH'
  'Motorcycle_speed_limit'
  'Truck_speed_limit'
  'Differential_speed_limits'
  'Median_type'
  'Centreline_rumble_strips'
  'Roadside_severity___driver_side_distance'
  'Roadside_severity___driver_side_object'
  'Roadside_severity___passenger_side_distance'
  'Roadside_severity___passenger_side_object'
  'Shoulder_rumble_strips'
  'Paved_shoulder___driver_side'
  'Paved_shoulder___passenger_side'
  'Intersection_type'
  'Intersection_channelisation'
  'Intersecting_road_volume'
  'Intersection_quality'
  'Property_access_points'
  'Number_of_lanes'
  'Lane_width'
  'Curvature'
  'Quality_of_curve'
  'Grade'
  'Road_condition'
  'Skid_resistance___grip'
  'Delineation'
  'Street_lighting'
  'Pedestrian_crossing_facilities___inspected_road'
  'Pedestrian_crossing_quality'
  'Pedestrian_crossing_facilities___intersecting_road'
  'Pedestrian_fencing'
  'Speed_management___traffic_calming'
  'Vehicle_parking'
  'Sidewalk___driver_side'
  'Sidewalk___passenger_side'
  'Service_road'
  'Facilities_for_motorised_two_wheelers'
  'Facilities_for_bicycles'
  'Roadworks'
  'Sight_distance'
  'Vehicle_flow__AADT_'
  'Motorcycle__'
  'Pedestrian_peak_hour_flow_across_the_road'
  'Pedestrian_peak_hour_flow_along_the_road_driver_side'
  'Pedestrian_peak_hour_flow_along_the_road_passenger_side'
  'Bicycle_peak_hour_flow'
  'Operating_Speed__85th_percentile_'
  'Operating_Speed__mean_'
  'Roads_that_cars_can_read'
  'Vehicle_Occupant_Star_Rating_Policy_Target'
  'Motorcycle_Star_Rating_Policy_Target'
  'Pedestrian_Star_Rating_Policy_Target'
  'Bicycle_Star_Rating_Policy_Target'
  'Annual_Fatality_Growth_Multiplier'
  'School_zone_warning'
  'School_zone_crossing_supervisor'
  'Smoothed_Section_ID'
  'Vehicle_SRS_Run_Off_LOC_Driver_Side'
  'Vehicle_SRS_Run_Off_LOC_Passenger_Side'
  'Vehicle_SRS_Head_On_LOC'
  'Vehicle_SRS_Head_On_Overtaking'
  'Vehicle_SRS_Intersection'
  'Vehicle_SRS_Property_Access'
  'Vehicle_SRS_Total'
  'Vehicle_SRS_Total_Smoothed'
  'Vehicle_Star_Rating_Raw'
  'Vehicle_Star_Rating_Smoothed'
  'Motorcyclist_SRS_Run_Off_LOC_Driver_Side'
  'Motorcyclist_SRS_Run_Off_Passenger_Side'
  'Motorcyclist_SRS_Head_On_LOC'
  'Motorcyclist_SRS_Head_On_Overtaking'
  'Motorcyclist_SRS_Intersection'
  'Motorcyclist_SRS_Property_Access'
  'Motorcyclist_SRS_Along'
  'Motorcyclist_SRS_Total'
  'Motorcyclist_SRS_Total_Smoothed'
  'Motorcyclist_Star_Rating_Raw'
  'Motorcyclist_Star_Rating_Smoothed'
  'Pedestrian_SRS_Along'
  'Pedestrian_SRS_Crossing_Intersecting_Road'
  'Pedestrian_SRS_Crossing_Inspected_Road'
  'Pedestrian_SRS_Total'
  'Pedestrian_SRS_Total_Smoothed'
  'Pedestrian_Star_Rating_Raw'
  'Pedestrian_Star_Rating_Smoothed'
  'Bicyclist_SRS_Along'
  'Bicyclist_SRS_Intersection'
  'Bicyclist_SRS_Run_Off'
  'Bicyclist_SRS_Total'
  'Bicyclist_SRS_Total_Smoothed'
  'Bicyclist_Star_Rating_Raw'
  'Bicyclist_Star_Rating_Smoothed'
  'Route_Unique_Identifier'
  'Length_1'
  'Type_Operation_Code'
  'Begin_Milepoint'
  'End_Milepoint'
  'Road_Name_1'
  'Ownership_Status'
  'Last_Update_Date'
  'Extraction_Date'
  'Route'
  'County_Number'
  'Route_Prefix'
  'Route_Number'
  'Route_Suffix'
  'Route_Section'
  'Route_Type'
  'Route_Label'
  'Road_Shield_Label'
  'County_Name'
  'Route_Unique_Identifier_Web'
  'City_Name'
  'District'
  'Mid_Milepoint'
  'Length_Miles_DMI'
  'Length_Feet_DMI'
  'Access_Control_Type'
  'Appalachian_Hwy_Route_Sequence'
  'Appalachian_Hwy_Begin_Descripti'
  'Appalachian_Hwy_Corridor'
  'Appalachian_Hwy_Section_Length_'
  'Appalachian_Hwy_End_Description'
  'Appalachian_Hwy_Section_ID'
  'Appalachian_Hwy_Roadway_Status'
  'Coal_Haul_Annual_Tons_Cardinal'
  'Coal_Haul_Annual_Tons_NonCardin'
  'Extended_Weight_System'
  'Forest_Hwy_Route_Description'
  'Forest_Hwy_Route_Number'
  'Forest_Hwy_Route_Sequence'
  'Forest_Hwy_System'
  'Forest_Hwy_Road'
  'Federal_System_Route_Descriptio'
  'Enhanced_National_Hwy_System'
  'Functional_Class'
  'National_Hwy_System'
  'Federal_System_Roadway_Status'
  'Strategic_Hwy_Network'
  'National_Hwy_System_Terminal'
  'Urban_Area_Census'
  'Government_Level'
  'Grade_Absolute_Difference'
  'Grade_Class'
  'Grade_Direction'
  'Grade_Percent'
  'Grade_Incoming'
  'Grade_Outgoing'
  'Horizontal_Curve_Class'
  'Horizontal_Curve_Degree'
  'Horizontal_Curve_Direction'
  'Horizontal_Curve_SuperElevation'
  'Horizontal_Curve_SuperElevati_1'
  'Freight_Network_KY_Designation'
  'Lanes_Total_Number_Driving'
  'Lane_Width_Feet'
  'Lanes_Number_Cardinal'
  'Lanes_Number_NonCardinal'
  'Median_Barrier_Type'
  'Median_Type_1'
  'Median_Width_Feet'
  'Median_Type_of_Roadway'
  'NATL_Freight_Critical_Corridor_'
  'NATL_Freight_Designation'
  'NATL_Truck_Network_Commercial_V'
  'NATL_Truck_Network_Route_Descri'
  'NATL_Truck_Network_Route_Sequen'
  'Shoulder_Type_Cardinal_Right'
  'Shoulder_Width_Feet_Cardinal_Ri'
  'Shoulder_Surface_Width_Feet_Car'
  'Shoulder_Type_Cardinal_Left'
  'Shoulder_Width_Feet_Cardinal_Le'
  'Shoulder_Surface_Width_Feet_C_1'
  'Shoulder_Type_NonCardinal_Left'
  'Shoulder_Width_Feet_NonCardinal'
  'Shoulder_Surface_Width_Feet_Non'
  'Shoulder_Type_NonCardinal_Right'
  'Shoulder_Width_Feet_NonCardin_1'
  'Shoulder_Surface_Width_Feet_N_1'
  'Speed_Limit_Official_Order'
  'Speed_Limit_Posted_MPH'
  'State_System_Proposed_Deletion'
  'State_System_Classification'
  'State_System_Toll_Road'
  'Traffic_ADT_Station'
  'Traffic_ADT_Station_Type'
  'Traffic_Last_Count'
  'Traffic_Last_Count_Year'
  'Traffic_ADT_Source'
  'Truck_Weight_Route_Description'
  'Truck_Weight_Route_Sequence'
  'Truck_Weight_Limit_Class'
  'Snow_Ice_Priority_Route_Type'
  'Surface_Type'
  'Type_Operation'
  'Process_BMP'
  'Process_EMP'

'''