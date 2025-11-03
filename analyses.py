from collections import defaultdict, Counter
from typing import List
import matplotlib.pyplot as plt
import pandas as pd

from data_loader import DataLoader
from model import Issue
import config


COLORS = ["#2E65AD", '#55A868', '#C44E52', "#7A5DD8", "#BB9F3B", '#64B5CD', "#DD8A32", "#DC4CC4", "#B6EB54", "#3ACE9F"]

class Analysis1:
    def __init__(self):
        self.loader = DataLoader()
        self.set_category(config.get_parameter('category'))
        self.OTHER_CUTOUT = config.get_parameter('other_cutout',5) / 100
        

    def set_category(self, value):
        valid_categories:List[str] = self.loader.get_label_categories()
        while value == "" or value not in valid_categories:
            value = input(f"Choose a valid category from the following list [{(', ').join(valid_categories)}]: ")
        self.CATEGORY:str = value
  

    def run(self):
        issues:List[Issue] = self.loader.get_issues()
        max_date = self.loader.get_migration_date()
        category = self.CATEGORY
        
        
        plots = {}
        for state,value in zip(["open","closed"],["age","duration"]):
            if state == "open":
                df = pd.DataFrame([{value:(max_date - issue.created_date).days}|
                                {category:[getattr(label,"sublabel",None) for label in issue.labels if label.category==category]}
                                 for issue in issues if issue.state==state])
            else:
                df = pd.DataFrame([{value:(issue.closed_date - issue.created_date).days}|
                                {category:[getattr(label,"sublabel",None) for label in issue.labels if label.category==category]}
                                 for issue in issues if issue.state==state and issue.closed_date])
            df_e = df.explode(category).dropna(subset=[category])
            count = df_e[value].count()
            if count:
                vc=df_e[category].value_counts()
                keep = vc[vc > count * self.OTHER_CUTOUT].index
                df_e[category] = df_e[category].map(lambda x:"other" if x not in keep else x)
                df_e = df_e.reset_index().drop_duplicates(subset=['index',value,category])
                df_e_pivot = df_e.pivot(index="index",columns=category,values=value)
                plots[state] = df_e_pivot.plot(kind="hist",stacked=True, color=COLORS, xlabel="Days open" if state=="open" else "Duration (days)",ylabel='Number of issues',title=f"{'Open Issue Age' if state=='open' else 'Closed Issue Duration'} by {category}")
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
        self.loader = DataLoader()
        self.set_category(config.get_parameter('category'))
        self.set_year(config.get_parameter('year'))

    def set_category(self, value):
        valid_categories:List[str] = self.loader.get_label_categories()
        while value == "" or value not in valid_categories:
            value = input(f"Choose a valid category from the following list [{(', ').join(valid_categories)}]: ")
        self.CATEGORY:str = value
  

    def set_year(self, value):
        valid_years:List[str] = self.loader.get_year_range() + ["all"]
        value = str(value)
        while value == "" or value not in valid_years:
            value = input(f"Choose a valid year from the following list {valid_years}: ")
        self.ISSUE_YEAR:str = value

    def run(self):
        issues: List[Issue] = self.loader.get_issues()

        all_issues = False
        year = None
        category = self.CATEGORY
        if self.ISSUE_YEAR == 'all':
            all_issues = True
        else:
            year = int (self.ISSUE_YEAR)

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
            for label in [label.sublabel for label in issue.labels if label.category == category]:
                monthly_counts[month][label] += 1

        # ---------------------------
        # Aggregate top labels
        # ---------------------------
        total_label_counts = Counter()
        for _, label_counts in monthly_counts.items():
            total_label_counts.update(label_counts)

        top_labels = [l for l, _ in total_label_counts.most_common(10)]

        months = sorted(monthly_counts.keys())
        data = {label: [monthly_counts[m][label] for m in months] for label in top_labels}

        # ---------------------------
        # Plot stacked bar chart
        # ---------------------------
        fig, ax = plt.subplots(figsize=(10, 5))
        bottom = [0] * len(months)

        for label, color in zip(top_labels, COLORS):
            ax.bar(months, data[label], bottom=bottom, label=label, color=color, alpha=0.85)
            bottom = [bottom[i] + data[label][i] for i in range(len(months))]

        ax.set_title(f"Monthly Issue Creation Trend by {category} ({self.ISSUE_YEAR})")
        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Issues Created")
        ax.legend(title=category)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

class Analysis3:
    def __init__(self):
        self.loader = DataLoader()
        self.set_category(config.get_parameter('category'))
        self.OTHER_CUTOUT = config.get_parameter('other_cutout',2) / 100

    def set_category(self, value):
        valid_categories:List[str] = self.loader.get_label_categories()
        while value == "" or value not in valid_categories:
            value = input(f"Choose a valid category from the following list [{(', ').join(valid_categories)}]: ")
        self.CATEGORY:str = value
        
    def run(self):
        issues:List[Issue] = self.loader.get_issues()
        max_date = self.loader.get_migration_date()
        category = self.CATEGORY
        df = pd.DataFrame([{"created_date":issue.created_date,"closed_date":(issue.closed_date if issue.state=="closed" else max_date)}|{category:[getattr(label,"sublabel",None) for label in issue.labels if label.category==category]} for issue in issues])
        df_e = df.explode(category).dropna(subset=[category])

        date_range = pd.date_range(df['created_date'].min(), df['closed_date'].max(), freq='D')
        # For each date, count how many issues are open
        count = df_e["created_date"].count()
        vc = df_e[category].value_counts()
        keep = vc[vc > count * self.OTHER_CUTOUT].index
        df_e[category] = df_e[category].map(lambda x:"other" if x not in keep else x)
        counts={}
        for label in df_e[category].value_counts().index:
            counts[label]=[((df_e['created_date'] <= dt) & (df_e[category]==label) & (df_e['closed_date'] >= dt)).sum() for dt in date_range]

        # # Put into DataFrame
        workload = pd.DataFrame({'date': date_range}|counts)
        workload['date'] = workload['date']

        # # Plot
        workload.plot.area(x="date", color=COLORS, ylabel=f'Open Issues by {category}', title='Historical Open Issues')

        plt.show()