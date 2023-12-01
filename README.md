# Electricity Transmission Database 
Scripts to process and visualize data for the global electricity transmission database 

TODO: Include Zenodo link here 

## Scripts

Below is a summary of each script in this repository 

### `usa/ba-mapping.ipynb`

Creates centerpoints for each USA balancing authority (BA) based on the largest 
city in each BA. If no large city is found in the BA, then the geometric centerpoint 
is used. 

**Inputs** 
- `usa/ba-mapper.csv` - A user created mapper on how to name each BA in the USA
- `usa/world.geojson` - An automatically downloaded file specifying the BA geographic boundaries. See notebook for the source. 
- `usa/worldcities/worldcities.csv` - An automatically downloaded file giving geographic locations and populations of large cities around the world. See notebook for the source. 

**Outputs**
- `usa/usa-centerpoints.csv` - A file with the folloing columns: 
    - **code**: Unique 5 Letter code used to identify the region  
    - **country**: `United States` for all. Used when joining into master dataset 
    - **city**: City representing center point of BA. Empty if no city identified
    - **population**: Population of city representing center point of BA. Empty if no city identified
    - **x**: Longitude of the centerpoint 
    - **y**: Latitude of the centerpoint
