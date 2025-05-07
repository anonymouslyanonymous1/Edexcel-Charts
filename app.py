from flask import Flask, flash, redirect, render_template, request, session
import re
import os
import json
import plotly.graph_objects as go
from dateutil import parser

app = Flask(__name__)
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")
@app.route("/graph", methods=["GET", "POST"])
def graph():
    subject = request.args.get("options")
    unit = request.args.get("unit")
    grade = request.args.get("grade")
    info = []
    if grade == "full":
        grade = "Full UMS"
        for file in os.listdir(f"static/{subject}/{unit}"):
            data=open(f"static/{subject}/{unit}/{file}", "r")
            data = json.load(data)
            year = re.sub(".json","", file)
            if not data:
                continue          
            else:
                full_ums_mark = data[0]["RAW"]
                ums_mark = data[0]["UMS"]
                for row in data:
                    if row["RAW"] < full_ums_mark and row["UMS"] == ums_mark:
                        full_ums_mark = row["RAW"]
                    else:
                        continue
                info.append([year, full_ums_mark])
    else:
        for file in os.listdir(f"static/{subject}/{unit}"):
            data=open(f"static/{subject}/{unit}/{file}", "r")
            data = json.load(data)
            year = re.sub(".json","", file)
            if not data:
                continue
            elif grade == "*" and data[0]["GRADE"] != grade:
                grade="[There is no A* for this unit!]"
            else:
                full_ums_mark = data[0]["RAW"]
                ums_mark = data[0]["UMS"]
                for row in data:
                    if row["RAW"] < full_ums_mark and row["GRADE"] == grade:
                        full_ums_mark = row["RAW"]
                    else:
                        continue
                info.append([year, full_ums_mark])

    data = info
    data.sort(key=lambda x: parser.parse(x[0]))
    x_labels = [item[0] for item in data]
    y_marks = [item[1] for item in data]
    hover_text = [f"{label}: {mark}" for label, mark in data]

    # Create the plot
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_labels,
        y=y_marks,
        mode='lines+markers',
        marker=dict(size=8, color='white', symbol="cross"),
        text=hover_text,
        hoverinfo='text',
        line=dict(color='#c0fa00', width=2)
    ))

    # Layout settings
    fig.update_layout(
        title=f"Goal: {grade} for {unit}",
        xaxis_title="Year",
        yaxis_title=f"Minimum Marks for {grade}",
        hovermode="x unified",
        xaxis_tickangle=-45,
        plot_bgcolor='black',  # Set plot background to black
        paper_bgcolor='black',  # Set paper (overall plot area) background to black
        font=dict(color='white'),  # Set font color to white for visibility
        xaxis=dict(showgrid=True, gridcolor='gray'),  # Gridlines color (gray for visibility)
        yaxis=dict(showgrid=True, gridcolor='gray')   # Gridlines color (gray for visibility)
    )

    # Export to HTML
    fig.write_html("/tmp/graph.html")
    file = open("/tmp/graph.html", "r", encoding="utf-8")
    html = file.read()
    html = re.sub("<body>", '<body style="background-color:black;">', html)
    html = re.sub('<head><meta charset="utf-8" /></head>', f'<head><meta charset="utf-8" /><title>{unit}</title> \n <link rel="icon" href="../static/icon.svg" type="image/svg+xml"></head>', html)
    return html, 200, {'Content-Type': 'text/html'}
if __name__ == '__main__':  
   app.run()
