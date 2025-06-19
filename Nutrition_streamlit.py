import pandas as pd
import numpy as np
import streamlit as st
import pymysql

st.title("Nutrition Project")

myconnection = pymysql.connect(host='127.0.0.1', user = 'root', password = 'rootroot', database = 'nutrition_db')

obesity_count_df = pd.read_sql_query("SELECT COUNT(*) AS total_rows FROM obesity", myconnection)
st.write(f"Total Records in Obesity Table: {obesity_count_df['total_rows'].iloc[0]}")

malnutrition_count_df = pd.read_sql_query("SELECT COUNT(*) AS total_rows FROM malnutrition", myconnection)
st.write(f"Total Records in Malnutrition Table: {malnutrition_count_df['total_rows'].iloc[0]}")

sql_queries = {
    "1. Top 5 regions with the highest average obesity levels in 2022": """
        SELECT Region, AVG(Mean_Estimate) AS Average_Obesity_Level
        FROM obesity
        WHERE Year = 2022
        GROUP BY Region
        ORDER BY Average_Obesity_Level DESC
        LIMIT 5;
    """,
    "2. Top 5 countries with highest average obesity estimates": """
        SELECT Country, AVG(Mean_Estimate) AS Average_Obesity_Estimate
        FROM obesity
        GROUP BY Country
        ORDER BY Average_Obesity_Estimate DESC
        LIMIT 5;
    """,
    "3. Obesity trend in India over the years (Mean_Estimate)": """
        SELECT Year, Mean_Estimate
        FROM obesity
        WHERE Country = 'India'
        ORDER BY Year ASC;
    """,
    "4. Average obesity by gender": """
        SELECT Gender, AVG(Mean_Estimate) AS Average_Obesity_Estimate
        FROM obesity
        GROUP BY Gender
        ORDER BY Average_Obesity_Estimate DESC;
    """,
    "5. Country count by obesity level category and age group": """
        SELECT obesity_level, age_group, COUNT(DISTINCT Country) AS Country_Count
        FROM obesity
        GROUP BY obesity_level, age_group
        ORDER BY obesity_level, age_group;
    """,
    "6a. Top 5 countries least reliable (highest average CI_Width)": """
        SELECT Country, AVG(CI_Width) AS Average_CI_Width
        FROM obesity
        GROUP BY Country
        ORDER BY Average_CI_Width DESC
        LIMIT 5;
    """,
    "6b. Top 5 countries most consistent (smallest average CI_Width)": """
        SELECT Country, AVG(CI_Width) AS Average_CI_Width
        FROM obesity
        GROUP BY Country
        ORDER BY Average_CI_Width ASC
        LIMIT 5;
    """,
    "7. Average obesity by age group": """
        SELECT age_group, AVG(Mean_Estimate) AS Average_Obesity_Estimate
        FROM obesity
        GROUP BY age_group
        ORDER BY Average_Obesity_Estimate DESC;
    """,
    "8. Top 10 Countries with consistent low obesity (low average + low CI)": """
        SELECT Country, AVG(Mean_Estimate) AS Average_Obesity_Estimate, AVG(CI_Width) AS Average_CI_Width
        FROM obesity
        GROUP BY Country
        ORDER BY Average_Obesity_Estimate ASC, Average_CI_Width ASC
        LIMIT 10;
    """,
    "9. Countries where female obesity exceeds male by large margin (same year)": """
        SELECT
            o_female.Country,
            o_female.Year,
            o_female.Mean_Estimate AS Female_Mean_Estimate,
            o_male.Mean_Estimate AS Male_Mean_Estimate,
            (o_female.Mean_Estimate - o_male.Mean_Estimate) AS Female_Male_Difference
        FROM
            obesity AS o_female
        JOIN
            obesity AS o_male ON o_female.Country = o_male.Country
            AND o_female.Year = o_male.Year
        WHERE
            o_female.Gender = 'Female' AND o_male.Gender = 'Male'
            AND (o_female.Mean_Estimate - o_male.Mean_Estimate) > 5.0
        ORDER BY Female_Male_Difference DESC;
    """,
    "10. Global average obesity percentage per year": """
        SELECT Year, AVG(Mean_Estimate) AS Global_Average_Obesity_Percentage
        FROM obesity
        GROUP BY Year
        ORDER BY Year ASC;
    """,
    "11. Average malnutrition by age group": """
        SELECT age_group, AVG(Mean_Estimate) AS Average_Malnutrition_Estimate
        FROM malnutrition
        GROUP BY age_group
        ORDER BY Average_Malnutrition_Estimate DESC;
    """,
    "12. Top 5 countries with highest average malnutrition estimates": """
        SELECT Country, AVG(Mean_Estimate) AS Average_Malnutrition_Estimate
        FROM malnutrition
        GROUP BY Country
        ORDER BY Average_Malnutrition_Estimate DESC
        LIMIT 5;
    """,
    "13. Malnutrition trend in African region over the years": """
        SELECT Year, AVG(Mean_Estimate) AS Average_Malnutrition_Estimate
        FROM malnutrition
        WHERE Region = 'Africa'
        GROUP BY Year
        ORDER BY Year ASC;
    """,
    "14. Gender-based average malnutrition": """
        SELECT Gender, AVG(Mean_Estimate) AS Average_Malnutrition_Estimate
        FROM malnutrition
        GROUP BY Gender
        ORDER BY Average_Malnutrition_Estimate DESC;
    """,
    "15. Malnutrition level-wise (average CI_Width by age group)": """
        SELECT malnutrition_level, age_group, AVG(CI_Width) AS Average_CI_Width
        FROM malnutrition
        GROUP BY malnutrition_level, age_group
        ORDER BY malnutrition_level, age_group;
    """,
    "16. Yearly malnutrition change in specific countries (India, Nigeria, Brazil)": """
        SELECT
            Country,
            Year,
            Mean_Estimate,
            LAG(Mean_Estimate, 1, Mean_Estimate) OVER (PARTITION BY Country ORDER BY Year) AS Previous_Year_Mean_Estimate,
            (Mean_Estimate - LAG(Mean_Estimate, 1, Mean_Estimate) OVER (PARTITION BY Country ORDER BY Year)) AS Yearly_Change
        FROM
            malnutrition
        WHERE
            Country IN ('India', 'Nigeria', 'Brazil')
        ORDER BY
            Country, Year;
    """,
    "17. Regions with lowest malnutrition averages": """
        SELECT Region, AVG(Mean_Estimate) AS Average_Malnutrition_Estimate
        FROM malnutrition
        GROUP BY Region
        ORDER BY Average_Malnutrition_Estimate ASC
        LIMIT 5;
    """,
    "18. Countries with increasing malnutrition (earliest to latest comparison)": """
        SELECT
            malnutrition.Country,
            (SELECT Mean_Estimate FROM malnutrition WHERE Country = malnutrition.Country ORDER BY Year ASC LIMIT 1) AS Malnutrition_First_Year,
            (SELECT Mean_Estimate FROM malnutrition WHERE Country = malnutrition.Country ORDER BY Year DESC LIMIT 1) AS Malnutrition_Last_Year
        FROM
            malnutrition
        GROUP BY
            malnutrition.Country
        HAVING
            Malnutrition_Last_Year > Malnutrition_First_Year;
    """,
    "19. Min/Max malnutrition levels year-wise comparison": """
        SELECT
            Year,
            MIN(Mean_Estimate) AS Min_Mean_Estimate,
            MAX(Mean_Estimate) AS Max_Mean_Estimate,
            AVG(Mean_Estimate) AS Avg_Mean_Estimate
        FROM malnutrition
        GROUP BY Year
        ORDER BY Year ASC;
    """,
    "20. High CI_Width flags for monitoring (CI_width > 5)": """
        SELECT
            Country,
            Year,
            Mean_Estimate,
            CI_Width,
            CASE
                WHEN CI_Width > 5 THEN 'Flagged for Monitoring'
                ELSE 'Within Acceptable Range'
            END AS CI_Flag
        FROM malnutrition
        WHERE CI_Width > 5
        ORDER BY CI_Width DESC;
    """,
    "21. Obesity vs malnutrition comparison by country (India, USA, Brazil, Nigeria, Germany)": """
        SELECT
            obesity.Country,
            obesity.Year,
            obesity.Mean_Estimate AS Obesity_Mean_Estimate,
            malnutrition.Mean_Estimate AS Malnutrition_Mean_Estimate
        FROM
            obesity
        JOIN
            malnutrition ON obesity.Country = malnutrition.Country AND obesity.Year = malnutrition.Year
        WHERE
            obesity.Country IN ('India', 'United States of America', 'Brazil', 'Nigeria', 'Germany')
        ORDER BY
            obesity.Country, obesity.Year;
    """,
    "22. Gender-based disparity in both obesity and malnutrition (separated results)": None, # Placeholder for sub-queries
    "22a. Average Obesity by Gender (Combined)": """
        SELECT
            Gender,
            AVG(Mean_Estimate) AS Average_Obesity_Estimate
        FROM
            obesity
        GROUP BY
            Gender
        ORDER BY
            Gender;
    """,
    "22b. Average Malnutrition by Gender (Combined)": """
        SELECT
            Gender,
            AVG(Mean_Estimate) AS Average_Malnutrition_Estimate
        FROM
            malnutrition
        GROUP BY
            Gender
        ORDER BY
            Gender;
    """,
    "23. Region-wise average estimates side-by-side (Africa and Americas)": """
        SELECT
            obesity.Region,
            AVG(obesity.Mean_Estimate) AS Average_Obesity_Estimate,
            AVG(malnutrition.Mean_Estimate) AS Average_Malnutrition_Estimate
        FROM
            obesity
        JOIN
            malnutrition ON obesity.Region = malnutrition.Region AND obesity.Year = malnutrition.Year
        WHERE
            obesity.Region IN ('Africa', 'Americas')
        GROUP BY
            obesity.Region
        ORDER BY
            obesity.Region;
    """,
    "24. Countries where obesity is 'High' AND malnutrition is 'Low' (categorical levels)": """
        SELECT
            obesity.Country,
            obesity.Year,
            obesity.obesity_level,
            malnutrition.malnutrition_level,
            obesity.Mean_Estimate AS Obesity_Mean_Estimate,
            malnutrition.Mean_Estimate AS Malnutrition_Mean_Estimate
        FROM
            obesity
        JOIN
            malnutrition ON obesity.Country = malnutrition.Country AND obesity.Year = malnutrition.Year
        WHERE
            obesity.obesity_level = 'High' AND malnutrition.malnutrition_level = 'Low'
        ORDER BY
            obesity.Country, obesity.Year;
    """,
    "25a. Average Obesity by Age Group and Year (Combined)": """
        SELECT
            Year,
            age_group,
            AVG(Mean_Estimate) AS Average_Obesity_Estimate
        FROM
            obesity
        GROUP BY
            Year, age_group
        ORDER BY
            Year ASC, age_group;
    """,
    "25b. Average Malnutrition by Age Group and Year (Combined)": """
        SELECT
            Year,
            age_group,
            AVG(Mean_Estimate) AS Average_Malnutrition_Estimate
        FROM
            malnutrition
        GROUP BY
            Year, age_group
        ORDER BY
            Year ASC, age_group;
    """
}

option = st.selectbox(
    'Select a Query to Run',
    tuple(sql_queries.keys()),
    index=None,
    placeholder="Choose a Query from the list"
)

st.write('You selected:', option)

if option:
    st.subheader(f"Results for: {option}")

    query_to_execute = sql_queries.get(option)

    df = pd.read_sql_query(query_to_execute, myconnection)

    st.dataframe(df, use_container_width=True)