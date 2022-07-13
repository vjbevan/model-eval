# Model Evaluation Toolbox

Developing model evaluation notebooks allowing users to compare model estimates to SnowEx data and other datasets.

### Collaborators on this project

| Name  | Personal Goals / Can help with | Role
| ------------- | ------------- | ------------- |
| [Valerie Bevan](https://github.com/vjbevan) | | |
| [Cassia Cai](https://github.com/CassiaCai) | | |
| [Evi Ofekeze](https://github.com/eviofekeze) | | |
| [Steven Pestana](https://github.com/spestana) | | Project Facilitator/Helper |
| [Justin Pflug](https://github.com/jupflug) | | |
| [Engela Sthapit](https://github.com/esthapit) | | |
| [Sveta Stuefer](https://github.com/sveta-ak) | | |
| [Melissa Wrzesien](https://github.com/mlwrzesien) | | Project Lead |

### The problem

Model evaluation can be a time consuming step consisting of downloading multiple validation datasets and post-processing the datasets to make sure they match your model resolution, spatial extent, and time period. This notebook allows users to compare the provided model output (from SnowModel)

### Application Example

List one specific application of this work.

### Sample data

Model data is from a NASA Land Information System simulation using Glen Liston's SnowModel. Model output is available for 4 water years from the NASA AWS bucket. Evaluation data is from the snowexSQL database.

### Specific Questions

Tasks to accomplish:
* Grid-to-point comparison: compare the model output (in a gridded raster) to a point dataset like snow pit snow depths
* Grid-to-grid comparison: compare model output to another gridded product, like ASO lidar
* Determine which evaluation metric is most appropriate for each comparison

Such a notebook will allow for asking/answering questions such as:
* Does the model over/underestimate compared to field observations?
* Does the model uncertainty correlate with land cover features (elevation, vegetation type)?


### Existing methods

Existing modeling evaluation methods traditionally require a user to download data from NSIDC or another DAAC. For the SnowEx snow pits, as an example, and user would have to search for them on NSIDC, download the data, and select the model grid cells that contain each snow pit. Once all the preprocessing steps are complete, only then could the user start to evaluate their model. This notebook provides the tools to make this an easier process.

### Proposed methods/tools

* 

### Future development

Future work could make this notebook more generalizable so that users can upload their own model output for evaluation. Future developments could also include more datasets for comparison, whether those in the SnowEx database or other products (snow reanalysis, meteorological data, SNOTEL, etc).

### Background reading

* [LIS Website](https://lis.gsfc.nasa.gov/)
* [LIS on GitHub](https://github.com/NASA-LIS/LISF)
* [SnowEx Database GitHub](https://github.com/SnowEx/snowexsql/)
* [SnowEx data on NSIDC](https://nsidc.org/data/snowex)
