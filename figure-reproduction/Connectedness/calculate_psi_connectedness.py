import numpy as np, pandas as pd, matplotlib.pyplot as plt, matplotlib as mpl, seaborn as sns
import math, string, re, pickle, json, os, sys, datetime, itertools
from collections import Counter
from tqdm import tqdm

import geopandas as gpd
from shapely.geometry import Point

import pygeohash as pgh
import warnings
warnings.filterwarnings("ignore", message=".*'iloc' is deprecated.*")
pd.options.mode.chained_assignment = None
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load in zipcode shapefile
zipcodes = gpd.read_file('data/tl_2019_us_zcta510.zip')
# https://www2.census.gov/geo/tiger/TIGER2019/ZCTA5/

def calculate_psi_connectedness(location_code):
  file_name = 'data/stays2_'+location_code+'.csv.gz'
  stays = pd.read_csv(file_name)
  users = stays.groupby('user')[['home_lon_med', 'home_lat_med']].median()
#   users = users.sample(frac=0.2)


  # Convert the df DataFrame to a GeoDataFrame
  crs = {'init': 'epsg:4326'}
  geometry = [Point(xy) for xy in zip(users.home_lon_med, users.home_lat_med)]
  geo_users = gpd.GeoDataFrame(users, crs=crs, geometry=geometry)

  # Perform spatial join
  joined = gpd.sjoin(geo_users, zipcodes, op='within')

  # Extract zip codes and merge with original DataFrame
  geo_users['zipcode'] = joined['ZCTA5CE10']


  user_to_homezip = geo_users[['zipcode']].to_dict()['zipcode']
  user_to_homezip = {k:v for k,v in user_to_homezip.items() if not pd.isna(v)}
  print("Number of users with zip codes", len(user_to_homezip), geo_users['zipcode'].str.slice(0, 3).value_counts().sort_index())

  # Filter out users who are not active
  geo_users['length'] = stays.groupby('user').apply(len)
  valid_users = list(geo_users[geo_users['length'] > 100].index)
  print("# Valid users", len(valid_users))
  filtered_stays = stays[stays['user'].isin(valid_users)]

  # Approx 2 min runtime to geohash
  filtered_stays['geohash9'] = filtered_stays[['lon_medoid', 'lat_medoid']].apply(lambda x: pgh.encode(*x,9), axis=1)
  filtered_stays['geohash8'] = filtered_stays['geohash9'].str.slice(0, 8)
  filtered_stays['geohash7'] = filtered_stays['geohash8'].str.slice(0, 7)
  filtered_stays['geohash6'] = filtered_stays['geohash7'].str.slice(0, 6)
  filtered_stays['geohash5'] = filtered_stays['geohash6'].str.slice(0, 5)
  filtered_stays['geohash4'] = filtered_stays['geohash5'].str.slice(0, 4)
  filtered_stays['geohash3'] = filtered_stays['geohash4'].str.slice(0, 3)


  ghns = ['geohash9','geohash8','geohash7','geohash6','geohash5','geohash4','geohash3']
  grouped_sets = filtered_stays.groupby('user').apply(lambda usergroup: {ghn:set(usergroup[ghn].to_list()) for ghn in ghns}).to_dict()


  # Calculate the size of the pairwise overlap
  all_zip_codes = set(user_to_homezip.values())

#   zip_to_zip_overlap = {tuple(sorted((z1,z2))):{ghn:[] for ghn in ghns} # Append to array (this is slow)
  zip_to_zip_overlap = {tuple(sorted((z1,z2))):{ghn:(0,0) for ghn in ghns} # Iteratively calculate mean
      for z1, z2 in list(itertools.combinations(all_zip_codes, 2)) + [(z,z) for z in all_zip_codes]}

  for user1, user2 in tqdm(itertools.combinations(grouped_sets.keys(), 2), total=len(valid_users)*(len(valid_users)-1)//2, miniters=10**5, desc="Calculating pairwise overlap for "+location_code+"..."):
      zip1, zip2 = user_to_homezip.get(user1), user_to_homezip.get(user2)
      if zip1 and zip2:
          key = tuple(sorted((zip2, zip1)))
          # Get all the overlaps for each geohash level
          for ghn in ghns:
              overlap = len(grouped_sets[user1][ghn] & grouped_sets[user2][ghn])
            #   zip_to_zip_overlap[key][ghn].append(overlap)
              n = zip_to_zip_overlap[key][ghn][1]
              zip_to_zip_overlap[key][ghn] =((n*zip_to_zip_overlap[key][ghn][0] + overlap)/(n+1), n+1)



  # Take the mean of the overlaps if there are more than zero overlaps 
  zip_to_zip_overlap_means = {key:{ghn:np.mean(overlaps) for ghn, overlaps in zip_to_zip_overlap[key].items()} for key in tqdm(zip_to_zip_overlap)}

  # Take the median of the overlaps
  zip_to_zip_overlap_medians = {key:{ghn:np.median(overlaps) for ghn, overlaps in zip_to_zip_overlap[key].items()} for key in tqdm(zip_to_zip_overlap)}

  # Take the mean of all the overlaps if there are more than 10
  zip_to_zip_overlap_means_filtered = {key:{ghn:np.mean(overlaps) for ghn, overlaps in zip_to_zip_overlap[key].items() if len(overlaps) > 10} for key in tqdm(zip_to_zip_overlap)}

  # Convert to dataframe
  zip_to_zip_overlap_means_df = pd.DataFrame(
      [[key[0], key[1]]+
      list(ghnoverlaps.values()) + list(zip_to_zip_overlap_medians[key].values()) + list(zip_to_zip_overlap_means_filtered[key].values()) for key, ghnoverlaps in zip_to_zip_overlap_means.items()],
        columns=['zip1', 'zip2']+ghns+['median_'+ghn for ghn in ghns]+['filtered_'+ghn for ghn in ghns])


  zip_to_zip_overlap_means_df.to_csv('results/zip_to_zip_overlap_means_df'+location_code+'.csv', index=False)
  print("Saved zip_to_zip_overlap_means_df"+location_code+".csv")

def __main__():
    locations = {
    "16980": "chicago",
    "35620": "nyc",
    "31080": "la",
    "19100": "dallas",
    "14460": "boston",
    }
    for location_code in locations.keys():
        print("Calculating psi for", locations[location_code])
        calculate_psi_connectedness(location_code)

    
if __name__ == "__main__":
    __main__()