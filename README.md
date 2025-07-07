# 🕸️ Microservice Web Scraping Platform for Customer Review Insights
A production-ready microservice application that automates web scraping of Google Maps business reviews, preprocesses the data, stages it into a PostgreSQL database, and exposes it via a Django Admin user interface (UI). It integrates a full observability stack (Prometheus + Grafana) to expose Docker container and application system metrics on Grafana dashboards. The software architecture follows a microservice design and is deployed using docker containers.

## Overview
This project demonstrates end-to-end system design skills—from web scraping and data engineering to full-stack application delivery and monitoring. It was built to simulate a real-world pipeline for collecting and visualizing customer sentiment in the food service industry.

## Features
* Web Scraper: Automates scraping of food business listings and customer reviews from Google Maps.

* Data Preprocessing Pipeline: Cleans and normalizes raw text, ratings, and review metadata.

* PostgreSQL with Entity Relationship Diagram (ERD): Relationships modeled using Crow’s Foot Notation → ERD → Normalized schema.

* Admin Dashboard: Django Admin UI to explore cleaned and structured review data.

* Dockerized Microservices: Modular architecture using Docker Compose.

* Resource Monitoring Stack: Real-time metrics and container insights using Prometheus, Grafana, Node Exporter, and cAdvisor.

* Interactive Tableau Dashboard: Visualizes sentiment, subcategory ratings (Service, Food, Atmosphere), and review trends.

## Tech Stack
| Component     | Tools Used                                   |
| ------------- | -------------------------------------------- |
| Backend       | Django, Gunicorn (WSGI)                      |
| Database      | PostgreSQL (normalized schema)               |
| Web Server    | NGINX                                        |
| Scraping      | Selenium, BeautifulSoup                      |
| Containers    | Docker, Docker Compose                       |
| Monitoring    | Prometheus, Grafana, Node Exporter, cAdvisor |
| Visualization | Tableau                                      |
| ERD Modeling  | Crow’s Foot Notation + ERD Diagram           |

## Design Flow of the Application
1) Scrape: Automatically extract business reviews from Google Maps using the scraper microservice.

2) Clean: Normalize and preprocess raw review text and subcategory ratings.

3) Stage: Save the cleaned data to CSV and load into a PostgreSQL database.

4) Visualize: Access structured data via Django Admin or Tableau dashboards.

5) Monitor: Track app health and container metrics with Grafana/Prometheus.

## Future Work
* Scheduled Scraping: Add periodic scraping via Celery and Redis to keep the dataset fresh.
* Integrate BERT (Bidirectional Transformer Model)
  I plan to incorporate transformer-based models like BERT to perform advanced Named Entity Recognition (NER) and sentiment analysis on customer reviews. BERT’s bidirectional architecture allows it to capture the full context of each word, making it exceptionally effective for:

  NER: Automatically identifying and extracting key entities such as dish names, staff mentions, location details, and service categories. This enables more granular analytics, deriving structured insights from unstructured review text.

  Sentiment Analysis: Understanding nuanced opinion phrases and emotional tone across reviews—beyond simple positive/negative labels—to assess customer satisfaction more accurately.

* Unit Tests

## Author
Erick X Lopez

## License
MIT — open to contributions and forks.

## Images of Application

## Database Design
<img width="1189" alt="ERD_Business_Logic" src="https://github.com/user-attachments/assets/20a0db5c-7194-4de1-a819-9f38db62a60e" />

<img width="991" alt="DB_Schema_Business_Logic" src="https://github.com/user-attachments/assets/3921be31-a65e-47e9-ae1a-ce28b3ef3119" />

## Admin User Interface

<img width="1199" alt="adminLogin" src="https://github.com/user-attachments/assets/12802ac4-61b3-4170-b117-b370a7ade15f" />
<img width="1439" alt="businesses" src="https://github.com/user-attachments/assets/57419024-5f46-4a53-a786-4148c70b537a" />
<img width="1428" alt="customerReviews" src="https://github.com/user-attachments/assets/4eef46e2-3250-41b6-8169-3b3059e61814" />
<img width="1425" alt="customerReviewsFilter" src="https://github.com/user-attachments/assets/32ee44cf-3db8-4685-87b8-815c59a1d57b" />
<img width="1440" alt="home" src="https://github.com/user-attachments/assets/8c6268c1-2894-47f6-b621-95371d873d22" />
<img width="1197" alt="storesFilter" src="https://github.com/user-attachments/assets/6786fcf5-2a81-4d55-b868-2e00cd135fee" />
<img width="1427" alt="subcategoryReviews" src="https://github.com/user-attachments/assets/e2e3aa38-01e8-4c65-9bd7-33e3e5f4e64c" />
<img width="1428" alt="subcategoryReviewsFilter" src="https://github.com/user-attachments/assets/d13217e8-1f8b-4f64-880e-0ce46c85f452" />

## Resource Monitoring Grafana Dashboards

![resourceMonitoring](https://github.com/user-attachments/assets/3e94d0a4-0a62-41ac-990b-b906db039bdb)


<img width="1434" alt="DockerContainers_Dashboard" src="https://github.com/user-attachments/assets/ae0b8597-7db6-44f9-8a27-dea2c7754eff" />

<img width="1438" alt="NodeExporter_Host_Dashboard" src="https://github.com/user-attachments/assets/cb652e11-308d-4696-b0f6-a185bbf10455" />

<img width="1431" alt="PrometheusDashboard" src="https://github.com/user-attachments/assets/126e430c-fee2-433c-b1b7-e0435f9f7774" />

## Endpoint

<img width="1336" alt="EndPoints" src="https://github.com/user-attachments/assets/5c54ce88-2642-4262-8eca-c23f3b386156" />

