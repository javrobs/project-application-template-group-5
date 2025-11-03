# ENPM611 Project Application - Group 5

This is our extension of the template for the ENPM611 class project. It implements an application that analyzes GitHub issues for the [poetry](https://github.com/python-poetry/poetry/issues) Open Source project and generates three different analyses.

This application template implements some of the basic functions:

- `data_loader.py`: Utility to load the issues from the provided data file and returns the issues in a runtime data structure (e.g., objects).
    - It has been extended to extract data from the issues of the __migration date__, __label categories__ and __year range__.
- `model.py`: Implements the data model into which the data file is loaded. The data can then be accessed by accessing the fields of objects.
    - Models have been extended by defining the __Label__ model, which separates labels in categories and sublabels. The __Issue__ model was extended by the addition of the _closed_date_ parameter. 
- `config.py`: Supports configuring the application via the `config.json` file. You can add other configuration paramters to the `config.json` file.
- `run.py`: This is the module that will be invoked to run the application. Based on the `--feature` command line parameter, one of the three analyses will be run. 
    - This module has been extended to run three different analyses, as well as to take additional arguments from the terminal 

## Setup

To get started, clone this repository and install the dependencies.
- No dependencies were added from the template.

### Install dependencies

In the root directory of the application, create a virtual environment, activate that environment, and install the dependencies like so:

```
pip install -r requirements.txt
```

### Download and configure the data file

Download the "poetry_issues_all.json" file from the project assignment in Canvas and place it in the main directory folder. Our .gitignore file will keep it out of version control. Alternatively, you can also specify an environment variable by the same name as the config setting (`ENPM611_PROJECT_DATA_PATH`) to read the json file from a different path.

### Run an analysis

With everything set up, working from the python environment, you should be able to run any of the features by typing the following command, where N is equal to 1, 2 or 3:
```
python run.py --feature N OR python run.py -f N
```


That will output basic information about the issues to the command line.

## Analysis

### Open age and Closed duration

#### Parameters:
- Category: A required parameter that specifies the category of label to be analyzed. If this parameter isn't provided, the user will be asked to input it for the analysis to run. Input it in the command as `--category X` or `-c X`, where X can be any of the label categories, for example __area__ or __kind__. 
- Other cutout: A percentage threshold of the total count of a label category necessary for the figure to show a specific label. Labels below the threshold will be grouped in the results as "Other" (default: 5%). Input it in the command as `--other-cutout N` or `-o N`
#### Output:
- Figures
    - Figure 1 shows a histogram for open issue age (How long has an issue been open), with stacked bars for the labels in issues.
    - Figure 2 shows a histogram for closed issue age (How long an issue took to close), with stacked bars for the labels in issues.
- Console
    - Statistic information for open and closed issues (mean and median age or duration).
    - Specific label statistical information for each sublabel in open and closed issues (mean and median age or duration).


### Month by month opened issues

#### Parameters:
- Year: The year to analyze. If this parameter isn't provided, the user will be asked to input it for the analysis to run. Input it in the command as `--year N` or `-y N`. 
- Category: A required parameter that specifies the category of label to be analyzed. If this parameter isn't provided the user will be asked to input it for the analysis to run. Input it in the command as `--category X` or `-c X`, where X can be any of the label categories, for example __area__ or __kind__. 
#### Output:
- Figure: How many issues were open that year, month by month, stacked by top 10 most labels in the category.


### Month by month opened issues

#### Parameters:
- Category: A required parameter that specifies the category of label to be analyzed. If this parameter isn't provided the user will be asked to input it for the analysis to run. Input it in the command as `--category X` or `-c X`, where X can be any of the label categories, for example __area__ or __kind__. 
- Other cutout: A percentage threshold of the total count of a label category necessary for the figure to show a specific label. Labels below the threshold will be grouped in the results as "Other" (default: 2%). Input it in the command as `--other-cutout N`
#### Output:
- Figure: How many issues of a specific label where open at a certain date, shown as area under the curve. 