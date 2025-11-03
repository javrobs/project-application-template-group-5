
import json
from typing import List

import config
from model import Issue
from datetime import datetime
from functools import reduce

# Store issues as singleton to avoid reloads
_ISSUES:List[Issue] = None
_MIGRATION_DATE:datetime = None
_LABEL_CATEGORY_LIST:List[str] = None
_YEAR_RANGE:List[int] = None

class DataLoader:
    """
    Loads the issue data into a runtime object.
    """
    
    def __init__(self):
        """
        Constructor
        """
        self.data_path:str = config.get_parameter('ENPM611_PROJECT_DATA_PATH')
        
    def get_issues(self):
        """
        This should be invoked by other parts of the application to get access
        to the issues in the data file.
        """
        global _ISSUES # to access it within the function
        if _ISSUES is None:
            _ISSUES = self._load()
            print(f'Loaded {len(_ISSUES)} issues from {self.data_path}.')
        return _ISSUES
    
    def get_migration_date(self):
        """
        This should be invoked by other parts of the application to get access
        to the latest date contained in the dataset (to obtain issue age, for example).
        Returns an aware datetime object
        """
        global _MIGRATION_DATE # to access it within the function
        if _MIGRATION_DATE is None:
            issues = self.get_issues()
            _MIGRATION_DATE = max([max([event.event_date for event in issue.events if event.event_date]) for issue in issues])
            print(f"Loaded migration date",_MIGRATION_DATE)
        return _MIGRATION_DATE 
    
    def get_label_categories(self):
        """
        This returns the categories of labels contained in the dataset as a list.
        """
        global _LABEL_CATEGORY_LIST # to access it within the function
        if _LABEL_CATEGORY_LIST is None:
            issues = self.get_issues()
            label_categories = []
            for issue in issues:
                label_categories += [label.category for label in issue.labels]
            _LABEL_CATEGORY_LIST = list(set(label_categories))
            print(f"Loaded label categories",', '.join(_LABEL_CATEGORY_LIST))
        return _LABEL_CATEGORY_LIST 
    
    def get_year_range(self):
        """
        This returns the years included in the dataset as a list.
        """
        global _YEAR_RANGE 
        if _YEAR_RANGE is None:
            issues = self.get_issues()
            created = [issue.created_date.year for issue in issues]
            _YEAR_RANGE = [str(each) for each in range(min(created),max(created)+1)]
            print("Loaded years")
        return _YEAR_RANGE 

    
    def _load(self):
        """
        Loads the issues into memory.
        """
        with open(self.data_path,'r') as fin:
            return [Issue(i) for i in json.load(fin)]
    

if __name__ == '__main__':
    # Run the loader for testing
    DataLoader().get_issues()