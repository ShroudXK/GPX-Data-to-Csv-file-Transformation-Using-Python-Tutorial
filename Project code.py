#!/usr/bin/env python
# coding: utf-8

# ## IS 305 Final Project
# ### Project Name:  GPX Data to Csv file Transformation Using Python Tutorial
# #### Goal: Learn what a GPX file is and extract useful data from it using the most basic Python.

# #### Informal Statement to Faculty:
# This project aims to build a simple, beginer-friendly workshop that teaches how to convert a GPX file into a CSV. It targets those who have already know some basic Python skills, like variables, loops, functions, lists and dictionaries, but have never worked with GPX or XML data before. The lesson will show how GPS trackpoints (latitude, longitude, elevation) are stored into a GPX file, the methods of extracting the points into usable Python XML tools and how we can use the points to compute such useful trail statistics as segment distance, cumulative distance, elevation gain and average grade using the Haversine formula. At the end readers will have a pipeline that reads a real GPX file and gives you a clean CSV that can drop into Excel or Google Sheets to continue working with, together with some advice on what problems a beginner might run into, and how you can go about debugging them.

# #### PART 1: Understanding and Reading a GPX File
# ##### 1.1 Introduction
# 
# GPS data shows up in a lot of everyday tools, like fitness applications or even urban development. Many of those tools store the location data as a GPX file, which is essentially an organized XML format storing a set of the geographical points in time. The use of GPX files, is far too ordinary, however, in order to be very user-friendly, at least at the very beginning. So when you are opening a GPX file, you normally make fun of the nested tags, the attributes and that vile XML syntax that can seem like a minefield if you first encounter XML. And coincidentally, the vast majority of data-analysis processes that we perform accept flat, tabular data-models such as CSV, which are so much simpler to open, inspect and manipulate.
# 
# The aim of this workshop is to go through how to transform a GPX file to a clean CSV dataset with just a bit of Python. This is an important skill since format conversion is a very common data-processing task: in real life, data is less often given to you in the form that you want to analyze. Knowing how to extract the bits you are interested in, having a foreign format of file, and convert it into a more accessible format is a crucial skill of any person who is doing data-work.
# 
# We are going to perform this with a GPX track file by taking the latitude, longitude, and elevation numbers of each of the points that have been prepared for this lesson. We will then do those points one at a time in order to produce useful trail statistics such as distance travelled, elevation gain and average grade. In between we will discuss the reasons why GPS distance calculations require special treatment, what are some challenges beginners might run into, and how to style your code to make every step of your working process self-aware and simple to debug.
# 
# The workshop is designed for those learners who have no prior knowledge using GPS data and XML files but already know the basics of Python. 

# ##### 1.2 What Is Inside a GPX File? 
# A GPX file isn’t magic. It’s just XML, which is a text format that uses “tags” (like HTML).
# 
# **Small Example 1:** A single GPS point looks like this:
# <trkpt lat="40.123456" lon="-105.456789">
#     <ele>1825.4</ele>
#     <time>2024-03-10T15:24:18Z</time>
# </trkpt> 
# 

# A single GPS point in a GPX file looks like this:
# 
# ```xml
# <trkpt lat="40.123456" lon="-105.456789">
#   <ele>1825.4</ele>
#   <time>2024-03-10T15:24:18Z</time>
# </trkpt>
# ```
# 
# Code breakdown:
# ```
# <trkpt> means “track point”
# ```
#     `lat=""` and `lon=""` means stored as attributes
# ```
# <ele> means elevation in meters
# 
# <time> means when the point was recorded
# ```
# A GPX file is just hundreds or thousands of these in a row.
# 

# ##### 1.3. What We Need to Pull From the gpx file:
# 
# For our project, we want Three pieces of data from each track point:
# 
# - **Latitude**  
# - **Longitude**  
# - **Elevation**  
# 
# Eventually we'll calculate:
# - **Distance between consecutive points**
# - **Elevation gain/loss**  
# - **Slope / grade (%)**
# 
# But first, we need a clean list of all the points!

# ##### 1.4. How Do We Read GPX Files in Python?
# We'll be using Python's built-in module:
# 
# `xml.etree.ElementTree as ET`
# 
# **Little background info:**
# 
# GPX files are written in XML, which is a structured text format that uses nested tags to represent data. Unlike CSV files, where each row is flat and easy to read, XML files are hierarchical: tags can contain other tags, attributes, and text values. Because of this structure, we need a tool that can understand XML and let us navigate through it in a controlled way.
# 
# **For this project**, we use Python’s built-in module `xml.etree.ElementTree`, usually imported as `ET`. This module is part of the Python standard library, which means it comes pre-installed with Python and does not require downloading or configuring any external packages. That makes it a good choice for beginners and for simple and practical tasks. There are more powerful XML libraries available, `ElementTree` is lightweight and works well for reading structured files like GPX when the file size is reasonable.
# 
# **IN SHORT:** This module lets Python read XML files without installing anything extra.

