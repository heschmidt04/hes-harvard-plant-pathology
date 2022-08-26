CSCI E14A - Building Interactive Web Applications for Data Analysis

# Plant Pathology Image Classification

## Project Plan

**Meeting Times**: Tuesdays 7:00 - 8:00 pm, Fridays 7:00 - 8:00 pm (1 hour)

**Google Meet Link**: https://meet.google.com/zvi-xxyh-igp

**Github Repo**: https://github.com/Harvard-DCE-BIWADA/S14A2022-final-plantpathology

**Website Location**: https://cryptic-refuge-39883.herokuapp.com/ **COMPLETED**

### Team Members

* **Andrea Cheang** - anc9890@g.harvard.edu
* **Heidi E. Schmidt** - hes350@g.harvard.edu
* **Matthew Thanos** - mpt986@g.harvard.edu

## Project Basics

The purpose of this project is to develop an image classification model to accurately classify a given leaf image from the test dataset to a particular disease category, and to identify the diseases of a plant from an single leaf image. This model is a multi-classification model, where it acn identify multiple types of diseases on a leaf.


## Project Structure

/app/ - /project/
/app/app.py - /project/app.py
/app/templates - /project/templates

/app/static - /project/static

The main components of the app are:

1. **Base** - It consists of a function for users to upload their images, where our application will classify the health of the plant and return the health category of the plant.

2. **Model** - The image classification moddel is a multi-classification modul, built using Tensorflow.


## Project Timeline

# Milestone 1 Tasks

### Andrea Cheang, Heidi E. Schmidt, Matthew Thanos

1. Github repository **COMPLETE**

### Heidi E. Schmidt
1. Process book **COMPLETE**
1. Project plan **COMPLETE**

### All:
1. Choose data set **COMPLETE**
1. Cite all work **COMPLETE**


# Milestone 2 Tasks

1. Clean Dataset - Everyone **COMPLETE**
- EDA: Find the percentage of 5 categories (plot bar chart); Find out image dimensions (plot scatterplot)
2. Create Heroku app - Andrea **COMPLETE**
- Copy over Lab 1 app structure
3. Come up with write-up on goal of the project and description of dataset - Matthew **COMPLETE**


# Milestone 3 Tasks

Create MVP
1. Train the model - Andrea **COMPLETE**
2. Do up frontend of website - Matthew **COMPLETE**
3. Do up backend (Connect to a database) - Heidi **COMPLETE**


# Milestone 4 Tasks
1. Have a placeholder page for the login **COMPLETE**
2. Cleaning up the Flask and Jinja templates **COMPLETE**
3. Include text blurbs to give a more detailed explanation on what the disease is **COMPLETE**


# Milestone 5 Tasks
1. Retraining the CNN Model **COMPLETE**
2. Display example classifications along with the prediction output in the front end **COMPLETE**
3. Create functionality for users with accounts and those without accounts **COMPLETE**
- Log-In function for users with accounts, they will be able to access their history of uploaded images and the respective classifications
- Prompt Sign-Up function for users without accounts

# Screencast Link
https://drive.google.com/file/d/1wszTWJBlT1zyA6S9X2Ar2wFzA_l_QHaw/view?usp=sharing

# References & Citations
- [The Plant Pathology Challenge 2020 data set to classify foliar disease of apples by Ranjita Thapa, Kai Zhang,Noah Snavely, Serge Belongie,Awais Khan.](https://bsapubs.onlinelibrary.wiley.com/doi/10.1002/aps3.11390 "The Plant Pathology Challenge 2020 data set to classify foliar disease of apples")
- [Kaggle competition](https://www.kaggle.com/competitions/plant-pathology-2021-fgvc8/overview "Kaggle competition")
- [Multi Label Classification](https://github.com/ashrefm/multi-label-soft-f1/blob/master/Multi-Label%20Image%20Classification%20in%20TensorFlow%202.0.ipynb)
- [Soft UI Design System](https://github.com/app-generator/flask-soft-ui-design)
- [Lab 6](https://github.com/Harvard-DCE-BIWADA/S14A2022/tree/main/lab6)
- [Lab 7](https://github.com/Harvard-DCE-BIWADA/S14A2022/tree/main/lab7)
