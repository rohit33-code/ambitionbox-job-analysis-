from flask import Flask, render_template, request , Response
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings(action="ignore")
import matplotlib.pyplot as plt
import os
import plotly.express as px
app = Flask(__name__)
data = pd.read_csv("ambitionbox_companies.csv")

@app.route("/")
def home():
    
    data.columns = data.columns.str.strip()


    locations = sorted(data["location"].str.split("+").str[0].str.strip().unique())
    # companies = sorted(data["Company"].unique())
    ratings = sorted(data["rating"].unique())
    about = sorted(data["about"].unique())
    salaries = sorted(data["salaries"].unique())

    return render_template("index.html",locations=locations,ratings=ratings , about = about , salaries = salaries)


def apply_filters(data, location, rating, about, salary):
    
    filtered_df = data.copy()
    if location:
        location = location.split("+")[0].strip()
        filtered_df = filtered_df[
            filtered_df["location"].str.contains(location, case=False, na=False)
        ]
        
    # if company:
    #     filtered_df = filtered_df[
    #         filtered_df["Company"].str.contains(company, case=False, na=False)
    #         ]
    
    if about:
        about_word = about.split("&")[0].strip()
        filtered_df = filtered_df[
            filtered_df["about"].str.contains(about_word, case=False, na=False)
            ]
        
    if rating:
        filtered_df = filtered_df[
            filtered_df["rating"] >= float(rating)
            ]
    
    if salary:
        try:
            salary_val = float(salary.replace("k",""))
            filtered_df["salary_num"] = filtered_df["salaries"].str.replace("k","").astype(float)
            filtered_df = filtered_df[
                filtered_df["salary_num"] >= salary_val
                ]
        except:
            pass
        
    return filtered_df

def get_user_inputs():

    location = request.args.get("location")
    rating = request.args.get("rating")
    about = request.args.get("about")
    salary = request.args.get("salaries")
    output = request.args.get("output")

    return location, rating, about, salary, output

@app.route("/results")
def results():

   
    location, rating, about, salary, output = get_user_inputs()
    filtered_df = apply_filters(data, location, rating, about, salary)
        
    print("Location:", location)
    print("Salary:", salary)
    print("Rating:", rating)
    print("About:", about)
    print("Filtered Rows:", filtered_df.shape)
    print(filtered_df.head())
    # table_data = filtered_df.to_dict(orient="records")
      
    if output == "table":
        table_data = filtered_df.to_dict(orient="records")
        print(table_data)
        return render_template("results.html" ,tables=table_data)
    
    return render_template("index.html")


@app.route("/visuals")
def visuals():

    location, rating, about, salary, output  = get_user_inputs()

    filtered_df = apply_filters(data, location, rating, about, salary)

    if "salary_num" not in filtered_df.columns:
        filtered_df["salary_num"] = filtered_df["salaries"].str.replace("k","").astype(float)

    fig1 = px.histogram(filtered_df, x="rating", title="Rating Distribution")

    fig2 = px.histogram(filtered_df, x="salary_num", title="Salary Distribution")

    top_reviews = filtered_df.sort_values(by="reviews", ascending=False).head(10)
    fig3 = px.bar(top_reviews, x="Company", y="reviews", title="Top Companies by Reviews")

    fig4 = px.scatter(filtered_df, x="rating", y="jobs", title="Jobs vs Rating")

    industry = filtered_df["about"].value_counts().reset_index()
    industry.columns = ["Industry", "Count"]
    fig5 = px.bar(industry.head(5), x="Industry", y="Count", title="Top Industries")

    top_salary = filtered_df.sort_values(by="salary_num", ascending=False).head(10)
    fig6 = px.bar(top_salary, x="Company", y="salary_num", title="Top Salaries" )

    return render_template("visuals.html",
        graph1=fig1.to_html(full_html=False),
        graph2=fig2.to_html(full_html=False),
        graph3=fig3.to_html(full_html=False),
        graph4=fig4.to_html(full_html=False),
        graph5=fig5.to_html(full_html=False),
        graph6=fig6.to_html(full_html=False),
    )
    
@app.route("/download")
def download():
    location, rating, about, salary, output = get_user_inputs()
    filtered_df = apply_filters(data, location, rating, about, salary)

    csv = filtered_df.to_csv(index=False)

    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=data.csv"}
    )

app.run(debug = True ,  port = 5000)