# ##### 1.5 Step-by-Step: Let’s Open the GPX File
# Here is the code showcase in Python:

# In[16]:


import xml.etree.ElementTree as ET
#demo file here
gpx_file = "001-multiuse-all-uses (1).gpx"

tree = ET.parse(gpx_file)
#This uses ET.parse() to read the entire GPX file and create a "tree" object representing the XML structure.
root = tree.getroot()
#This grabs the top-level (root) element of the XML tree, usually the <gpx> tag in GPX files.
print("Root tag:", root.tag)


# Okay, now I am sure you gonna ask for this weird output, what is it? Why it looks like some strange, creepy web link? 
# 
# DON'T PANIC! 
# 
# ##### Understanding Namespaces in GPX Files:
# One of the first confusing moment when working with GPX files in Python is that things seem to “silently fail.” You might write code that looks perfectly reasonable, such as searching for all <trkpt> elements, but unluckily, only to find that Python returns an empty list. No error, no warning, just no data. This is a very common beginner experience when working with XML-based formats like GPX.
# 
# **The reason** this happens is that GPX files use something called an **XML namespace**. 
# 
# **XML namespace:** An XML namespace does not mean that there are actually spaces in the tag name, and it does not change how the tag looks inside the file. Instead, a namespace is a way to uniquely identify which specification a tag belongs to. You can think of it as a label or “domain name” attached to a tag so that different XML standards do not accidentally reuse the same tag names with different meanings.
# 
# For example, many XML formats might use a tag called <name> or <point>. Without namespaces, there would be no reliable way to tell whether <point> refers to a GPS location, a 3D model vertex, or something else. A namespace reveals this by attaching a unique identifier, which is usually a URL to every tag in the document.
# 
# **Small Example 2:** In a GPX file, the namespace is defined at the top of the file like this:
# 
# ```xml
# <gpx xmlns="http://www.topografix.com/GPX/1/1">
# ```
# 
# This line means: all tags inside this file follow the GPX 1.1 specification published by Topografix. The URL itself is not something the file visits; it is simply a globally unique name used to identify the GPX standard.
# 
# **Wait**, then what is GPX 1.1? IS it something about version, or what?
# 
# **What Does GPX 1.1 Standard Mean?**
# 
# GPX is a defined file format, and like many technical standards, it has versions. GPX 1.1 is the most widely used and current version of the GPX specification. The standard defines:
# 
#     Tags that are often used (such as <trkpt>, <ele>, <trk>)
# 
#     What attributes those tags can have (latitude, longitude, etc.)
# 
#     How GPS tracks, routes, and waypoints are structured
# 
# When a GPX file says it uses the GPX 1.1 namespace, it is explicitly stating: “These tags mean what the GPX 1.1 documentation says what they mean.” This is important for software compatibility issues.

# ##### What Goes Wrong If We Ignore the Namespace?
# **Small Example 3:** If we try to find all track points like this:
# ```python
# root.findall(".//trkpt")
# ```
# Sadly, Python will return you an empty list, even though the file clearly contains track points. This happens because the actual tag name is not `trkpt`, but:
# ```
# {http://www.topografix.com/GPX/1/1}trkpt
# ```
# **This is one of the most common beginner mistakes when working with XML and GPX files**

# ##### How ElementTree Handles Namespaces?
# Now, we've grabbed some ideas about some insights about the XML data file. What's next is how Python, specifically, how `ElementTree` handle those namespaces ?
# 
# Instead of hard-coding the full namespace URL everywhere, a cleaner approach is to extract it once from the root tag and reuse it. This keeps the code readable.
# ```python
# import xml.etree.ElementTree as ET
# #input the file here: 
# gpx_file = 
# 
# tree = ET.parse(gpx_file)
# 
# root =tree.getroot()
# 
# print("Root tag:", root.tag)
# if "}" in root.tag:
#     namespace = root.tag.split("}")[0] + "}"
# else:
#     namespace = ""
# 
# track_points = root.findall(".//" + namespace + "trkpt")
# ```
# 
# By handling namespaces this way, we avoid silent failures and gain more understanding of how XML data is structured. More importantly, this approach builds a useful skill because many real-world data formats use namespaces as well, it is important to know how to recognize and handle them.

