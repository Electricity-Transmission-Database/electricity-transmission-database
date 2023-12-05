# Global Tranmission Database
Scripts to process and visualize data for the global electricity transmission database 

## Description
...

## Getting started
coming soon...

## What's here

### Scripts

#### `usa/ba-mapping.ipynb`
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

#### `usa/ba-transmission.ipynb`

Estimates transmission capacity between each BA based on historical maximum flow rates.

**Inputs** 
- `usa/ba-mapper.csv` - A user created mapper on how to name each BA in the USA
- `usa/flows/xxx.csv` - Automatically downloaded datafiles (represented by `xxx`) giving historical transmission between BAs. The files contain hourly flow values in 6 month intervals. See the notebook for the datasource. 

**Outputs**
- `usa/usa-transmission-capacity.csv` - A file with the folloing columns: 
    - **TECHNOLOGY**: Unique name of transmission technology 
    - **From**: BA of flow from 
    - **To**: BA of flow to 
    - **Cap (MW) +**: Capacity in direction of From->To (Positive Number)
    - **Cap (MW) -**: Capacity in direction of From->To (Negative Number)


## TODO
- [ ] Add environment file
- [ ] Make figures in notebooks
    - [ ] Included/excluded regions
- [ ] Include Zenodo link here