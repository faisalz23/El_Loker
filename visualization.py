import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
import numpy as np
from wordcloud import WordCloud
import re
import sys

try:
    # Connect to MongoDB with error handling
    print("Attempting to connect to MongoDB...")
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    
    # Test the connection
    client.server_info()
    print("Successfully connected to MongoDB!")
    
    db = client['jobstreet2']
    collection = db['job']
    
    # Check if collection exists and has data
    if collection.count_documents({}) == 0:
        print("Warning: No data found in the collection. Please run the scraper first.")
        sys.exit(1)
    
    # Convert MongoDB data to pandas DataFrame
    print("Fetching data from MongoDB...")
    data = list(collection.find())
    df = pd.DataFrame(data)
    
    if df.empty:
        print("Error: No data found in the DataFrame")
        sys.exit(1)
    
    print(f"Successfully loaded {len(df)} records")
    
    # Set style for visualizations
    plt.style.use('seaborn-v0_8')
    sns.set_theme(style="whitegrid")
    
    def create_job_distribution_by_category():
        plt.figure(figsize=(15, 8))
        category_counts = df['category'].value_counts()
        sns.barplot(x=category_counts.values, y=category_counts.index)
        plt.title('Distribution of Jobs by Category')
        plt.xlabel('Number of Jobs')
        plt.ylabel('Job Category')
        plt.tight_layout()
        plt.savefig('job_distribution_by_category.png')
        plt.close()

    def create_top_companies():
        plt.figure(figsize=(15, 8))
        top_companies = df['company'].value_counts().head(20)
        sns.barplot(x=top_companies.values, y=top_companies.index)
        plt.title('Top 20 Companies with Most Job Postings')
        plt.xlabel('Number of Job Postings')
        plt.ylabel('Company Name')
        plt.tight_layout()
        plt.savefig('top_companies.png')
        plt.close()

    def create_location_distribution():
        plt.figure(figsize=(15, 8))
        location_counts = df['location'].value_counts().head(15)
        sns.barplot(x=location_counts.values, y=location_counts.index)
        plt.title('Top 15 Job Locations')
        plt.xlabel('Number of Jobs')
        plt.ylabel('Location')
        plt.tight_layout()
        plt.savefig('location_distribution.png')
        plt.close()

    def create_job_type_distribution():
        plt.figure(figsize=(15, 8))
        job_type_counts = df['job_type'].value_counts().head(10)
        sns.barplot(x=job_type_counts.values, y=job_type_counts.index)
        plt.title('Top 10 Job Types')
        plt.xlabel('Number of Jobs')
        plt.ylabel('Job Type')
        plt.tight_layout()
        plt.savefig('job_type_distribution.png')
        plt.close()

    def create_salary_wordcloud():
        # Extract salary information
        salary_text = ' '.join(df['salary'].dropna().astype(str))
        
        # Create wordcloud
        wordcloud = WordCloud(width=1200, height=800, background_color='white').generate(salary_text)
        
        plt.figure(figsize=(15, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Salary Information Word Cloud')
        plt.tight_layout()
        plt.savefig('salary_wordcloud.png')
        plt.close()

    def create_category_salary_comparison():
        # Extract numeric values from salary strings
        def extract_salary(salary_str):
            if pd.isna(salary_str) or salary_str == 'Not specified':
                return None
            numbers = re.findall(r'\d+', salary_str)
            if numbers:
                return int(numbers[0])
            return None
        
        df['salary_numeric'] = df['salary'].apply(extract_salary)
        
        # Create boxplot
        plt.figure(figsize=(15, 8))
        sns.boxplot(x='category', y='salary_numeric', data=df)
        plt.title('Salary Distribution by Job Category')
        plt.xlabel('Job Category')
        plt.ylabel('Salary (in millions)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('category_salary_comparison.png')
        plt.close()

    def create_job_postings_timeline():
        # Extract date information
        df['posted_date'] = pd.to_datetime(df['posted_date'], errors='coerce')
        
        # Group by date and count
        daily_counts = df.groupby(df['posted_date'].dt.date).size()
        
        plt.figure(figsize=(15, 8))
        daily_counts.plot(kind='line')
        plt.title('Job Postings Timeline')
        plt.xlabel('Date')
        plt.ylabel('Number of Job Postings')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('job_postings_timeline.png')
        plt.close()

    def create_category_location_heatmap():
        # Create a pivot table of category vs location
        pivot_table = pd.pivot_table(
            df,
            values='title',
            index='category',
            columns='location',
            aggfunc='count',
            fill_value=0
        )
        
        plt.figure(figsize=(15, 10))
        sns.heatmap(pivot_table, cmap='YlOrRd', annot=True, fmt='d')
        plt.title('Job Distribution: Category vs Location')
        plt.xlabel('Location')
        plt.ylabel('Category')
        plt.tight_layout()
        plt.savefig('category_location_heatmap.png')
        plt.close()

    # Create all visualizations
    print("Creating visualizations...")
    create_job_distribution_by_category()
    create_top_companies()
    create_location_distribution()
    create_job_type_distribution()
    create_salary_wordcloud()
    create_category_salary_comparison()
    create_job_postings_timeline()
    create_category_location_heatmap()
    print("Visualizations created successfully!")

except Exception as e:
    print(f"Error: {str(e)}")
    print("\nTroubleshooting steps:")
    print("1. Make sure MongoDB service is running")
    print("2. Check if you have data in the 'jobstreet2' database")
    print("3. Verify your MongoDB connection string")
    print("4. Check if all required Python packages are installed")
    sys.exit(1)

finally:
    if 'client' in locals():
        client.close()
        print("MongoDB connection closed") 