# ##### 1.7 Building a Function to Extract Points
# We want a function that:
# 1. Opens the GPX file
# 2. Detects whether there’s a namespace
# 3. Finds all the `<trkpt>` tags
# 4. Reads `lat` / `lon` / `elevation`
# 5. Stores each point in a dictionary
# 6. Returns a list of all points
# 
# **Parse the GPX file into an XML “tree”**
# 
# We start by letting `ElementTree` read the GPX file. Think of this as loading the file into a structured object so we can search for tags like <trkpt>.
# ```python
# tree = ET.parse(gpx_path)
# root = tree.getroot()
# ```
# 
# **Handle namespaces**
# 
# A common GPX beginner trap is that you try to find <trkpt> tags, as we talked about earlier, and you will get zero results, even though the file clearly has track points. That happens because many GPX files use an XML namespace.
# 
# So we check whether the root tag contains a namespace, and we prepare the correct tag strings for `findall()`
# 
# ```python
# ns = {}
# if "}" in root.tag:
#     uri = root.tag.split("}")[0].strip("{")
#     ns["gpx"] = uri
#     trkpt_tag = ".//gpx:trkpt"
#     ele_tag = "gpx:ele"
#     time_tag = "gpx:time"
# else:
#     trkpt_tag = ".//trkpt"
#     ele_tag = "ele"
#     time_tag = "time"
# ```
# 
# We build this block because we want to make the same function work across GPX files, even if some use namespaces and some don’t.
# 
# **Loop through trackpoints**
# 
# A GPX file contains lots of track points. That’s why we use a loop, we want to do the same extraction process for every <trkpt> tag.
# 
# ```python
# points=[]
# 
# for trkpt in root.findall(trkpt_tag, ns):
#     ...
#     points.append(point)
# ```
# 
# The core idea of this loop is that each <trkpt> element in the GPX file represents one GPS point. Inside the loop, we read one `trkpt` at a time and convert it into one Python dictionary containing latitude, longitude, and elevation.
# 
# By appending each dictionary to a list, the entire GPX track becomes a list of point dictionaries, which is much easier to work with in later steps.
# 
# **Extract lat/lon/ele/time from each <trkpt>**
# 
# `lat` and `lon` are stored as attributes inside the loop, so we will use `.get()`. And we will use `.find()` since elvation and time are child tags.
# 
# ```python
# lat = float(trkpt.get("lat"))
# lon = float(trkpt.get("lon"))
# 
# ele_elem = trkpt.find(ele_tag, ns)
# ele = float(ele_elem.text) if (ele_elem is not None and ele_elem.text) else None
# 
# time_elem = trkpt.find(time_tag, ns)
# time_text = time_elem.text.strip() if (time_elem is not None and time_elem.text) else None
# ```
# Be aware, we need to allow elevation/time to be **None** because GPX files aren’t always consistent as they will update regularly.
# 
# **Store 'point' as a dictionary AND Return the list**
# 
# A dictionary is a convenient format because later we can do things like `point["lat"]` and it reads clearly.
# 
# ```python
# point = {"lat": lat, "lon": lon, "ele": ele, "time": time_text}
# points.append(point)
# ```
# 
# Return the list:
# 
# ```python
# return points
# ```
# 
# Full part walkthrough:

# In[39]:


def load_gpx_points(gpx_path):
    
    tree = ET.parse(gpx_path)
    root = tree.getroot()

    ns ={}
    if "}" in root.tag:
        uri = root.tag.split("}")[0].strip("{")
        ns["gpx"] = uri
        trkpt_tag = ".//gpx:trkpt"
        ele_tag = "gpx:ele"
        time_tag = "gpx:time"
    else:
        trkpt_tag = ".//trkpt"
        ele_tag = "ele"
        time_tag = "time"

    points = []

    for trkpt in root.findall(trkpt_tag, ns):
        lat = trkpt.get("lat")
        lon = trkpt.get("lon")

        if lat is None or lon is None:
            continue  

        lat = float(lat)
        lon = float(lon)
        ele_elem = trkpt.find(ele_tag, ns)
        ele = float(ele_elem.text) if (ele_elem is not None and ele_elem.text) else None
        time_elem = trkpt.find(time_tag, ns)
        time_text = time_elem.text.strip() if (time_elem is not None and time_elem.text) else None

        point = {
            "lat": lat,
            "lon": lon,
            "ele": ele,
            "time": time_text
        }

        points.append(point)

    return points


# ##### 1.8. Testing the Function
# Run this in your Jupyter notebook: (you can insert your own gpx file by input their own file path)
# 

# In[18]:


#example code showcase:
points = load_gpx_points("001-multiuse-all-uses (1).gpx")

print("Total points:", len(points))
print(points[0])  # look at the first point


# You should see something like:
# ```
# Total points: 165
# {'lat': 38.21371, 'lon': -87.22078, 'ele': 168.3, 'time': '2025-11-12T09:18:43-08:00'}
# ```
# 
# If you see something similar, congratulations! You just extracted usable GPS data!
# 
# This is the foundation for everything else in the project.

