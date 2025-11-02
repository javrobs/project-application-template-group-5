from collections import defaultdict, Counter
from typing import List
import matplotlib.pyplot as plt
import numpy as np
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

class Analysis1():
    def __init__(self):
        pass
    def run(self):
        pass

class Analysis2():
    def __init__(self):
        # Get all the issues in the issues list
        self.ISSUE_YEAR = config.get_parameter('issue_year')

    def run(self):
        issues: List[Issue] = DataLoader().get_issues()

        if self.ISSUE_YEAR is None:
            print(f"⚠️ No issue year provided exiting application.")
            return

        all_issues = False
        year = None
        if self.ISSUE_YEAR == 'all':
            all_issues = True
        else:
            year = int (self.ISSUE_YEAR)

        if year is None:
            print(f"⚠️ Issue year provided is not a number, exiting application.")
            return

        if all_issues:
            filtered_issues = issues
        else:
            filtered_issues = [
                issue for issue in issues
                if issue.created_date and issue.created_date.year == year and issue.labels
            ]

        # ---------------------------
        # Aggregate monthly counts
        # ---------------------------
        monthly_counts = defaultdict(lambda: Counter())

        for issue in filtered_issues:
            month = issue.created_date.strftime("%Y-%m")
            for label in issue.labels:
                monthly_counts[month][label] += 1

        # ---------------------------
        # Aggregate top labels
        # ---------------------------
        total_label_counts = Counter()
        for _, label_counts in monthly_counts.items():
            total_label_counts.update(label_counts)

        top_labels = [l for l, _ in total_label_counts.most_common(6)]

        months = sorted(monthly_counts.keys())
        data = {label: [monthly_counts[m][label] for m in months] for label in top_labels}

        # ---------------------------
        # Plot stacked bar chart
        # ---------------------------
        fig, ax = plt.subplots(figsize=(10, 5))
        bottom = [0] * len(months)
        colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B3', '#CCB974', '#64B5CD']

        for label, color in zip(top_labels, colors):
            ax.bar(months, data[label], bottom=bottom, label=label, color=color, alpha=0.85)
            bottom = [bottom[i] + data[label][i] for i in range(len(months))]

        ax.set_title(f"Monthly Issue Creation Trend by Label ({self.ISSUE_YEAR})")
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Issues Created")
        ax.legend(title="Labels")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

class Analysis3():
    def __init__(self):
        pass
    def run(self):
        pass