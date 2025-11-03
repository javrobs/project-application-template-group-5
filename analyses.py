
from typing import List
import matplotlib.pyplot as plt
import pandas as pd

from data_loader import DataLoader
from model import Issue
import config

class ExampleAnalysis:
    """
    Implements an example analysis of GitHub
    issues and outputs the result of that analysis.
    """
    
    def __init__(self):
        """
        Constructor
        """
        # Parameter is passed in via command line (--user)
        self.USER:str = config.get_parameter('user')
    
    def run(self):
        """
        Starting point for this analysis.
        
        Note: this is just an example analysis. You should replace the code here
        with your own implementation and then implement two more such analyses.
        """
        issues:List[Issue] = DataLoader().get_issues()
        
        ### BASIC STATISTICS
        # Calculate the total number of events for a specific user (if specified in command line args)
        total_events:int = 0
        for issue in issues:
            total_events += len([e for e in issue.events if self.USER is None or e.author == self.USER])
        
        output:str = f'Found {total_events} events across {len(issues)} issues'
        if self.USER is not None:
            output += f' for {self.USER}.'
        else:
            output += '.'
        print('\n\n'+output+'\n\n')
        

        ### BAR CHART
        # Display a graph of the top 50 creators of issues
        top_n:int = 50
        # Create a dataframe (with only the creator's name) to make statistics a lot easier
        df = pd.DataFrame.from_records([{'creator':issue.creator} for issue in issues])
        # Determine the number of issues for each creator and generate a bar chart of the top N
        df_hist = df.groupby(df["creator"]).value_counts().nlargest(top_n).plot(kind="bar", figsize=(14,8), title=f"Top {top_n} issue creators")
        # Set axes labels
        df_hist.set_xlabel("Creator Names")
        df_hist.set_ylabel("# of issues created")
        # Plot the chart
        plt.show()

class Analysis1:
    def __init__(self):
        self.loader = DataLoader()
        self.set_category(config.get_parameter('category'))

    def set_category(self, value):
        valid_categories = self.loader.get_label_categories()
        while value == "" or value not in valid_categories:
            value = input(f"Choose a valid category from the following list [{(', ').join(valid_categories)}]: ")
        self.CATEGORY:str = value

    def run(self):
        issues:List[Issue] = self.loader.get_issues()
        max_date = self.loader.get_migration_date()
        category = self.CATEGORY
        issue_ages = pd.DataFrame([{"age":(max_date - issue.created_date).days,"duration":(issue.updated_date - issue.created_date).days,"state":issue.state}|{category:[getattr(label,"sublabel",None) for label in issue.labels if label.category]} for issue in issues])
        
        plots = {}
        for state,value in zip(["open","closed"],["age","duration"]):
            df = issue_ages[issue_ages["state"]==state]
            df_e = df.explode(category).dropna(subset=[category])
            count = df_e["state"].count()
            if count:
                vc=df_e[category].value_counts()
                keep = vc[vc>count*.05].index
                df_e[category] = df_e[category].map(lambda x:"other" if x not in keep else x)
                df_e = df_e.reset_index().drop_duplicates(subset=['index',value,category])
                df_e_pivot = df_e.pivot(index="index",columns=category,values=value)
                plots[state] = df_e_pivot.plot(kind="hist",stacked=True,xlabel="Days open" if state=="open" else "Duration (days)",ylabel='Number of issues',title=f"{'Open Issue Age' if state=='open' else 'Closed Issue Duration'} by {category}")
                print(f"{'='*40}\n{'='*40}\n{state} issues".upper())
                print(f"Mean {value} (days):   {df[value].mean():.2f}")
                print(f"Median {value} (days): {df[value].median():.2f}")
                
                print(f"\nIssues {state} labeled with '{category}' category: {count}")
                for key, count in df_e[category].value_counts().items():
                    select_df = df_e[df_e[category]==key]
                    print(f"[{category}/{key}] - Count: {count}, Mean {value}: {select_df[value].mean():.2f}, Median {value}: {select_df[value].median():.2f}")

        plt.show()

class Analysis2:
    def __init__(self):
        pass
    def run(self):
        pass

class Analysis3:
    def __init__(self):
        pass
    def run(self):
        pass