# ##### Part 1 Sum-up:
# By the end of this section, the student should understand:
# ```
# -What GPX files are
# -How XML tags store GPS information
# -Why Python’s built-in `ElementTree` module works for this task
# -How to loop through <trkpt> elements
# -How to extract: latitude / longitude / elevation / timestamp
# -How to store all points in a list for later calculations
# ```
# Now your dataset is ready, and in Part 2 we’ll start doing actual data processing:
# ```
# -distances
# -elevation gain
# -slopes / gradients

# #### PART 2: Calculating Useful Trail Data
# ##### 2.1. Introduction: Why Do We Need This?
# Now that we can read our GPX file and extract a list of points, the next thing we want is to turn these raw coordinates into meaningful trail statistics.
# 
# When mountain bikers, hikers, or runners look at a trail summary, they might need things like:
# ```
# -How long is the trail?
# -How much climbing is there?
# -What is the average grade?
# -Is this a chill trail? A climb? A black-diamond suffer-fest?
# ```
# 
# GPX file already contains the information, but it's hidden in the form of latitude, longitude, and elevation data. Our job is to calculate those trail stats ourselves.
# 
# To do that, we need to:
# ```
# -Loop through pairs of consecutive points
# -Compute the distance between each pair
# -Compare elevations
# -Add up only the positive elevation differences
# -Use totals to compute grade percentages
# ``` 
# This is the heart of the project, the real “data processing” part.

# ##### 2.2. How Do We Compute Distance Between Two GPS Points?
# We can’t just use regular geometry, because the Earth is round-ish. So instead, we use the **haversine formula**.
# ##### The Haversine Formula in short:
# It answers the question: 
# **"How far apart are two points on Earth if I only know their latitude and longitude?"**
# ```
# - Earth is a sphere 
# - Straight line through the Earth is hard to calculate
# - Haversine gives the shortest distance over the Earth's surface (great-circle distance)
# ```
# It's perfect for our GPX project. We use it to measure the real distance between two consecutive track points.
# 
# **One-line summary:**  
# Haversine is magic math that turns (`lat1`, `lon1`) to (`lat2`, `lon2`) into actual kilometers/meters, even though Earth is round.
# 
# 
# Small example:
# We will have two points with:
# ```
# -`lat1`, `lon1`
# -`lat2`, `lon2`
# ```
# as our **input**.
# 
# And our **output** will be Distance between them in meters.
# 
# **Main Idea:** We convert lat/lon from degrees to radians, then apply a formula that estimates the arc length on a sphere.

# In[41]:


#example code showcase:
#We will try to calculate the distance from Central Park to Times Square in NYC:
#This example just showcases the math functions to calculate, the logic is the same for any other scenarios
from math import radians, sin, cos, sqrt, atan2

def haversine_example(lat1, lon1, lat2, lon2):
    R = 6371000 
    lat1, lon1 = radians(lat1), radians(lon1)
    lat2, lon2 = radians(lat2), radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return distance

dist = haversine_example(40.7128, -74.0060, 40.7589, -73.9851)  # example: NYC Central Park → Times Square
print("Distance:", dist, "meters")


# ##### 2.3. Concept: How to Calculate Elevation Gain
# For elevation, we only care about climbing, not descending.
# 
# **Rule:**  
# Only **positive** elevation differences count.  
# If the next point is lower then gain = 0 (ignore descents).
# 
# Small example:
# ```
# -Point A : 1800 m  
# -Point B : 1812 m  +12 m gain  
# -Point C : 1790 m  0 m gain
# 

# In[42]:


#example code showcase:
#Example elevations from three consecutive points
ele1 = 1800   # previous point
ele2 = 1812   # current point

# Only count the climb
gain = max(0, ele2 - ele1)


print("elevation difference in meters:", ele2 - ele1)
print("elevation gain counted in meters:", gain)


# 
# A distance helper function:

# In[43]:


import math

