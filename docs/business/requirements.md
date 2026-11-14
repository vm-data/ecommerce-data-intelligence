
# Business Requirements

## 1. Project Overview

**Project:** E-commerce Data Intelligence Platform

**Dataset:** Brazilian E-Commerce Public Dataset by Olist

**Primary Audience:** Technical portfolio and business users

**Project Scope:** Full end-to-end data engineering, analytics,
business intelligence, and machine learning platform.

## 2. Business Objective

Build a centralized data platform that collects, stores,
transforms, and analyzes e-commerce data.

The platform should provide reliable business insights through
dashboards and support predictive analytics through machine
learning models.

## 3. Business Stakeholders

- Sales
- Marketing
- Product Management
- Operations
- Executive Management
- Data Engineering
- Data Science

## 4. Business Use Cases

1. Sales performance analytics
2. Product and category analytics
3. Customer analytics and segmentation
4. Geographical analytics
5. Delivery and operational analytics
6. Predictive analytics and machine learning

## 5. Key Business KPIs

### Sales
- Total orders
- Total revenue
- Average order value
- Monthly revenue
- Month-over-month revenue growth

### Customers
- Unique customers
- Repeat customer rate
- Average customer spend
- Customer recency
- Customer purchase frequency

### Products
- Top-selling products
- Category revenue
- Product sales volume
- Average product price

### Operations
- On-time delivery rate
- Late delivery rate
- Average delivery time
- Average delivery delay
- Order cancellation rate

## 6. Machine Learning Objectives

### Model 1: Late Delivery Prediction
Problem: Classification

Objective: Predict whether an order will be delivered late.

### Model 2: Customer Segmentation
Problem: Clustering

Objective: Group customers based on purchasing behavior
using Recency, Frequency, and Monetary features.

### Model 3: Customer Churn / Repurchase-Risk Analysis
Problem: Predictive scoring or classification

Objective: Estimate whether a customer will fail to make
another purchase within a defined observation window.

Note: This is a historical repurchase-risk proxy, not
subscription-style churn.

### Model 4: Product Recommendation
Problem: Recommendation system

Objective: Recommend products based on historical
customer purchasing patterns.

## 7. Technical Requirements

- Reproducible local development environment
- Automated data ingestion
- Raw and processed data storage
- Reliable data transformations
- Workflow orchestration
- Analytics-ready data models
- Interactive business dashboards
- Machine learning training and evaluation
- Model experiment tracking
- Version-controlled code and documentation

## 8. Expected Deliverables

- End-to-end data pipelines
- Centralized data storage
- Data transformation models
- Analytics-ready datasets
- Business intelligence dashboards
- Four machine learning deliverables
- Technical documentation
- GitHub portfolio repository

## 9. Dataset Limitations

- Historical dataset, not a live transactional feed.
- No reliable real-time inventory information.
- Churn must be approximated using repurchase behavior.
- Delivery prediction must avoid post-delivery data leakage.
- Recommendations will be based on available historical
  purchasing interactions.

## 10. Project Scope

The project will cover all six business use cases and all
four machine learning objectives.

Advanced streaming and distributed processing will be
evaluated separately as extensions, based on available
hardware and learning objectives.