def haversine_distance(lat1, lon1, lat2, lon2):
    rlat1 = math.radians(lat1)
    rlon1 = math.radians(lon1)
    rlat2 = math.radians(lat2)
    rlon2 = math.radians(lon2)
    dlat = rlat2 - rlat1
    dlon = rlon2 - rlon1
    a = (math.sin(dlat/2)**2 +
         math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    R = 6371000
    distance = R * c

    return distance


# ##### 2.4 Loop through real GPX points
# 
# **Why we loop through pairs of points?**
# 
# This part is important because distance is not stored per point. A single point is just a location. The idea of 'distance traveled' only makes sense when you compare two locations and try to find how far did we move from point A to point B? That’s why the code loops through pairs of consecutive points.
# 
# This is why the loop starts like this:
# 
# ```python
# for i in range(1, len(points)):
#     p1 = points[i-1]
#     p2 = points[i]
# ```
# 
# The reason why we start at `1` is because it's the cleanest way to have a previous point `i-1` and a current point `i`. If we start with `0`, there will be no previous point for the first value.
# 
# Next line:
# 
# ```python
# d = haversine_distance(p1["lat"], p1["lon"], p2["lat"], p2["lon"])
# total_distance += d
# ```
# 
# This line of code basically help us get the distance between these two consecutive GPS points, then add it into the running total by using haversine distance formula.
# 
# 
# **Elevation gain: why we only add positive changes**
# Elevation gain is not the same as 'ending elevation minus starting elevation' If you go up and down a bunch of times, your total climbing should count all the uphill parts, not cancel out with downhill parts.
# 
# ```python
# diff = p2["ele"] - p1["ele"]
# if diff > 0:
#     total_gain += diff
# ```
# Only uphill segments contribute to gain. Downhill segments are ignored for “gain”
# 
# **Notice**
# 
# Here is a beginner trap: some GPX files have missing elevation values, or some points don’t include <ele>. If we try to subtract None, Python might crash (do not ask why I know this and do not attempt). So this check makes the function more reliable.

# In[22]:


#Full demo walkthrough
points = load_gpx_points("001-multiuse-all-uses (1).gpx")
def compute_trail_stats(points):
    
    total_distance = 0.0
    total_gain = 0.0
    
#loop through pairs of points
    for i in range(1, len(points)):
        p1 = points[i-1]
        p2 = points[i]

        
#distance
        d = haversine_distance(p1["lat"], p1["lon"],
                               p2["lat"], p2["lon"])
        total_distance += d
        
#elevation gain
        if p1["ele"] is not None and p2["ele"] is not None:
            diff = p2["ele"] - p1["ele"]
            if diff > 0:
                total_gain += diff
    
#avoid division by zero
    if total_distance > 0:
        avg_grade = total_gain / total_distance
    else:
        avg_grade = 0
    
    return total_distance, total_gain, avg_grade

#test
dist, gain, grade = compute_trail_stats(points)

print("Total distance (m):", dist)
print("Total elevation gain (m):", gain)
print("Average grade (%):", grade * 100)


# Test of the result:
# Our sample GPX file was downloaded from Trailforks. The original GPX file contains a moutain-bike trail located in Lynnville, Indiana, USA. And from the website, the data shows this trail is about 1.3 mile long (Directly corresponding to our final computed result).
# 
# Access link: https://www.trailforks.com/trails/001-multiuse-all-uses/ 
# 

# ##### PART 3: From raw points to a csv trail file
# **Goal of this part:** By the end of this section, we want to:
# ```
# -Take the points list from Part 1
# -Add useful calculated columns (segment distance, cumulative distance, elevation gain, etc.)
# -Save everything into a CSV file we can open in Excel / Google Sheets.
# ```
# We’re basically going from:
# messy XML GPX to clean spreadsheet-style data

# 3.1 What should each row contain?
# We already have this for each point:
# `lat`
# `lon`
# `ele`
# `time`(we will exclude this since time is not a significant variable that matters)
# 
# Now we’ll add more columns that come from our Part 2 calculations:
# 
# For each point (except the very first), we define:
# 
# -`seg_dist_m` → distance from previous point to this point
# 
# -`cum_dist_m` → distance from start up to this point
# 
# -`seg_gain_m` → positive elevation gain from previous point
# 
# -`cum_gain_m` → total elevation gain so far
# 
# So each row will look like:
# ```python
# {
#   "index": i,
#   "lat": ...,
#   "lon": ...,
#   "ele": ...,
#   "time": ...,
#   "seg_dist_m": ...,  
#   "cum_dist_m": ...,
#   "seg_gain_m": ...,
#   "cum_gain_m": ...
# }
# ```

# ##### 3.2. Small example: How to build one row in csv file?
# 
# Imagine we have two points:
# ```python
# p0 = {"lat": 40.0, "lon": -105.0, "ele": 1800}
# p1 = {"lat": 40.0005, "lon": -105.0005, "ele": 1810}
# ```
# 
# We can do:
# ```python
# seg_dist = haversine_distance(p0["lat"], p0["lon"],
#                               p1["lat"], p1["lon"])
# seg_gain = max(0, p1["ele"] - p0["ele"])
# 
# row1 = {
#     "index": 1,
#     "lat": p1["lat"],
#     "lon": p1["lon"],
#     "ele": p1["ele"],
#     "seg_dist_m": seg_dist,
#     "cum_dist_m": seg_dist,  
#     "seg_gain_m": seg_gain,
#     "cum_gain_m": seg_gain
# }
# ```
# This is the basic logic we will apply in a loop later.

# ##### 3.3 Then, we will try to write a tiny csv file:
# 
# Small example:
# ```python
# headers = ["index", "lat", "lon"]
# 
# rows = [
#     {"index": 0, "lat": 40.0, "lon": -105.0},
#     {"index": 1, "lat": 40.1, "lon": -105.1}
# ]
# 
# with open("tiny_example.csv", "w") as f:
# #write header
#     f.write(",".join(headers) + "\n")
#     
# #write each row
#     for row in rows:
#         values = [str(row[h]) for h in headers]
#         f.write(",".join(values) + "\n")
# ```

# ##### 3.4 Full demo:
# **logic:**
# 
# We’ll write a function that:
# 
# -Takes `points` from Part 1
# 
# -Loops through them in order
# 
# -Calculates segment distance & gain between point `i-1` and `i`
# 
# -Keeps running totals
# 
# -Returns:
# 
# 1. the list of row dictionaries
# 
# 2. total distance, total gain, average grade.
# 
# **Start with the containers and running totals**
# 
# Before we do any looping, we need a place to store rows and totals that we keep updating.
# 
# ```python
# rows = []
# total_distance = 0.0
# total_gain = 0.0
# ```
# 
# Be aware here! If you don’t initialize totals like this, you can’t “accumulate” distance/gain as you move through the points.
# 
# **Handle the empty points case**
# ```python
# if len(points) == 0:
#     return rows, 0.0, 0.0, 0.0
# ```
# 
# Calm down, I know what you are looking at, three 0.0 in a row, right? It's super weird if you first meet stuff like this, but don't be panic. This is a guard case (also called an early exit), it basically means  that if there are no points at all, stop immediately and return safe default values.
# 
# **Add the first row manually**
# 
# This is one of the most “why are we doing this?” moments for beginners.
# 
# The reason we doing this is because the first point has no point before it, which means segment `distance = 0` `segment gain = 0` `cumulative distance/gain = 0`
# 
# We need:
# ```python
# first = points[0]
# first_row = {
#     "index": 0,
#     "lat": first["lat"],
#     "lon": first["lon"],
#     "ele": first["ele"],
#     "seg_dist_m": 0.0,
#     "cum_dist_m": 0.0,
#     "seg_gain_m": 0.0,
#     "cum_gain_m": 0.0
# }
# rows.append(first_row)
# 
# ```
# This makes the table consistent, every point gets a row, including the first.
# 
# Be aware! You should NOT skip the first row or your index will gets you confused.
# 
# **Loop through the rest of the points**
# 
# Now we do the real work: compute stats between point `i-1` and point `i`
# 
# ```python
# for i in range(1, len(points)):
#     p_prev = points[i - 1]
#     p_curr = points[i]
# ```
# 
# Also Be Aware! You should make sure that you DID NOT start at 0 because `i-1` will become `-1`. Python will still run as usual but it grabs the wrong element and will create wrong distance.
# 
# **Compute segment distance and update cumulative distance**
# 
# Now we compute the distance for this segment only:
# 
# ```python
# seg_dist = haversine_distance(
#     p_prev["lat"], p_prev["lon"],
#     p_curr["lat"], p_curr["lon"]
# )
# total_distance += seg_dist
# 
# ```
# `seg_dist` = distance from previous point to current point
# 
# `total_distance` = sum of all segments so far
# 
# 
# **Compute segment gain and update cumulative gain**
# 
# We start with `seg_gain = 0.0` because most segments aren’t pure climbing
# 
# ```python
# seg_gain = 0.0
# if p_prev["ele"] is not None and p_curr["ele"] is not None:
#     diff = p_curr["ele"] - p_prev["ele"]
#     if diff > 0:
#         seg_gain = diff
#         total_gain += diff
# ```
# 
# `diff > 0` means uphill
# 
# `None` checks prevent crashes if elevation is missing
# 
# Be aware that if you firget to do `None` check, it will cause `TypError` when doing subtracting.
# 
# **Build one row for this point and append it**
# 
# Now we create a row dictionary that captures both:
# 
#     the raw point info (lat/lon/ele)
# 
#     the calculated segment + cumulative metrics
# 
# ```python
# row = {
#     "index": i,
#     "lat": p_curr["lat"],
#     "lon": p_curr["lon"],
#     "ele": p_curr["ele"],
#     "seg_dist_m": seg_dist,
#     "cum_dist_m": total_distance,
#     "seg_gain_m": seg_gain,
#     "cum_gain_m": total_gain
# }
# rows.append(row)
# ```
# 
# **Compute average grade at the end**
# 
# We do grade once at the end using cumulative totals
# 
# ```python
# if total_distance > 0:
#     avg_grade = total_gain / total_distance
# else:
#     avg_grade = 0.0
# ```
# 
# **Finally, return everythoing in one package**
# ```python
# return rows, total_distance, total_gain, avg_grade
# ```

# In[29]:


#Full code showcase:
def build_trail_table(points):
#Turn raw GPX points into a list of rows with distances and gains
    rows =[]
    total_distance =0.0
    total_gain = 0.0

#handle the very first point 
    if len(points) == 0:
        return rows, 0.0, 0.0, 0.0

    first = points[0]
    first_row = {
        "index": 0,
        "lat": first["lat"],
        "lon": first["lon"],
        "ele": first["ele"],
        "seg_dist_m": 0.0,
        "cum_dist_m": 0.0,
        "seg_gain_m": 0.0,
        "cum_gain_m": 0.0
    }
    rows.append(first_row)

#loop through the rest of the points
    for i in range(1, len(points)):
        p_prev = points[i - 1]
        p_curr = points[i]

#distance between consecutive points
        seg_dist = haversine_distance(
            p_prev["lat"], p_prev["lon"],
            p_curr["lat"], p_curr["lon"]
        )
        total_distance += seg_dist

#elevation gain
        seg_gain = 0.0
        if p_prev["ele"] is not None and p_curr["ele"] is not None:
            diff = p_curr["ele"] - p_prev["ele"]
            if diff > 0:
                seg_gain = diff
                total_gain += diff

        row = {
            "index": i,
            "lat": p_curr["lat"],
            "lon": p_curr["lon"],
            "ele": p_curr["ele"],
            "seg_dist_m": seg_dist,
            "cum_dist_m": total_distance,
            "seg_gain_m": seg_gain,
            "cum_gain_m": total_gain
        }

        rows.append(row)

#compute average grade
    if total_distance > 0:
        avg_grade = total_gain / total_distance
    else:
        avg_grade = 0.0

    return rows, total_distance, total_gain, avg_grade


# ##### 3.5 Write the table to a csv file:

# In[24]:


#code showcase:
def save_trail_csv(filename, rows):
    headers = [
        "index",
        "lat",
        "lon",
        "ele",
        "seg_dist_m",
        "cum_dist_m",
        "seg_gain_m",
        "cum_gain_m"
    ]

    with open(filename, "w") as f:
        f.write(",".join(headers) + "\n")

        for row in rows:
            values = []
            for h in headers:
                value = row.get(h, "")
                if value is None:
                    values.append("")
                else:
                    values.append(str(value))
            line = ",".join(values)
            f.write(line + "\n")


# ##### 3.6 Final Step:
# Now, we will put everything together:

# In[37]:


#Load gpx
points = load_gpx_points("001-multiuse-all-uses (1).gpx")
print("Number of raw points:", len(points))

#Build the trail table stats
rows, total_distance, total_gain, avg_grade = build_trail_table(points)
print("Total distance (m):", total_distance)
print("Total elevation gain (m):", total_gain)
print("Average grade (%):", avg_grade * 100)

#Save to CSV
output_csv = "trail_output.csv"
save_trail_csv(output_csv, rows)


# ##### Summary of PART 3:
# At this point your project can:
# -Read a GPX file
# -Extract GPS points
# -Compute distances, elevation gain, and grade
# -Build a full table with per-point metrics
# -Export everything to a CSV file
# 
# That’s already a complete data processing pipeline.

# #### PART 4: Final Part -- The Complete pipeline to transform a GPX file to a usable CSV.
# ##### 4.1:Wrap up
# At this point we have all the “building blocks” to build a complete pipeline:
# What we will do in this part:
# 
# `load_gpx_points(gpx_path)` : reads GPX and returns a list of points
# 
# `haversine_distance(...)` : distance between two points
# 
# `build_trail_table(points)` : builds rows + totals
# 
# `save_trail_csv(filename, rows)` : writes CSV
# 
# ##### 4.2 Complete code for trsnforming a gpx file to a cleaned csv:

# In[35]:


#FUll Project code demo
import xml.etree.ElementTree as ET
import math
import csv

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000 

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def load_gpx_points(gpx_path):

    tree = ET.parse(gpx_path)
    root = tree.getroot()

    ns = {}
    if "}" in root.tag:
        uri = root.tag.split("}")[0].strip("{")
        ns["gpx"] = uri
        trkpt_path = ".//gpx:trkpt"
        ele_tag = "gpx:ele"
        time_tag = "gpx:time"
    else:
        trkpt_path = ".//trkpt"
        ele_tag = "ele"
        time_tag = "time"

    points =[]
    for trkpt in root.findall(trkpt_path, ns):
        lat_text = trkpt.get("lat")
        lon_text = trkpt.get("lon")
        if lat_text is None or lon_text is None:
            continue

        lat = float(lat_text)
        lon = float(lon_text)

        ele_elem = trkpt.find(ele_tag, ns)
        ele = float(ele_elem.text) if (ele_elem is not None and ele_elem.text) else None

        time_elem = trkpt.find(time_tag, ns)
        time_text = time_elem.text.strip() if (time_elem is not None and time_elem.text) else None

        points.append({
            "lat": lat,
            "lon": lon,
            "ele": ele,
            "time": time_text
        })

    return points

def build_trail_table(points):
    rows = []
    total_distance = 0.0
    total_gain = 0.0

    if len(points) == 0:
        return rows, 0.0, 0.0, 0.0

    first = points[0]
    rows.append({
        "index": 0,
        "lat": first["lat"],
        "lon": first["lon"],
        "ele": first["ele"],
        "time": first["time"],
        "seg_dist_m": 0.0,
        "cum_dist_m": 0.0,
        "seg_gain_m": 0.0,
        "cum_gain_m": 0.0
    })

    for i in range(1, len(points)):
        p_prev = points[i - 1]
        p_curr = points[i]

        seg_dist = haversine_distance(
            p_prev["lat"], p_prev["lon"],
            p_curr["lat"], p_curr["lon"]
        )
        total_distance += seg_dist

        seg_gain = 0.0
        if p_prev["ele"] is not None and p_curr["ele"] is not None:
            diff = p_curr["ele"] - p_prev["ele"]
            if diff > 0:
                seg_gain = diff
                total_gain += diff

        rows.append({
            "index": i,
            "lat": p_curr["lat"],
            "lon": p_curr["lon"],
            "ele": p_curr["ele"],
            "time": p_curr["time"],
            "seg_dist_m": seg_dist,
            "cum_dist_m": total_distance,
            "seg_gain_m": seg_gain,
            "cum_gain_m": total_gain
        })

    avg_grade = (total_gain / total_distance) if total_distance > 0 else 0.0
    return rows, total_distance, total_gain, avg_grade



def save_trail_csv(csv_path, rows):
    headers = [
        "index", "lat", "lon", "ele", "time",
        "seg_dist_m", "cum_dist_m", "seg_gain_m", "cum_gain_m"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


gpx_file = "001-multiuse-all-uses (1).gpx"
output_csv = "trail_output_Final_demo.csv"



points = load_gpx_points(gpx_file)
print("Number of raw points:", len(points))

rows, total_distance, total_gain, avg_grade = build_trail_table(points)
print("Total distance (in m):", total_distance)
print("Total elevation gain (in m):", total_gain)
print("Average grade (%):", avg_grade * 100)

save_trail_csv(output_csv, rows)


# ##### 4.3 Conclusion / Final Wrap-up:
# The entire project in the context is just a pipeline regarding the way to convert a GPX (raw XML) utilizing simple Python built-in libraries into a processed, useful CSV. I formatted it in this manner (as a couple of small functions rather than a single large block) because it is less complex to learn and debug. When something fails, it is easy to know what step failed: parsing, distance math, table building, or CSV writing. This is also similar to the way data processing would in real life it tends to be in stages and not in one large block of data with a bunch of confusing functions.
# 
# I decided to implement the standard `xml.etree.ElementTree` module of Python to read the GPX file as it will not need any extra installations. Although greater level libraries, which are capable of reading GPX files in a much easier manner than the former, the learner must utilize a built-in XML parser, which requires the learner to comprehend the file structure and the actual data storage mechanism. This makes the experience worthwhile particularly to novices who are yet to understand how the structured data formats such as XML operate.
# 
# Haversine formula is applied to achieve the distance between GPS points as latitude and longitude coordinates are not on the flat on the Earth surface. One of the most frequent mistake of a beginner is the confusion of latitude and longitude with the x and y coordinates and the simple distance equations, which will give wrong results. Using the formula to convert the degree to radian and Haversine formula, the program gives more realistic values of the distance. It has a formula that might seem intimidating to look at initially, but the implementation is done as a small helper function so that a learner can concentrate on its usage and why it is applied instead of remember the formula.
# 
# The other obstacle is the GPX file format. XML namespaces are often contained in many GPX files and when not handled correctly may result in no results being returned by `findall()`. This usually causes confusion to the learners when they observe that zero points have been loaded yet there is definitely data on the file. To avoid this the parsing function verifies the existence of namespace and the search paths are modified. Some GPX files might lack elevation data, or the elevation data is not consistent, therefore the code is designed to avoid mistakes arising when the elevations are not given.
# 
# The created CSV file is a flattened and structured representation of the initial GPX track. A row is associated with a GPS point recorded and the extra columns like the segment distance, the total distance and the elevation gain make the data much easier to work with. When the data is in CSV form it can be opened in spreadsheet software or further analysed using other analysis programs without understanding GPX or XML at all. This is the major reason why the project was driven to convert a specialized format into a general-purpose table.
# 
# Last but not the least, I would like to note the drawback of this method. GPS data are generally noisy and elevation appears to be more so than other parameters, and tiny variations have the ability to swell the values of elevation gain. This implementation is acceptably accurate to be used in learning, although a more sophisticated implementation may involve smoothing, noise reduction, or thresholding very small changes in elevation. In spite of those shortcomings, the project manages to show the entire data-processing pipeline of raw input up to practical output, which is the main learning objective of this tutorial.
