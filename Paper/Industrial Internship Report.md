Industrial Internship Report
Tech Elecon Pvt. Ltd
Submitted by
Om Patel
12202130501047
In partial fulfillment for the award of the degree of
BACHELOR OF TECHNOLOGY
in
Computer Science and Design
G H Patel College of Engineering & Technology
The Charutar Vidya Mandal (CVM) University,
Vallabh Vidyanagar - 388120
May 2026



ii
ACKNOWLEDGMENT
The completion of this work would not have been possible without the cooperation, coordination, and
support of several individuals. I would like to express my sincere gratitude to Mr. Satyam Raval, my
industry mentor, for his valuable guidance, encouragement, and continuous support throughout the
duration of my internship.
I am also thankful to my internal guide, Dr. Kinjal Joshi for his constant support and valuable suggestions
that helped me successfully complete this internship. I would like to extend my heartfelt thanks to the
Head of the Department, Dr. Sudhir Vegad, and Principal, Dr. Kaushik Nath, for providing a chance
for such a wonderful internship opportunity from the institute.
I am also grateful to all the faculty members of the Department of Computer Engineering, G H Patel
College of Engineering and Technology, Vallabh Vidyanagar, for their guidance and support.
Om Patel
(12202130501047)
iii
ABSTRACT
This report presents GearMind AI, a full-stack industrial gear fault detection and
predictive maintenance dashboard developed during a 16-week internship at Tech Elecon
Pvt. Ltd., Anand, Gujarat.
GearMind AI employs a per-gear-type multi-model architecture with dedicated classifiers
trained for each of the four gear types: Gradient Boosting Machine (GBM) for helical gear
(99.87% accuracy), SVM with RBF kernel for spur gear (82.3%), SVM with RBF kernel
for bevel gear (99.4%), and Gradient Boosting for worm gear (100% accuracy on the
50,000-sample synthetic dataset). Each gear type also has a dedicated RUL regressor,
StandardScaler, and label encoder, trained on physics-informed synthetic sensor data with
SMOTE oversampling to handle class imbalance. The overall system integrates SHAP
(SHapley Additive exPlanations) and LIME (Local Interpretable Model-agnostic
Explanations) explainability frameworks to ensure transparent, interpretable predictions
suitable for maintenance engineers without deep ML expertise.
The system is built on a React 19 frontend with an eight-module interactive dashboard and
a FastAPI backend exposing sixteen REST API endpoints backed by a SQLite database.
An AI Copilot powered by LLaMA 3.3 70B via the Groq API provides natural language
decision support to maintenance personnel. Additional modules include a Manufacturing
QC checker with AGMA-grade compliance, Vibration and PHM analysis with FFT
spectral decomposition, a Differential Evolution-based parameter optimizer, and an AIgenerated
seven-section maintenance report with PDF export capability.
The manufacturing QC module achieved a 96% parameter pass rate during validation.
The system maintains a sub-300ms API response time for full prediction plus SHAP
computation. Cost-benefit analysis demonstrates savings of Rs. 4.05 to 4.68 Lakh per gear
unit when early fault detection replaces failure-driven maintenance. This project
demonstrates the practical applicability of explainable AI, full-stack ML system
development, and industrial IoT concepts in a real-world manufacturing context.
iv
List of Figures
Fig 1.1 Tech Elecon Organization Chart. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 0 3
Fig 2.1 Service Process Flow – Tech Elecon Pvt. Ltd.. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 05
Fig 3.1 GearMind AI System Development Life Cycle. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 11
Fig 3.2 P roject Timeline – Gantt Chart. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
Fig 3.3 Use Case Diagram — User Roles and Permissions. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
Fig 4.1 Data Flow Diagram — Level 1. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
Fig 5.1 System Architecture Diagram. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
Fig 5.2 Sequence Diagram – Prediction Request Flow. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
Fig 5.3 Entity Relationship Diagram (ERD) — Database Schema. . . . . . . . . . . . . . . . . . . . . . . . . . 22
Fig 6.1 ML Pipeline Activity Diagram. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28
Fig 6.2 Screenshot: Login Page. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33
Fig 6.3 Screenshot: Main Dashboard. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34
Fig 6.4 Vibration & PHM Analysis Page. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 35
Fig 6.5 Screenshot: SHAP + LIME Explainability View. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 36
Fig 6.6 Screenshot: What-If Optimizer Module. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 37
Fig 6.7 Screenshot: Manufacturing QC Module. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 38
Fig 6.8 Screenshot: Reliability and Fatigue Data Page. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 39
Fig 6.9 Screenshot: Staff Directory and Shift Schedule. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 40
Fig 6.10 Screenshot: AI Report Generator Output. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 41
Fig 6.11 Screenshot: AI Copilot Chat Widget. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 43
Fig 6.12 Screenshot: Cost Impact Analysis Module. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 44
Fig 6.13 Screenshot: Model Comparison Page. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 45
Fig 6.14 History Module. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 46
v
List of Tables
Table 1.1 Tech Elecon Product Portfolio. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 02
Table 2.1 Major Equipment at Tech Elecon – Technical Specifications . . . . . . . . . . . . . . . . . . . . . 04
Table 3.1 Technology Stack Summary. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 08
Table 3.2 Literature Review Summary — Key Papers. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
Table 3.3 Roles and Responsibilities. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
Table 4.1 Feasibility Analysis — Technical, Economic, Operational, Time. . . . . . . . . . . . . . . . . . 15
Table 4.2 Functional Requirements Specification. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
Table 5.1 Database Schema — gear_history Table Key Fields. . . . . . . . . . . . . . . . . . . . . . . . . . . . 22
Table 5.2 RBAC Role Permissions Matrix. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25
Table 5.3 FastAPI Endpoint Specifications — All 10 Endpoints. . . . . . . . . . . . . . . . . . . . . . . . . . . 25
Table 6.1 ML Model Performance Comparison — All 5 Models. . . . . . . . . . . . . . . . . . . . . . . . . . 30
Table 6.2 Cost Impact Model — Per Gear Unit (INR). . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 44
Table 7.1 Test Cases — Fault Prediction Module. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 48
Table 7.2 Test Cases — API Endpoints (Backend). . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 49
Table 7.3 Test Cases — Frontend UI Modules. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 50
Table 8.1 Problems Encountered and Solutions. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 53
Table 8.2 Future Enhancement Roadmap. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 55
vi
Abbreviations
AI Artificial Intelligence
ML Machine Learning
XAI Explainable Artificial Intelligence
GBM Gradient Boosting Machine
XGB XGBoost — Extreme Gradient Boosting
RF Random Forest
SVM Support Vector Machine
LR Logistic Regression
SHAP SHapley Additive exPlanations
LIME Local Interpretable Model-agnostic Explanations
LLM Large Language Model
RUL Remaining Useful Life
PHM Prognostics and Health Management
FFT Fast Fourier Transform
RMS Root Mean Square
MTBF Mean Time Between Failures
AGMA American Gear Manufacturers Association
API Application Programming Interface
REST Representational State Transfer
RBAC Role-Based Access Control
QC Quality Control
DFD Data Flow Diagram
ERD Entity Relationship Diagram
SDLC Software Development Life Cycle
SQLite Self-Contained Serverless SQL Database Engine
IoT Internet of Things
SMOTE Synthetic Minority Over-sampling Technique
JWT JSON Web Token
CRUD Create, Read, Update, Delete
MLflow Machine Learning Lifecycle Platform
GBM Gradient Boosting Machine
vii
Table of Contents
Declaration ........................................................................................................................... i
Acknowledgement .............................................................................................................. ii
Abstract .............................................................................................................................. iii
List of Figures .................................................................................................................... iv
List of Tables .......................................................................................................................v
List of Abbreviations ......................................................................................................... vi
Table of Contents .............................................................................................................. vii
Chapter 1 Overview of the Company.............................................................................1
1.1 History of Tech Elecon Pvt. Ltd. ...........................................................................1
1.2 Product Portfolio & Scope of Work.......................................................................1
1.3 Organization Chart .................................................................................................2
1.4 Capacity of Plant ....................................................................................................3
Chapter 2 Overview of Departments and Production Layout.....................................4
2.1 Departments at Tech Elecon ..................................................................................4
2.2 Technical Specifications of Major Equipment ......................................................4
2.3 Schematic Production Layout ................................................................................5
Chapter 3 Introduction to Project & Project Management.........................................6
3.1 Project Summary ....................................................................................................6
3.2 Purpose, Objective & Scope ..................................................................................7
3.2.1 Purpose ..........................................................................................................7
3.2.2 Objectives .....................................................................................................7
3.2.3 Scope .............................................................................................................8
3.3 Technology & Literature Review ..........................................................................8
3.3.1 Machine Learning for Gear Fault Detection……………………………….9
3.3.2 Explainable AI (XAI) in Industrial Settings……………………………... 10
3.3.3 Prognostic Health Management (PHM)…………………………………. 10
3.4 Project Planning & Scheduling ............................................................................11
3.4.1 Development Life Cycle .............................................................................11
viii
3.4.2 Project Timeline ..........................................................................................12
3.4.3 Use Case Diagram – User Roles & Permissions ........................................12
Chapter 4 System Analysis ............................................................................................14
4.1 Study of Current System ......................................................................................14
4.2 Problems & Weaknesses of Current System .......................................................14
4.3 Requirements & Feasibility .................................................................................15
4.3.1 Functional Requirements ............................................................................16
4.3.2 Non-Functional Requirements…………………………………………....17
4.4 Proposed System Modules & Data Flow .............................................................17
Chapter 5 System Design...............................................................................................19
5.1 System Architecture & Methodology ..................................................................19
5.2 Sequence Diagram – Prediction Request Flow ....................................................20
5.3 Database Design...................................................................................................21
5.4 Deployment Architecture .....................................................................................23
5.5 Input / Output & Interface Design .......................................................................24
5.5.1 Input Design ................................................................................................24
5.5.2 Output Design .............................................................................................24
5.6 Access Control & Security...................................................................................24
Chapter 6 Implementation ............................................................................................27
6.1 Implementation Environment ..............................................................................27
6.2 ML Pipeline Implementation ...............................................................................27
6.2.1 Synthetic Data Generation ..........................................................................28
6.2.2 Preprocessing and Feature Engineering ......................................................29
6.2.3 Model Training and Evaluation ..................................................................30
6.3 Backend API Implementation ..............................................................................31
6.4 Dashboard Modules & Screenshots .....................................................................31
6.4.1 Login Page ..................................................................................................32
6.4.2 Main Dashboard – Gear Health Module .....................................................33
6.4.3 Vibration & PHM Analysis Page ................................................................34
6.4.4 SHAP + LIME Explainability View ...........................................................35
6.4.5 What-If Optimizer Module .........................................................................37
ix
6.4.6 Manufacturing QC Module .........................................................................37
6.4.7 Reliability & Fatigue Data Page .................................................................38
6.4.8 Staff Directory & Shift Schedule ................................................................39
6.4.9 AI Report Generator ...................................................................................41
6.4.10 AI Copilot Chat Widget ..............................................................................42
6.4.11 Cost Impact .................................................................................................43
6.4.12 Model Comparison......................................................................................44
6.4.13 History Module ...........................................................................................45
6.5 Results & Outcomes ............................................................................................46
Chapter 7 Testing ...........................................................................................................48
7.1 Testing Plan & Strategy .......................................................................................48
7.2 Test Results & Analysis .......................................................................................48
7.2.1 Test Cases – Fault Prediction Module ........................................................48
7.2.2 Test Cases – API Endpoints ........................................................................49
7.2.3 Test Cases – Frontend UI Modules……………………………………….50
Chapter 8 Conclusion and Discussion ..........................................................................52
8.1 Overall Analysis & Internship Viability ..............................................................52
8.2 Problems Encountered & Solutions .....................................................................53
8.3 Summary & Limitations ......................................................................................53
8.3.1 Limitations ..................................................................................................54
8.4 Future Enhancement ............................................................................................54
Chapter 9 References .....................................................................................................56
Appendices ........................................................................................................................58
Appendix I - Activity Logbooks 58
Appendix II - Attendance Sheets 59
Appendix III - Feedback from Industry Mentor 60
12202130501047 OVERVIEW OF THE COMPANY bh
CVM University 1 GCET
1. OVERVIEW OF THE COMPANY
1.1 HISTORY OF TECH ELECON PVT. LTD.
Tech Elecon Private Limited is a private limited company based in Vallabh Vidyanagar,
Gujarat, India. It was incorporated on 30 May 2012 and operates in the field of information
technology and communication services. The company is involved in providing IT
consulting, software development, networking, and communication solutions. Over
the years, it has developed expertise in delivering integrated solutions combining hardware,
software, and networking technologies. Tech Elecon serves a wide range of clients
including industrial, government, and enterprise sectors, offering solutions that support
communication systems and digital infrastructure.
1.2 PRODUCT PORTFOLIO AND SCOPE OF WORK
Tech Elecon Pvt. Ltd. provides a combination of IT services, telecom solutions, and
software development services. Its major offerings include:
⚫ Software Development Services: Custom software, web applications, and enterprise
solutions using technologies such as .NET, PHP, and open-source platforms.
⚫ Networking & Communication Solutions: High-speed internet, IP VPN, bandwidth
services, and secure data communication systems.
⚫ Telecom & Infrastructure Services: VoIP systems, leased line installation, and
cloud-based telephony solutions for businesses.
⚫ Data & Security Solutions: Data storage, system integration, and secure
communication networks.
12202130501047 OVERVIEW OF THE COMPANY bh
CVM University 2 GCET
Table 1.1 Tech Elecon Product Portfolio
Division Product Category Applications
Software Division Custom Software & Web
Apps
Business automation,
enterprise systems
Networking Internet & VPN Services Secure communication,
connectivity
Telecom Solutions VoIP & Cloud Telephony Business communication
systems
IT Services Data Storage & Security Data management and
protection
1.3 ORGANIZATION CHART
Tech Elecon Pvt. Ltd. follows a structured organizational hierarchy consisting of top
management, followed by departmental heads managing various functions such as IT
services, networking, software development, and operations. The company includes teams
working on:
• Software development
• Network infrastructure
• Telecom services
• Client support and maintenance
The IT Department, where this internship was carried out, focuses on software
development, system integration, and technical support.
12202130501047 OVERVIEW OF THE COMPANY bh
CVM University 3 GCET
Fig 1.1 Tech Elecon Organization Chart
1.4 CAPACITY OF PLANT
As an IT and telecom solutions provider, Tech Elecon Pvt. Ltd. operates on a service-based
capacity model rather than manufacturing capacity. The company is capable of handling
multiple projects simultaneously in areas such as:
• Software development
• Network setup and maintenance
• Telecom infrastructure deployment
It utilizes modern tools, communication technologies, and technical expertise to deliver
scalable and efficient solutions to clients across different sectors.
12202130501047 OVERVIEWS OF
DEPARTMENTS AND
PRODUCTION LAYOUT bh
CVM University 4 GCET
2. OVERVIEWS OF DEPARTMENTS AND
PRODUCTION LAYOUT
2.1 DEPARTMENTS AT TECH ELECON PVT. LTD.
Tech Elecon Pvt. Ltd. is organized into various departments, each contributing to its service
delivery:
⚫ IT & Software Development Department: Responsible for application development,
coding, and system design.
⚫ Networking & Telecom Department: Handles internet services, VPN setup, VoIP
systems, and communication infrastructure.
⚫ Data & Security Department: Manages data storage, cybersecurity, and secure
communication systems.
⚫ Support & Maintenance Department: Provides technical support, troubleshooting,
and system updates.
Operations & Management: Oversees project execution, client coordination, and
business operations.
2.2 TECHNICAL SPECIFICATIONS OF MAJOR EQUIPMENT
Table 2.1 Major Equipment at Tech Elecon – Technical Specifications
System / Tool Specification Purpose
Software Technologies .NET, PHP, Open Source Application development
Networking Systems IP VPN, Broadband Connectivity solutions
Telecom Tools VoIP, Cloud Telephony Communication systems
Data Systems Data Storage & Security Data management
12202130501047 OVERVIEWS OF
DEPARTMENTS AND
PRODUCTION LAYOUT bh
CVM University 5 GCET
IT Infrastructure Servers & Network
Devices
System deployment
2.3 SCHEMATIC LAYOUT OF PRODUCTION PROCESS
Tech Elecon Pvt. Ltd. follows a service-based operational workflow. The process begins
with client requirement analysis, followed by system design and planning. Based on
requirements, the company provides solutions such as software development, networking
setup, or telecom infrastructure implementation. After development and configuration, the
system undergoes testing and validation to ensure performance and reliability. The final
solution is then deployed at the client site, followed by continuous monitoring, support,
and maintenance. This workflow ensures efficient delivery of services and long-term
client satisfaction.
Fig 2.1 Service Process Flow – Tech Elecon Pvt. Ltd.
12202130501047 INTRODUCTION TO PROJECT AND PROJECT
MANAGEMENT bh
CVM University 6 GCET
3. INTRODUCTION TO PROJECT AND PROJECT
MANAGEMENT
3.1 PROJECT SUMMARY
GearMind AI is a full-stack industrial gear fault detection and predictive maintenance
system developed as the primary deliverable of the 16-week internship at Tech Elecon Pvt.
Ltd. The project addresses the critical industrial need for automated, data-driven gear health
monitoring in lieu of periodic manual inspections, which are both costly and unable to
detect incipient gear faults before catastrophic failure occurs. The key sentence that
captures the system's value proposition is: GearMind AI enables maintenance engineers at
Elecon to predict gear faults before they occur, quantify remaining useful life, and receive
AI-generated maintenance recommendations all from a web browser, in under 300
milliseconds.
The system is built as a four-component stack: a React 19 single-page application serving
as the user interface, a FastAPI Python backend (gear_api.py, version 5.0) providing 16
RESTful API endpoints, a SQLite database for session and history management, and a suite
of sixteen trained machine learning model artifacts four classifiers, four RUL regressors,
four StandardScalers, and four label encoders, one complete set per gear type (helical, spur,
bevel, and worm), stored as serialized pickle (.pkl) files. An AI Copilot powered by the
Groq API (LLaMA 3.3 70B) provides natural language interaction capabilities. MLflow
v2.7.1 is used for experiment tracking and model registry management throughout the
development lifecycle.
The project was scoped to demonstrate the technical feasibility of AI-driven predictive
maintenance using simulated sensor data engineered to reflect real Elecon gear operating
parameters. The system architecture is designed to support a future migration to live IoT
sensor streams via MQTT or OPC-UA protocols, digital twin integration, and enterprisescale
deployment on cloud infrastructure.
12202130501047 INTRODUCTION TO PROJECT AND PROJECT
MANAGEMENT bh
CVM University 7 GCET
3.2 PURPOSE, OBJECTIVE AND SCOPE
3.2.1 Purpose
The purpose of GearMind AI is to demonstrate that machine learning techniques
specifically ensemble classifiers, explainability frameworks (SHAP, LIME), and large
language models can be applied to industrial gear health monitoring in a manner that is
accurate, interpretable, and actionable for non-specialist users. The system serves as a proof
of concept for Tech Elecon's broader Industry 4.0 digitalization initiative, providing a
working prototype that can be evaluated and iteratively refined using real sensor data as the
IoT infrastructure matures.
3.2.2 Objectives
The primary and secondary objectives of the GearMind AI project were defined jointly
with the industry mentor and the internal guide at the commencement of the internship. The
objectives are:
1. Develop a multi-class gear fault classification model achieving accuracy above 95% on
held-out synthetic test data, using at least five ML algorithms with comparative evaluation.
2. Integrate SHAP and LIME explainability frameworks to provide per-prediction feature
attribution and local linear explanations, ensuring maintenance engineers can understand
the basis of each fault prediction.
3. Build a ten-endpoint FastAPI backend with sub-300ms response time for the critical
prediction + SHAP computation pathway.
4. Design and implement an eight-module React 19 dashboard covering gear health,
vibration analysis, XAI, parameter optimization, QC verification, reliability data, staff
management, and AI report generation.
5. Implement an AI Copilot powered by LLaMA 3.3 70B via the Groq API to provide
context-aware natural language decision support.
6. Conduct comprehensive testing of all system components including API endpoints, ML
model validation, UI module testing, and end-to-end integration testing.
12202130501047 INTRODUCTION TO PROJECT AND PROJECT
MANAGEMENT bh
CVM University 8 GCET
3.2.3 Scope
The scope of GearMind AI includes: (a) fault classification for four gear types — helical,
spur, bevel, and worm gears — using gear-type-specific input feature sets (8 features for
helical and bevel, 6 features for spur, and 13 features for worm); (b) remaining useful life
(RUL) estimation based on a parameterized degradation model; (c) SHAP and LIME
explainability for every prediction; (d) FFT-based vibration spectral analysis and gear mesh
frequency tracking; (e) AGMA-compliant manufacturing QC verification for dimensional
tolerances; (f) cost-benefit analysis comparing preventive, delayed, and failure
maintenance scenarios; and (g) AI-generated maintenance reports with PDF export.
The scope explicitly excludes: (a) real-time IoT sensor connectivity (future scope); (b)
integration with Elecon's SAP ERP system (future scope); (c) production deployment on
cloud infrastructure (future scope); and (d) physical gear rig testing or validation against
real sensor measurements. All machine learning training and evaluation is conducted on
physics-informed synthetic data generated specifically for this project.
3.3 TECHNOLOGY AND LITERATURE REVIEW
The literature underlying GearMind AI spans four domains: machine learning for fault
detection, explainable AI, prognostics and health management (PHM), and full-stack web
development for industrial applications. The following review summarizes the key works
that informed the project's technical design decisions.
Table 3.1 Technology Stack Summary
Layer Technology Version Purpose
Frontend React 19.0 Interactive SPA dashboard
Frontend Recharts 3.8 Data visualization charts
Frontend Tailwind CSS 3.x Utility-first styling
Build Tool Vite 8.0 Frontend dev server and bundler
Backend FastAPI 0.110 REST API framework
Backend Python 3.11 Core runtime
ML scikit-learn 1.4 Model training, SHAP, LIME
ML XGBoost 2.0 XGBoost classifier
12202130501047 INTRODUCTION TO PROJECT AND PROJECT
MANAGEMENT bh
CVM University 9 GCET
ML Tracking MLflow 2.7.1 Experiment tracking, model registry
Explainability SHAP 0.45 SHapley value computation
Explainability LIME 0.2.0.1 Local linear explanations
Database SQLite 3.x Session and history storage
LLM Groq API (LLaMA
3.3 70B)
- AI Copilot and report generation
PDF Export jsPDF 3.8 Client-side PDF generation
3.3.1 Machine Learning for Gear Fault Detection
The application of supervised machine learning to gear fault classification is wellestablished
in the PHM literature. Lei et al. (2018) provide a comprehensive survey of
machinery health prognostics methods, covering data acquisition, feature extraction, and
RUL prediction across multiple machine types including gearboxes. Their taxonomy of
fault indicators vibration-based, temperature-based, and wear-based directly shaped the
eight-feature input schema adopted in GearMind AI.
Gradient Boosting Machines, as formulated by Friedman (2001), and XGBoost as
presented by Chen and Guestrin (2016), are among the most effective algorithms for
structured tabular data classification, which characterizes the sensor feature vectors used in
this project. Both algorithms were included in the GearMind AI model comparison
pipeline, with GBM achieving the highest accuracy (99.87%) on the synthetic test dataset.
Random Forest (Breiman, 2001) was included for its inherent interpretability through
feature importance scores, which complement the SHAP explanations generated for each
prediction. Support Vector Machine and Logistic Regression were included as baseline
models to provide contrast against the ensemble methods and to evaluate the difficulty of
the classification task.
The Isolation Forest algorithm (Liu et al., 2008) was incorporated for real-time anomaly
detection flagging sensor readings that deviate significantly from the training distribution.
This is particularly important in a production setting where the input distribution may shift
as gears age, introducing readings outside the training data manifold.
12202130501047 INTRODUCTION TO PROJECT AND PROJECT
MANAGEMENT bh
CVM University 10 GCET
3.3.2 Explainable AI (XAI) in Industrial Settings
Lundberg and Lee (2017) introduced SHAP values as a unified framework for interpreting
any machine learning model's predictions by computing Shapley values from cooperative
game theory. SHAP provides both local explanations (why a specific prediction was made)
and global feature importance (which features drive model behavior across the dataset). In
GearMind AI, SHAP's TreeExplainer is used for GBM, XGBoost, and Random Forest
models exploiting the tree structure for efficient computation while a background sampler
provides SHAP values for SVM and Logistic Regression via the KernelExplainer.
Ribeiro, Singh, and Guestrin (2016) introduced LIME as a model-agnostic local
explainability method that fits a simple linear model in the neighborhood of a specific
prediction. GearMind AI uses LIME's tabular explainer to generate local linear
approximations for each fault prediction, displaying the signed feature contributions that
most influenced the specific output a format well-suited for maintenance engineers who
need to understand which sensor reading triggered a fault alert.
3.3.3 Prognostic Health Management (PHM)
The Remaining Useful Life (RUL) estimation module in GearMind AI is informed by
reliability theory and Weibull survival analysis, as covered in the PHM survey by Lei et al.
(2018). The Weibull distribution with shape parameter β = 2.5 and scale parameter η =
5,000 hours represents a typical wear-out failure mode for industrial gears, consistent with
industry practice for helical gear assemblies under moderate load. The bathtub failure curve
implemented in the Reliability and Fatigue Data module follows the three-region model:
infant mortality, constant failure rate, and wear-out a foundational concept in reliability
engineering.
12202130501047 INTRODUCTION TO PROJECT AND PROJECT
MANAGEMENT bh
CVM University 11 GCET
Table 3.2 Literature Review Summary — Key Papers
Author(s) Year Topic Contribution to GearMind AI
Lei et al. 2018 PHM Survey Defined feature taxonomy and RUL framework
Friedman 2001 GBM Core algorithm for best-performing model
Chen & Guestrin 2016 XGBoost Second model in comparison pipeline
Lundberg & Lee 2017 SHAP Primary explainability framework
Ribeiro et al. 2016 LIME Secondary, local explanation method
Breiman 2001 Random Forest Baseline ensemble model
Liu et al. 2008 Isolation Forest Anomaly detection layer
AGMA 1997 AGMA 2003-
B97
QC tolerance standards
3.4 PROJECT PLANNING AND SCHEDULING
3.4.1 Development Life Cycle
GearMind AI was developed using an Agile-Scrum methodology with two-week sprint
cycles, adapted to suit the internship structure. The overall 16-week timeline was divided
into eight sprints, each with clearly defined deliverables reviewed with the industry mentor
at the end of each sprint. This iterative approach allowed early delivery of working software
(the ML pipeline was operational by end of Sprint 2) with progressive feature additions in
each subsequent sprint.
The development life cycle followed a standard sequence: requirements gathering and
domain study (Weeks 1–2), data design and ML pipeline (Weeks 3–5), FastAPI backend
(Weeks 6–8), React frontend initial modules (Weeks 9–11), advanced modules and
integration (Weeks 12–14), testing and optimization (Week 15), and documentation and
report writing (Week 16). Daily stand-up meetings with the industry mentor were
conducted via MS Teams when remote, and in-person on campus days.
Fig 3.1 GearMind AI System Development Life Cycle
12202130501047 INTRODUCTION TO PROJECT AND PROJECT
MANAGEMENT bh
CVM University 12 GCET
3.4.2 Project Timeline and Gantt Chart
The project timeline was managed using a Gantt chart developed in MS Project, tracking
task dependencies, milestone dates, and resource allocation across the 16-week period. Key
milestones included: completion of ML model training and evaluation (end of Week 5),
FastAPI backend deployment on localhost (end of Week 8), React dashboard MVP with
three modules (end of Week 11), full eight-module integration (end of Week 14), and final
report submission (Week 16).
Fig 3.2 Project Timeline — Gantt Chart
3.4.3 Use Case Diagram — User Roles and Permissions
The system implements Role-Based Access Control (RBAC) with six distinct user roles,
each with a defined set of permitted and restricted actions. The use case diagram (Fig 3.3)
illustrates the interaction between user roles and system features. The six roles are: Super
Admin (full system access, user management), Shift Supervisor (health dashboard, report
generation, shift scheduling), ML Engineer (model comparison, training logs,
SHAP/LIME), PHM Analyst (vibration analysis, RUL, reliability data), Bevel Gear
Specialist (bevel module, AGMA calculations), and Maintenance Technician (read-only
gear health dashboard).
12202130501047 INTRODUCTION TO PROJECT AND PROJECT
MANAGEMENT bh
CVM University 13 GCET
Fig 3.3 Use Case Diagram — User Roles and Permissions
Table 3.3 Roles and Responsibilities
Role Person Responsibilities
Intern Om Patel Full system design, ML development, React frontend, FastAPI
backend, testing, documentation
Industry Mentor Mr. Satyam Raval Domain guidance, requirement clarification, sprint reviews,
progress evaluation
Internal Guide Dr. Kinjal Joshi Academic supervision, report review, CE evaluations, final
assessment
12202130501047 SYSTEM ANALYSIS bh
CVM University 14 GCET
4. SYSTEM ANALYSIS
4.1 STUDY OF CURRENT SYSTEM
Prior to the GearMind AI project, gear health monitoring at Elecon relied on a combination
of periodic manual inspections, threshold-based vibration alarms, and the experiential
judgment of senior maintenance technicians. Maintenance schedules were governed by
manufacturer-recommended intervals typically 500 to 1,000 operating hours for routine
inspection and 2,500 to 5,000 hours for major overhaul regardless of the actual condition
of the gear unit.
Vibration monitoring was implemented on approximately 30% of critical gear units using
basic threshold alarms configured in the Bentley Nevada 3500 system. These alarms
triggered when vibration RMS exceeded a fixed threshold (typically 7 mm/s for ISO 10816-
3 Zone D), but provided no classification of fault type, no RUL estimate, and no root cause
analysis. Alarm response was manual and depended entirely on the availability and
expertise of the duty maintenance engineer.
Maintenance records were maintained in Microsoft Excel spreadsheets, with no centralized
database, no automated trend analysis, and no digital integration between vibration data,
lubrication logs, and wear measurement records. Manufacturing QC records were stored in
paper-based inspection reports archived in department filing systems, making historical
analysis and trend detection practically infeasible.
4.2 PROBLEMS AND WEAKNESSES OF CURRENT SYSTEM
The current system exhibits several critical weaknesses that impair maintenance
effectiveness and increase operational risk. These weaknesses were identified through
structured discussions with the maintenance department head and three senior technicians
during the first two weeks of the internship.
• No real-time visibility of gear health status across monitored units maintenance
personnel must physically inspect each unit to assess condition.
12202130501047 SYSTEM ANALYSIS bh
CVM University 15 GCET
• Threshold-based vibration alarms trigger only after significant degradation has
already occurred, missing the early fault signatures (e.g., sideband energy growth
at gear mesh harmonics) that precede alarm-level vibration.
• No integration between vibration data, lubrication records, and wear measurements
siloed data prevents comprehensive health assessment.
• No prediction of Remaining Useful Life replacements is either too early (wasteful) or
too late (resulting in catastrophic failure and extended downtime).
• Manufacturing QC checks performed manually with no digital tracking of tolerance
deviations over time, making it impossible to identify systematic process drift.
• Shift scheduling and staff management handled via paper-based systems with no
digital scheduling, conflict detection, or workload visibility.
• Maintenance cost analysis not performed systematically the economic impact of early
intervention versus failure-driven repair is not quantified at the gear unit level.
4.3 REQUIREMENTS AND FEASIBILTY
Table 4.1 Feasibility Analysis — Technical, Economic, Operational, Time
Feasibility
Type
Assessment Justification
Technical Feasible All technologies (React 19, FastAPI, scikit-learn, SHAP, LIME) are
open-source, well-documented, and have active community support. All
required hardware (developer workstation + corporate LAN) is
available.
Economic Feasible Zero licensing cost (open-source stack). Estimated Rs. 4.5 Lakh savings
per gear unit through early fault detection versus failure-driven
maintenance. Development cost is absorbed within the internship
program.
Operational Feasible Web-based dashboard requires only a modern browser. Role-based
access control suits the existing organizational hierarchy. No specialized
hardware at the point of use.
Time Feasible 16-week internship timeline is sufficient for v4.0 development with
simulated sensor data. Agile-Scrum methodology with 2-week sprints
ensures continuous delivery and early risk mitigation.
Legal / Ethical Feasible All data used is synthetically generated; no personal data or proprietary
sensor data is used. All open-source licenses (MIT, Apache 2.0) are
compatible with Tech Elecon's usage requirements.
12202130501047 SYSTEM ANALYSIS bh
CVM University 16 GCET
4.3.1 Functional Requirements
The functional requirements for GearMind AI were derived from the weaknesses identified
in the current system analysis and were validated with the industry mentor. The system
must provide:
1. Real-time gear health dashboard with health score (0–100), fault probability (per
class), and RUL estimation in cycles and operating shifts.
2. Multi-model ML fault classification with automated selection of the best-performing
model and cross-validated performance metrics.
3. SHAP and LIME explainability for every prediction, with feature attribution charts
and root cause analysis text.
4. Vibration analysis with FFT spectral decomposition, gear mesh frequency tracking,
sideband energy detection, and Weibull reliability function visualization.
5. Manufacturing QC verification with AGMA-grade compliance checking for eight
dimensional parameters per gear type.
6. Role-based access control with six distinct user roles, each with defined permissions.
7. AI Copilot for natural language Q&A about gear health and maintenance
recommendations.
8. Automated AI report generation covering seven sections, with PDF export capability.
9. Historical data logging and trend analysis with SQLite persistence and CSV export.
10. Differential Evolution optimizer for safe operating parameter identification.
Table 4.2 Functional Requirements Specification
Req. ID Requirement Priority Status
FR-01 Multi-model fault classification (5
models, 3 classes)
Critical Implemented
FR-02 SHAP global and local explanations per
prediction
Critical Implemented
FR-03 LIME local linear explanation per
prediction
High Implemented
FR-04 FFT vibration analysis with gear mesh
frequency
High Implemented
FR-05 AGMA-compliant QC verification for 8
parameters
High Implemented
FR-06 RUL estimation in cycles and shifts Critical Implemented
FR-07 RBAC with 6 user roles Medium Implemented
FR-08 AI Copilot (LLaMA 3.3 70B / Groq) High Implemented
12202130501047 SYSTEM ANALYSIS bh
CVM University 17 GCET
FR-09 7-section AI maintenance report + PDF
export
Medium Implemented
FR-10 SQLite history with CSV export Medium Implemented
FR-11 Differential Evolution optimizer Medium Implemented
FR-12 Isolation Forest anomaly detection High Implemented
4.3.2 Non-Functional Requirements
Beyond functional requirements, the system must satisfy the following non-functional
requirements: (a) API response time below 300 milliseconds for the prediction + SHAP
pathway; (b) frontend first-load time below 3 seconds on a standard corporate LAN; (c)
support for at least 25 simultaneous gear unit monitoring sessions; (d) data persistence
across browser sessions via SQLite; and (e) cross-browser compatibility with Chrome,
Firefox, and Edge.
4.4 PROPOSED SYSTEM MODULES AND DATA FLOW
The GearMind AI system is architected as eight functional modules, each addressing a
specific aspect of gear health management. The modules are designed to be loosely coupled
each module can be accessed independently via the React navigation sidebar while sharing
a common state management layer that propagates the current gear type, sensor readings,
and prediction results across modules.
The Data Flow Diagram (Level 1) in Fig 4.1 illustrates how sensor input flows from the
user through the React frontend, across the FastAPI backend, through the ML prediction
engine and XAI layer, into the database, and back to the dashboard display components.
The context diagram in Fig 4.2 shows the external entities interacting with GearMind AI
including the maintenance engineer, the LLM API, the MLflow tracking server, and the
future IoT sensor feed.
12202130501047 SYSTEM ANALYSIS bh
CVM University 18 GCET
Fig 4.1 Data Flow Diagram — Level 1
The eight modules are: (1) Gear Health Dashboard the central module displaying health
score, fault probability, and recommended actions for all four gear types (Helical, Spur,
Bevel, Worm), with a 3D interactive gear animation rendered via Three.js and React Three
Fiber; (2) Vibration and PHM Analysis FFT spectra, gear mesh frequency, reliability
curves; (3) SHAP + LIME Explainability side-by-side global and local explanations per
gear type; (4) What-If Optimizer Differential Evolution parameter search with lock/unlock
per parameter; (5) Manufacturing Q AGMA tolerance verification; (6) Reliability and
Fatigue Data MTBF, S-N curve, Weibull, bathtub curve; (7) Staff and Shift Management
personnel directory and shift scheduling; and (8) AI Report Generator LLM-generated
nine-section maintenance report (executive summary, fault assessment, sensor analysis,
root cause, RUL, recommendations, cost-benefit, monitoring protocol, technical
specifications) with client-side PDF export via jsPDF.
12202130501047 SYSTEM DESIGN bh
CVM University 19 GCET
5. SYSTEM DESIGN
5.1 SYSTEM DESIGN AND METHODOLOGY
GearMind AI follows a three-tier client-server architecture: the Presentation Tier (React 19
frontend), the Application Tier (FastAPI Python backend), and the Data Tier (SQLite
database and ML artifact storage). This architecture cleanly separates concerns — the
frontend handles user interaction and visualization, the backend manages business logic
and ML inference, and the data tier provides persistence. The separation also makes future
migration straightforward: the SQLite data tier can be replaced with PostgreSQL without
changes to the API contract, and the frontend can be deployed independently as a static
web application.
The methodology follows a RESTful API design philosophy with JSON payloads, stateless
server-side processing, and structured error responses using HTTP standard status codes.
All ML artifacts (trained model .pkl files, scaler objects, and background datasets for
SHAP) are loaded into memory at server startup and held in process memory for zerolatency
inference. This design achieves sub-300ms response times for the most complex
prediction + SHAP computation pathway.
12202130501047 SYSTEM DESIGN bh
CVM University 20 GCET
Fig 5.1 System Architecture Diagram
5.2 SEQUENCE DIAGRAM — PREDICTION REQUEST FLOW
The sequence diagram in Fig 5.2 illustrates the complete interaction flow for a fault
prediction request. The user adjusts sensor input sliders in the React dashboard, triggering
a debounced (300ms) POST request to /api/predict. The FastAPI backend validates the
input using Pydantic models, then invokes the active ML classifier to generate fault class
probabilities. Simultaneously, the SHAP TreeExplainer (or KernelExplainer for non-tree
12202130501047 SYSTEM DESIGN bh
CVM University 21 GCET
models) computes per-feature Shapley values. The backend also runs the Isolation Forest
anomaly detector to flag out-of-distribution inputs, and computes the RUL estimate based
on the fault probability and gear type parameters. The complete response fault class,
probabilities, health score, RUL, SHAP values, anomaly flag, and recommended actions is
returned as a single JSON object, eliminating round-trip latency for downstream
visualization updates.
Fig 5.2 Sequence Diagram – Prediction Request Flow
5.3 DATABASE DESIGN
The primary data store is a SQLite database file (gear_history.db) managed by the FastAPI
backend. SQLite was chosen for its zero-configuration deployment characteristics,
appropriate for a proof-of-concept system running on a developer workstation. The
database schema is designed for forward compatibility the gear_history table's schema can
12202130501047 SYSTEM DESIGN bh
CVM University 22 GCET
be migrated to PostgreSQL without structural changes, as it avoids SQLite-specific data
types and relies only on SQL standards-compliant constructs.
Fig 5.3 Entity Relationship Diagram (ERD) — Database Schema
Table 5.1 Database Schema — gear_history Table Key Fields
Column Data Type Constraint Description
log_id TEXT PRIMARY
KEY
Unique log identifier (e.g. LOG-00180)
gear_id TEXT NOT NULL Gear unit identifier (e.g. HG-01, SG-02)
gear_type TEXT NOT NULL Helical / Spur / Bevel
timestamp DATETIME NOT NULL Prediction timestamp (UTC)
load_kn REAL NOT NULL Applied load in kN
torque_nm REAL NOT NULL Applied torque in Nm
vibration_rms REAL NOT NULL Vibration RMS in mm/s
12202130501047 SYSTEM DESIGN bh
CVM University 23 GCET
temperature_c REAL NOT NULL Gear temperature in °C
wear_mm REAL NOT NULL Surface wear depth in mm
lubrication_idx REAL NOT NULL Lubrication quality index (0–1)
efficiency_pct REAL NOT NULL Transmission efficiency in %
cycles_in_use INTEGER NOT NULL Cumulative operating cycles
fault_label TEXT NOT NULL No Fault / Minor Fault / Major Fault
fault_probability REAL NOT NULL Probability of predicted fault class
health_score INTEGER NOT NULL Health score 0–100
rul_cycles INTEGER NOT NULL Remaining useful life in cycles
anomaly_flag INTEGER DEFAULT 0 Isolation Forest anomaly flag (0/1)
model_used TEXT NOT NULL ML model name used for prediction
The database also maintains a user’s table for authentication reference (username, hashed
password, role), a sessions table linking user logins to prediction histories, and a reports
table storing generated AI report content for retrieval. The total database size for 10,000
prediction records is approximately 8 MB, well within SQLite's practical limits.
5.4 DEPLOYMENT ARCHITECTURE
The deployment architecture for the development and demonstration environment uses a
single developer workstation running both the React development server (Vite, port 5173)
and the FastAPI backend (Uvicorn, port 8000). MLflow tracking runs on port 5000. The
Groq API for LLM inference is accessed via HTTPS to api.groq.com. The system requires
Node.js 18+ (Node.js 20 LTS tested), Python 3.12 (3.12.4 tested), and approximately 4 GB
of RAM for comfortable operation with all ML models and SHAP background datasets
loaded in memory.
The production deployment target outlined in the future scope would containerize the
FastAPI backend as a Docker image deployed on an AWS EC2 instance, with the React
frontend served via AWS CloudFront CDN and the SQLite database replaced by an AWS
RDS PostgreSQL instance. Live IoT sensor data would be ingested via an AWS IoT Core
MQTT broker with a Kinesis Data Streams pipeline feeding the prediction endpoint.
12202130501047 SYSTEM DESIGN bh
CVM University 24 GCET
5.5 INPUT / OUTPUT AND INTERFACE DESIGN
5.5.1 Input Design
The system accepts eight continuous sensor input features per prediction request. These
features represent the measurable physical parameters of gear operation that have
established correlations with gear health degradation in the PHM literature. Each feature is
provided via an interactive slider in the React dashboard, with real-time debouncing at
300ms to prevent excessive API calls during slider adjustment.
The eight input features and their operational ranges are: Load (kN): 10–500; Torque (Nm):
50–5,000; Vibration RMS (mm/s): 0.1–15; Temperature (°C): 40–120; Wear (mm): 0.0–
2.0; Lubrication Index (0–1): 0.0–1.0; Efficiency (%): 60–100; and Cycles in Use: 0–
100,000. The ranges were calibrated to reflect realistic Elecon gear operating envelopes
based on manufacturer specifications and domain expert consultation.
5.5.2 Output Design
The system produces a rich, multi-component output for each prediction: (a) Fault Class
one of {No Fault, Minor Fault, Major Fault} with probability scores for all three classes;
(b) Health Score (0–100) derived from the fault probabilities and severity weights; (c) RUL
estimate in operating cycles and equivalent shifts; (d) SHAP feature attribution values with
a waterfall visualization; (e) LIME local explanation with a bar chart of signed feature
contributions; (f) Isolation Forest anomaly flag with an out-of-distribution warning if
triggered; (g) Tiered Recommended Actions (Immediate / Within 48 hours / Schedule /
Monitor); and (h) Cost impact comparison across preventive, delayed, and failure
maintenance scenarios.
5.6 ACCESS CONTROL AND SECURITY
GearMind AI implements Role-Based Access Control (RBAC) with six user roles managed
via React context state. Each role is associated with a permissions set that controls which
dashboard modules and API endpoints are accessible. The current v4.0 implementation
12202130501047 SYSTEM DESIGN bh
CVM University 25 GCET
stores role state client-side, designed for straightforward migration to JWT/OAuth2 tokenbased
authentication in a production deployment.
Table 5.2 RBAC Role Permissions Matrix
Role Gear
Health
Vibration XAI Optimizer QC Staff Reports
Super Admin RW RW RW RW RW RW RW
Shift Supervisor RW R R R R RW RW
ML Engineer R R RW RW R R R
PHM Analyst R RW RW R R R R
Bevel Specialist R R R R RW R R
Maintenance Tech. R — — — — — R
R = Read access, RW = Read-Write access, — = No access. All API endpoints validate the
requesting role against the endpoint's permission requirement and return HTTP 403
Forbidden for unauthorized access attempts. Passwords are stored as bcrypt hashes in the
users table, and rate limiting (100 requests per minute per IP) is enforced at the Uvicorn
ASGI level.
Table 5.3 FastAPI Endpoint Specifications — All 10 Endpoints
Method Endpoint Auth
Required
Response
Time
Purpose
POST /api/predict Yes < 300ms Fault classification + RUL + SHAP +
anomaly detection
GET /api/gear-configs Yes < 50ms Gear type configs, unit presets, safe
operating ranges
GET /api/models Yes < 50ms Model comparison metrics (Accuracy, F1,
AUC, CV Mean)
POST /api/chat Yes < 3s (LLM) LLM Copilot Q&A via Groq API
(LLaMA 3.3 70B)
POST /api/report Yes < 5s (LLM) AI-generated 7-section maintenance report
POST /api/optimize Yes < 2s Differential Evolution parameter
optimization
12202130501047 SYSTEM DESIGN bh
CVM University 26 GCET
GET /api/lime Yes < 500ms LIME local explanation for current
prediction
GET
/POST
/DELETE
/api/history Yes < 100ms Gear session history CRUD + CSV export
GET /api/confusionmatrix
Yes < 50ms Model evaluation confusion matrix data
GET /api/bevel-specs Yes < 50ms AGMA 2003-B97 bevel gear rating
calculations
12202130501047 IMPLEMENTATION bh
CVM University 27 GCET
6. IMPLEMENTATION
6.1 IMPLEMENTATION ENVIRONMENT
GearMind AI was developed on a Windows 11 development workstation with an Intel Core
i7-12th Gen processor, 16 GB RAM, and 512 GB NVMe SSD. The operating system for
development was Windows 11 Pro, with Python 3.12.4 installed via Miniconda (as
specified in the project requirements.txt: pandas==2.0.3, numpy==1.24.3, scikitlearn==
1.3.0, xgboost==1.7.6, shap==0.42.1, lime==0.2.0.1, mlflow==2.7.1,
streamlit==1.28.0, plotly==5.17.0) and Node.js 18+ (LTS) installed via the official
installer. Visual Studio Code served as the primary IDE, with extensions for Python
(Pylance, Black formatter), JavaScript/TypeScript (ESLint, Prettier), and REST API testing
(Postman collection runner).
The Python backend environment used a dedicated Conda virtual environment
(gearmind_env) with all dependencies specified in a requirements.txt file for
reproducibility. The React frontend was bootstrapped with the Vite template and managed
with npm. Git version control was used throughout, with a private GitHub repository for
source management and a structured branching strategy: main (stable), dev (integration),
and feature branches per sprint task.
6.2 ML PIPELINE IMPLEMENTATION
The ML pipeline activity diagram (Fig 6.1) shows the complete flow from data ingestion
through model training, evaluation, and deployment.
12202130501047 IMPLEMENTATION bh
CVM University 28 GCET
Fig 6.1 ML Pipeline Activity Diagram
6.2.1 Synthetic Data Generation
Since live IoT sensor data was not available for this internship, a physics-informed
synthetic data generator was developed (data_generator.py) to produce realistic training
datasets. The generator models three fault classes per gear type: No Fault (healthy
operation), Minor Fault (early degradation), and Major Fault (severe degradation requiring
immediate intervention). For helical and bevel gears the labelled fault types are Surface
Pitting, Wear Fatigue, and Thermal Degradation; for spur gears: Tooth Fracture, General
Wear, and Overload Vibration; for worm gears: Thermal Breakdown, General Degradation,
12202130501047 IMPLEMENTATION bh
CVM University 29 GCET
and Bearing Instability. For each fault class, the sensor features are drawn from gear-typespecific
probability distributions calibrated against manufacturer operating specifications.
For helical gears in the No Fault class, for example, Vibration RMS is drawn from a lognormal
distribution with μ = 0.7, σ = 0.3 (corresponding to approximately 2.0 mm/s mean),
while Major Fault vibration is drawn from μ = 1.9, σ = 0.2 (approximately 6.7 mm/s mean).
Realistic cross-feature correlations are introduced using a Cholesky-decomposed
multivariate Gaussian to reflect the physical coupling between load, torque, and vibration
in gear systems. The helical gear dataset contains 50,000 samples generated using physicsinformed
correlations (Archard wear equation, friction-heat model, exponential lubrication
decay). The spur, bevel, and worm gear datasets each contain 5,000 to 10,000 samples,
totalling approximately 75,000 sensor records across all four gear types. An 80:20 stratified
train-test split is applied per gear type, and SMOTE (Synthetic Minority Over-sampling
Technique) is applied to the training split to balance the three fault classes before model
fitting.
SMOTE (Synthetic Minority Over-sampling Technique) was applied to the training split
to address class imbalance the No Fault class naturally dominates at approximately 60% of
samples, reflecting real-world healthy operating time fractions. SMOTE balanced the
training set to equal class proportions before model fitting, preventing bias toward the
majority class.
6.2.2 Preprocessing and Feature Engineering
Feature preprocessing applies a StandardScaler (zero mean, unit variance normalization)
fitted on the training set and saved as scaler.pkl for application to inference-time inputs. No
additional feature engineering was required as the eight sensor features directly represent
physically meaningful quantities. However, polynomial feature interaction terms (degree
2) were generated for the Logistic Regression model to capture non-linear class boundaries,
consistent with the approach used in the Worm Gear Logistic Regression module developed
in an earlier phase of the project.
12202130501047 IMPLEMENTATION bh
CVM University 30 GCET
6.2.3 Model Training and Evaluation
Five classifier models were trained using scikit-learn (v1.4) and XGBoost (v2.0).
Training parameters for the best-performing Gradient Boosting Machine included:
n_estimators=300, max_depth=5, learning_rate=0.05, subsample=0.8,
min_samples_leaf=4, and random_state=42.
An 80:20 stratified train-test split was used, with 5-fold cross-validation on the training set
to estimate generalization performance. All models were evaluated on the same held-out
test set for fair comparison.
Table 6.1 ML Model Performance Comparison — All 5 Models
Model Accuracy
(%)
F1 Score ROC-AUC CV Mean Inference Time
Gradient Boosting
(Best)
99.87 0.9987 1.0000 0.9976 8 ms
XGBoost 99.79 0.9979 1.0000 0.9971 5 ms
Random Forest 98.40 0.9842 0.9996 0.9910 12 ms
SVM (RBF Kernel) 95.08 0.9520 0.9943 0.9390 45 ms
Logistic Regression 95.10 0.9522 0.9942 0.9389 2 ms
The high accuracy values across all models reflect the quality of the physics-informed
synthetic data generation approach the feature distributions are well-separated between
fault classes, making the classification task tractable for all five algorithms. The GBM
model was selected as the production model (best_classifier.pkl) based on its combination
of highest accuracy, highest cross-validation mean, and acceptable inference time.
MLflow experiment tracking recorded all training runs, hyperparameter configurations,
metric values, and model artifacts. The MLflow model registry maintains the production
GBM as version 1.0 (status: Production), with all other models registered as Staging
versions available for comparison in the Model Comparison dashboard module. The
12202130501047 IMPLEMENTATION bh
CVM University 31 GCET
MLflow UI at localhost:5000 provides a complete audit trail of all training experiments
conducted during the 16-week development period.
6.3 BACKEND API IMPLEMENTATION
The FastAPI backend (gear_api.py) is structured as a single application module with ten
route handlers, supplemented by a dedicated LLM Copilot module (llm_copilot.py) and a
SHAP computation module (shap_handler.py). Pydantic v2 models enforce strict input
validation on all POST endpoints, with automatic OpenAPI (Swagger) documentation
generated at /docs.
The /api/predict endpoint is the most computationally intensive: it receives the eight sensor
features, retrieves the active model from the in-memory model registry, runs inference to
obtain class probabilities, computes SHAP values via the cached TreeExplainer (or
KernelExplainer), runs the Isolation Forest anomaly check, computes the RUL estimate
using the parameterized degradation model, and assembles the complete response JSON.
Profiling during testing showed a consistent end-to-end latency of 180–260ms for GBM
predictions with SHAP computation well within the 300ms target.
The /api/chat endpoint builds a SHAP-enriched context string from the current gear state
and prediction results, then sends it to the Groq API with a system prompt that configures
the LLaMA 3.3 70B model as an expert gear maintenance advisor. The LLM response is
streamed back to the frontend via Server-Sent Events (SSE), providing real-time typing
animation in the AI Copilot chat widget. The /api/report endpoint uses a similar approach
but with a structured prompt requesting a seven-section maintenance report in JSON format
for reliable parsing by the frontend.
6.4 DASHBOARD MODULES AND SCREENSHOTS
The React 19 frontend implements eight functional modules accessible via a persistent
navigation sidebar. The application uses React Context and the Zustand state management
12202130501047 IMPLEMENTATION bh
CVM University 32 GCET
library for global state (current gear type, sensor readings, prediction results, and user role),
with individual module components using useEffect hooks to react to state changes and
trigger API calls. A notable frontend feature is the 3D interactive gear animation
component, built using Three.js (v0.183) with React Three Fiber (@react-three/fiber v9.6)
and Drei helpers (@react-three/drei v10.7). The 3D scene renders four gear types —
SpurGearPair, HelicalGearPair, BevelGearPair, and WormGearAssembly — as animated
Three.js meshes within a factory environment comprising FactoryFloor, FactoryWalls,
StructuralColumns, GearPlatform, SceneLighting, and AtmosphericParticles components.
The animation speed reflects live sensor RPM and health state. Framer Motion (v12.38)
provides page transition and widget animation. Recharts (v3.8) handles all 2D data
visualization including bar charts, area charts, radial bar gauges, and line charts. jsPDF
(v2.5) with jspdf-autotable (v3.8) provides client-side PDF generation. Axios (v1.14)
handles HTTP communication with the backend API. The project uses Vite (v8.0) as the
build tool and dev server, and Vitest (v4.1) with React Testing Library for unit and
integration testing.
6.4.1 Login Page
The login page implements form-based authentication with client-side role assignment. Six
pre-configured user accounts correspond to the six RBAC roles. Upon successful login, the
user role is stored in React Context and persisted to sessionStorage for page-refresh
resilience. The login page features the GearMind AI logo, a gear animation background,
and a clean industrial dark-theme aesthetic.
12202130501047 IMPLEMENTATION bh
CVM University 33 GCET
Fig 6.2 Screenshot: Login Page
6.4.2 Main Dashboard
The Gear Health module is the primary analytical screen of GearMind AI. It displays a
RadialBar health gauge (0–100) as the central health indicator, color-coded from green
(>80) through amber (40–80) to red (<40). Below the gauge, fault probability bars show
12202130501047 IMPLEMENTATION bh
CVM University 34 GCET
the probability for each of the three fault classes (No Fault, Minor Fault, Major Fault) with
color coding and percentage values. Sensor status indicator cards display the current value
of each of the eight input features against their safe operating ranges, with red highlighting
for out-of-range values.
The module includes six sub-tabs for deeper analysis: (1) Overview with health summary
and recommended actions; (2) Feature Analysis with SHAP waterfall chart; (3) Fault
Details with the full probability breakdown; (4) RUL Tracker with lifecycle timeline; (5)
Maintenance Schedule with recommended intervention timeline; and (6) Cost Impact with
a per-unit financial comparison. The recommended actions are tiered as: Immediate (red)
for Major Fault, Within 48 hours (amber) for Minor Fault, and Routine Monitoring (green)
for No Fault.
Fig 6.3 Screenshot: Main Dashboard
6.4.3 Vibration and PHM Analysis Page
The Vibration and PHM Analysis module renders gear mesh vibration signals in the time
domain and their FFT spectral decomposition in the frequency domain. The gear mesh
frequency (GMF) is computed as: GMF = N × RPM / 60, where N is the number of teeth.
Sideband energy at GMF ± n×RPM/60 harmonics is tracked as an indicator of load
distribution irregularities and tooth damage. The module also displays a 12-month failure
12202130501047 IMPLEMENTATION bh
CVM University 35 GCET
probability timeline and the Weibull Reliability Function R(t) = exp(-(t/η)^β) with β = 2.5
and η = 5,000 hours.
Fig 6.4 Vibration & PHM Analysis Page
6.4.4 SHAP + LIME Explainability View
The XAI module presents SHAP and LIME explanations side by side in a split-panel
layout. The SHAP panel displays a waterfall chart showing the contribution of each feature
to the departure of the prediction from the base value (expected model output over the
training set). Positive SHAP values push the prediction toward fault; negative values push
toward healthy. The LIME panel displays a horizontal bar chart of the signed linear
12202130501047 IMPLEMENTATION bh
CVM University 36 GCET
approximation coefficients for the local neighborhood of the current input point. Below
both charts, a natural language root cause analysis paragraph is generated by combining the
top three SHAP features into a human-readable maintenance interpretation.
Fig 6.5 Screenshot: SHAP + LIME Explainability View
12202130501047 IMPLEMENTATION bh
CVM University 37 GCET
6.4.5 What-If Optimizer Modules
The What-If Optimizer uses Scipy's Differential Evolution algorithm to find the set of free
(unlocked) parameter values that minimizes the predicted fault probability subject to the
constraint that each parameter remains within its safe operating range. The user can lock
any subset of the eight parameters (representing parameters that cannot be adjusted in
practice, such as load imposed by the driven machine), and the optimizer searches the
remaining free dimensions. The optimization completes in under 2 seconds for typical
configurations (4–6 free parameters) and displays the optimal parameter set overlaid on the
current sensor readings.
Fig 6.6 Screenshot: What-If Optimizer Module
6.4.6 Manufacturing QC Module
The Manufacturing QC module implements AGMA-grade dimensional tolerance
verification for eight parameters per gear type: module, pitch circle diameter, tooth
thickness, tip circle diameter, root circle diameter, face width, helix angle (for helical
gears), and surface roughness. The user enters measured values from QC inspection, and
the system computes the tolerance deviation, checks against AGMA 10–12 grade limits
(configurable per gear type), and returns a Pass/Fail status for each parameter. An overall
QC Score (0–100) is computed as the weighted average of parameter pass rates. A
dimensional accuracy radar chart visualizes the relative deviation from nominal for all eight
parameters simultaneously.
12202130501047 IMPLEMENTATION bh
CVM University 38 GCET
Fig 6.7 Screenshot: Manufacturing QC Module
6.4.7 Reliability and Fatigue Data Page
The Reliability and Fatigue Data module provides four reliability engineering
visualizations: (1) MTBF bar chart comparing expected intervals between failures across
gear types and operating conditions; (2) S-N (Stress-Number of Cycles) fatigue curve
plotting cycles to failure as a function of contact stress amplitude in MPa, following the
Wöhler curve approach; (3) Weibull Reliability Function R(t) showing the probability of
surviving to time t; and (4) the Bathtub Failure Curve showing the three regions of the gear
lifecycle infant mortality (early failures from manufacturing defects), constant failure rate
12202130501047 IMPLEMENTATION bh
CVM University 39 GCET
(normal operating life), and wear-out (end-of-life degradation). All curves are
parameterized per gear type and can be adjusted interactively.
Fig 6.8 Screenshot: Reliability and Fatigue Data Page
6.4.8 Staff Directory and Shift Schedule
The Staff and Shift Management module provides an admin-accessible view of the
maintenance department's human resources. The staff directory displays eight personnel
12202130501047 IMPLEMENTATION bh
CVM University 40 GCET
records with fields for name, role, department, shift preference, and contact extension. The
shift schedule is visualized as a Gantt chart view covering the current and next two weeks,
with color coding for Morning (06:00–14:00), Afternoon (14:00–22:00), and Night (22:00–
06:00) shifts. The calendar view offers a monthly overview of shift assignments with
conflict detection for under-staffed periods.
Fig 6.9 Screenshot: Staff Directory and Shift Schedule
12202130501047 IMPLEMENTATION bh
CVM University 41 GCET
6.4.9 AI Report Generator
The AI Report Generator uses the Groq API (LLaMA 3.3 70B) to produce a structured
seven-section maintenance report tailored to the current gear state and prediction results.
The seven sections are: (1) Executive Summary a brief management-level synopsis of gear
health; (2) Fault Assessment detailed analysis of the identified fault type and severity; (3)
Recommended Actions prioritized maintenance interventions with timelines; (4) Cost
Analysis quantified financial impact of the predicted fault; (5) Failure Mode Analysis
FMEA-style root cause and effect chain; (6) Historical Trends interpretation of the gear's
health trajectory over logged sessions; and (7) Post-Maintenance Protocol checklist of
actions to be taken after maintenance is performed. The generated report is displayed in the
dashboard and can be exported as a PDF using jsPDF.
12202130501047 IMPLEMENTATION bh
CVM University 42 GCET
Fig 6.10 Screenshot: AI Report Generator Output
6.4.10 AI Copilot Chat Widget
The AI Copilot is implemented as a floating drawer widget accessible from any module via
a persistent 'Ask AI' button. When opened, the copilot loads the current gear state (gear
type, sensor readings, prediction results, and top SHAP features) into a structured context
block and appends it to every user query sent to the LLaMA 3.3 70B model. This context
injection ensures that the copilot's responses are grounded in the specific gear condition
being monitored, rather than generic maintenance advice. The conversation history is
maintained client-side for the duration of the session and displayed in a chat bubble
interface with timestamp and role indicators.
12202130501047 IMPLEMENTATION bh
CVM University 43 GCET
Fig 6.11 Screenshot: AI Copilot Chat Widget
6.4.11 Cost Impact Analysis Module
The Cost Impact module provides a financial breakdown comparing the per-unit
maintenance costs across three scenarios: Preventive Repair (early intervention based on
12202130501047 IMPLEMENTATION bh
CVM University 44 GCET
GearMind AI alert), Delayed Overhaul (intervention after further degradation), and Failure
(complete gear seizure requiring emergency replacement plus downtime costs). Costs are
parameterized per gear type based on Elecon's internal maintenance cost data. Bar charts
display the three cost scenarios for all four gear types simultaneously, with the maximum
savings (Preventive vs Failure scenario) highlighted as the headline metric.
Table 6.2 Cost Impact Model — Per Gear Unit (INR)
Scenario Helical Gear Spur Gear Bevel Gear Max Savings
(Helical)
Preventive Repair Rs. 45,000 Rs. 38,000 Rs. 52,000 —
Delayed Overhaul Rs. 1,20,000 Rs. 95,000 Rs. 1,40,000 —
Catastrophic Failure Rs. 4,50,000 Rs. 3,80,000 Rs. 5,20,000 —
Savings (Prev. vs
Fail.) Rs. 4,05,000 Rs. 3,42,000 Rs. 4,68,000 Rs. 4.68 Lakh
Fig 6.12 Screenshot: Cost Impact Analysis Module
6.4.12 Module Comparison Page
The Model Comparison module presents a side-by-side performance evaluation of all five
trained ML models. A summary table shows Accuracy, F1 Score, AUC-ROC, and CV
Mean for each model. Four bar charts visualize the comparative metrics. The bestperforming
model (GBM at 99.87% accuracy) is automatically highlighted with a gold
12202130501047 IMPLEMENTATION bh
CVM University 45 GCET
border and a 'Best Model' badge. Users with the ML Engineer role can select any model as
the active model for subsequent predictions allowing comparison of SHAP explanations
across different model families.
Fig 6.13 Screenshot: Model Comparison Page
6.4.13 History Module
The History module displays a complete log of all past prediction sessions stored in SQLite,
including gear unit ID, fault class, health score, RUL estimate, and timestamp. It supports
12202130501047 IMPLEMENTATION bh
CVM University 46 GCET
filtering by gear unit and verdict type, and visualizes health trends over time to help
engineers identify recurring fault patterns.
Fig 6.14 History Module
6.5 RESULTS AND OUTCOMES
The GearMind AI system achieved all primary technical objectives defined at the
commencement of the internship. The following results were recorded during validation
testing in the final two weeks of the internship period.
The results of multi-model evaluation across all four gear types are summarised below. For
helical gear, Gradient Boosting Machine achieved the highest accuracy at 99.87% (F1:
0.9987, AUC: 1.000, CV mean: 0.9976), followed by XGBoost at 99.79% (AUC: 1.000).
For spur gear, SVM with RBF kernel achieved the best accuracy at 82.27% (AUC: 0.887)
a more challenging classification task due to fewer discriminating features in the 6-feature
spur dataset; Random Forest was the second-best at 89.62%. For bevel gear, SVM with
RBF kernel led at 99.40% (F1: 0.9940, AUC: 0.9999, CV mean: 0.9934), closely followed
by Gradient Boosting at 98.66%. For worm gear, Gradient Boosting achieved perfect 100%
accuracy (F1: 1.000, AUC: 1.000) on the 13-feature worm dataset, with Random Forest at
12202130501047 IMPLEMENTATION bh
CVM University 47 GCET
99.98%. Each gear type therefore uses its own best-performing model: GBM for helical
and worm, SVM (RBF) for spur and bevel. An Isolation Forest anomaly detector is also
trained on the helical gear data to flag out-of-distribution sensor readings. The SHAP
computation completed in 55–80ms using the pre-computed background dataset,
contributing to a total prediction + SHAP response time of 180–260ms — within the 300ms
SLA.
The Manufacturing QC module achieved a 96% overall parameter pass rate across all
tolerance checks performed during validation testing. The RUL estimation tracked per gear
unit: for HG-01(Helical Gear unit 1) with a health score of 87, the estimated RUL was
85,564 cycles (approximately 142 8-hour operating shifts). The AI Copilot responded to
all 50 test queries with contextually relevant, gear-domain-specific answers within an
average of 1.8 seconds.
The cost savings quantification demonstrated Rs. 4.05–4.68 Lakh per gear unit by adopting
preventive maintenance based on GearMind AI alerts versus allowing failure to occur. Over
a fleet of 100 gear units, this represents a potential annual saving of Rs. 4.05–4.68 Crore a
compelling business case for deploying GearMind AI at scale across Elecon's gear
monitoring infrastructure.
12202130501047 TESTING bh
CVM University 48 GCET
7. TESTING
7.1 TESTING PLAN
A comprehensive four-level testing strategy was adopted for GearMind AI, covering all
system components from individual ML model performance to end-to-end user workflow
validation. The testing was conducted during Week 15 of the internship, following
completion of all development tasks, with systematic documentation of test cases, expected
outputs, actual outputs, and pass/fail status.
The four testing levels were: (1) ML Model Validation statistical evaluation of all five
trained models on the held-out test set; (2) Backend API Testing functional and
performance testing of all sixteen FastAPI endpoints using Postman (interactive Swagger
UI at /docs used for initial endpoint verification); (3) Frontend UI Testing automated unit
and integration testing using Vitest v4.1 with React Testing Library, covering GearScene,
HelicalGearPair, SpurGearPair, gear geometry utilities, SHAP widget, and state store;
cross-browser functional testing in Chrome, Firefox, and Edge for all eight dashboard
modules; and (4) Integration Testing end-to-end testing of the complete prediction →
SHAP → LLM → report pipeline. Regression testing was performed on modules that
underwent bug fixes identified during testing.
7.2 TEST RESULTS AND ANALYSIS
7.2.1 Test Cases— Fault Prediction Module
Table 7.1 Test Cases — Fault Prediction Module
TC ID Test Condition Expected
Output
Actual Output Remark
TC-01 All sensors within
nominal healthy range
No Fault, Health
> 80
No Fault, Health: 87,
RUL: 85,564 cycles
PASS
TC-02 Vibration RMS = 8
mm/s (limit: 6 mm/s)
Major Fault,
Health < 40
Major Fault, Health:
34, Vibration SHAP
+0.42
PASS
12202130501047 TESTING bh
CVM University 49 GCET
TC-03 Wear = 1.5 mm (near
limit 1.6 mm)
Minor Fault, low
RUL
Minor Fault, Health:
58, RUL: 12,450
cycles
PASS
TC-04 Lubrication Index =
0.05 (critical low)
Major Fault,
Lube SHAP
dominant
Major Fault, Health:
22, Lube SHAP
+0.51
PASS
TC-05 All inputs at maximum
safe operating values
No Fault, Health
near 100
No Fault, Health: 96 PASS
TC-06 Invalid input: Load = -
50 kN (out of range)
422 Validation
Error
HTTP 422
Unprocessable Entity
PASS
TC-07 Bevel gear — high
torque + high wear
combo
Major Fault,
Wear + Torque
SHAP dominant
Major Fault, SHAP
confirms Wear +
Torque
PASS
TC-08 Optimizer: 4 free
params, Load locked at
300 kN
Safe parameter
set, Fault Prob <
0.1
Optimal point found
in 1.8s, Fault Prob:
0.04
PASS
TC-09 Anomaly: Temperature
= 130°C (out of
distribution)
Isolation Forest
flag = 1
Anomaly flag raised,
warning displayed
PASS
TC-10 Model switch from
GBM to XGBoost midsession
XGBoost
prediction
matches GBM
within 0.5%
Accuracy difference:
0.08%, both No Fault
PASS
7.2.2 Test Case — API Endpoints
Table 7.2 Test Cases — API Endpoints (Backend)
TC ID Endpoint Test Type Expected
Response
Actual Response Remark
TA-01 POST
/api/predict
(valid)
Functional 200 OK +
prediction JSON <
300ms
200 OK, 243ms
avg.
PASS
TA-02 GET /api/models Functional 200 OK + 5 model
metrics
200 OK + correct
metrics
PASS
TA-03 POST /api/chat
(query)
Functional 200 OK + LLM
response
200 OK,
contextual answer,
1.8s avg.
PASS
TA-04 POST /api/report Functional 200 OK + 7-
section JSON
200 OK, all 7
sections present
PASS
TA-05 GET /api/history
(empty DB)
Boundary 200 OK + empty
array
200 OK, [] PASS
TA-06 DELETE
/api/history/LOG-
001
Functional 200 OK + deleted 200 OK, record
removed
PASS
12202130501047 TESTING bh
CVM University 50 GCET
TA-07 POST
/api/predict
(invalid role)
Security 403 Forbidden HTTP 403
returned
PASS
TA-08 POST
/api/optimize (5
free params)
Performance 200 OK + optimal
params < 2s
200 OK, 1.74s PASS
TA-09 GET /api/lime Functional 200 OK + LIME
explanation JSON
200 OK, 430ms (<
500ms SLA)
PASS
TA-10 POST
/api/predict (100
concurrent)
Load All 200 OK, < 1s
avg.
200 OK, 0.87s
avg. (Uvicorn
workers)
PASS
7.2.3 Test Cases — Frontend UI Modules
Table 7.3 Test Cases — Frontend UI Modules
TC
ID
Module Test Action Expected Behavior Result
TU-
01
Login Enter valid
credentials for
all 6 roles
Role-specific dashboard
loads with correct
permissions
PASS
TU-
02
Gear Health Adjust Vibration
slider to 8 mm/s
Health gauge drops to
red, Major Fault shown,
SHAP updates
PASS
TU-
03
Gear Health Switch gear type
from Helical to
Spur
Input ranges update,
new prediction triggered
PASS
TU-
04
Vibration
PHM
Change RPM to
1500
GMF recalculated, FFT
chart updates
PASS
TU-
05
XAI Trigger LIME
tab refresh
LIME bar chart renders
with correct signed
contributions
PASS
TU-
06
QC Module Enter out-oftolerance
surface
roughness
Parameter marked FAIL
in red, QC score
decreases
PASS
TU-
07
History Filter by gear
type = Bevel
Only bevel gear records
displayed
PASS
TU-
08
AI Copilot Ask 'What
caused this
fault?'
LLM responds with
SHAP-grounded root
cause
PASS
TU-
09
Report Gen. Click Generate
Report, then
Export PDF
7-section report
rendered, PDF
downloaded
PASS
TU-
10
Cross-browser Load app in
Chrome, Firefox,
Edge
Full functionality, no
layout issues
PASS
12202130501047 TESTING bh
CVM University 51 GCET
All 30 test cases across the three test suites passed without failures. One issue was identified
during testing that had not been caught during development: the LIME explanation tab took
520ms on first load due to cold computation of the LIME background sampler. This was
resolved by pre-computing the sampler at server startup and caching it in process memory,
reducing subsequent LIME response times to 380–450ms within the 500ms SLA. The fix
was validated with a regression test (TC-09 variant) confirming sub-500ms response for
LIME.
12202130501047 CONCLUSION
AND DISCUSSIONS bh
CVM University 52 GCET
8. CONCLUSION AND DISCUSSIONS
8.1 OVERALL ANALYSIS OF INTERNSHIP VIABILITY
The GearMind AI internship project was completed successfully within the 16-week
timeline at Tech Elecon Pvt. Ltd. All primary technical objectives were met or exceeded.
The final system, GearMind AI v5.0, supports four gear types Helical, Spur, Bevel, and
Worm each with a dedicated ML model, RUL regressor, SHAP explainer, and operating
unit presets. The helical gear GBM model achieved 99.87% fault prediction accuracy; the
worm gear GBM achieved 100%; the bevel gear SVM achieved 99.4%; and the spur gear
SVM achieved 82.3% on a more challenging 6-feature classification task. The system
exposes sixteen FastAPI endpoints, delivers SHAP and LIME explainability for every
prediction, provides an eight-module React 19 dashboard with a Three.js 3D gear
animation, and demonstrated compelling cost-benefit metrics showing savings of Rs. 4.05–
4.68 Lakh per gear unit.
The internship provided immensely valuable hands-on experience across four technical
domains: industrial machine learning (data generation, model selection, evaluation, and
deployment), explainable AI (SHAP TreeExplainer, LIME tabular, model-agnostic
interpretation), full-stack web development (React 19 with hooks, FastAPI with async
endpoints, SQLite CRUD), and industrial domain knowledge (gear manufacturing
processes, AGMA standards, vibration analysis, reliability engineering). The combination
of technical depth and domain exposure represents a rare and valuable learning opportunity
that directly prepares the student for a career in industrial AI or data engineering.
The industry mentor assessed the project as technically sound and industrially relevant,
noting in the feedback that the SHAP explainability integration and the cost-benefit
analysis module were particularly impressive in demonstrating the business value of AIdriven
maintenance.
12202130501047 CONCLUSION
AND DISCUSSIONS bh
CVM University 53 GCET
8.2 PROBLEMS ENCOUNTERED AND SOLUTIONS
Table 8.1 Problems Encountered and Solutions
Problem
Encountered
Root Cause Solution Adopted
No real IoT sensor
data available
Elecon's IoT
infrastructure not yet
deployed for
internship access
Developed physics-informed synthetic data generator
with gear-type-specific distributions and fault
injection; validated parameter ranges against
manufacturer specs
SHAP computation
caused > 2s API
latency on first load
SHAP
KernelExplainer
requires background
dataset sampling per
call
Pre-computed SHAP background dataset at startup;
switched to TreeExplainer for GBM/XGBoost; cached
explanation objects in process memory
Class imbalance (No
Fault class dominant)
Healthy operation
accounts for 60%+ of
real-world gear
operating time
Applied SMOTE oversampling to minority classes in
training split; used class-weighted loss in GBM and
XGBoost
RBAC without a
backend
authentication server
JWT/OAuth2
backend not in project
scope
Client-side React Context role management; designed
for JWT migration in v5.0; protected API endpoints
with role check middleware
Recharts performance
lag on large history
dataset
React re-render
triggered for every
scroll event in history
table
Implemented pagination (50 records/page), virtual
scrolling via react-window, and rolling window chart
(last 30 sessions)
LIME response time
exceeded 500ms on
first load
LIME background
sampler computed
on-demand
Pre-computed sampler at server startup; cached in
process memory; reduced to 380–450ms
React router 404 on
page refresh in Vite
dev server
Vite dev server routes
to index.html only for
root
Added historyApiFallback: true to Vite config;
production deploy uses nginx try_files directive
8.3 SUMMARY AND LIMITATIONS
During the 16-week internship at Tech Elecon Pvt. Ltd., the following was successfully
completed: (a) a complete five-model machine learning pipeline with GBM achieving
99.87% accuracy on synthetic data; (b) SHAP (global and per-prediction) and LIME (local)
explainability integration; (c) a sixteen-endpoint FastAPI backend (gear_api.py v5.0) with
sub-300ms prediction response time; (d) a fully functional eight-module React 19
dashboard with Recharts visualizations, Three.js 3D gear animation, and Vitest test
12202130501047 CONCLUSION
AND DISCUSSIONS bh
CVM University 54 GCET
coverage; (e) Differential Evolution parameter optimizer; (f) AI-powered maintenance
report generation and PDF export via LLaMA 3.3 70B; (g) Manufacturing QC module with
AGMA compliance checking; (h) Role-Based Access Control with six user roles; and (i)
comprehensive testing documentation with 30 test cases across three test suites.
8.3.1 Limitations
The following limitations of the current v4.0 implementation are acknowledged. First, the
system operates exclusively on physics-informed synthetic data; accuracy on real live
sensor streams from production floor gear units has not been validated and may differ from
the 99.87% reported here due to real-world noise, measurement artifacts, and sensor drift.
Second, the RBAC implementation is client-side only a production deployment requires a
JWT/OAuth2 authentication server with secure token management. Third, the system
currently supports monitoring of up to 25 gear units simultaneously; scaling to 100+ units
would require migration from SQLite to PostgreSQL and deployment on a multi-worker
server. Fourth, LLM (Groq API) functionality is internet-dependent, with no offline
fallback available in v4.0. Fifth, the cost model uses estimated maintenance cost figures
that should be validated against actual Elecon financial data in a production deployment.
8.4 FUTURE ENHANCEMENTS
The following enhancements are planned for subsequent development phases, to be
undertaken after the internship by the Tech Elecon data science team or in a follow-on
project:
1. Live IoT Integration: Connect to real vibration, temperature, and lubrication sensors
on production floor gear units via MQTT or OPC-UA protocols, replacing the
simulated slider inputs with real-time data streams.
2. Digital Twin: Build a 3D gear simulation model (e.g., using FEniCS for FEA) that
mirrors the real-time sensor state, enabling virtual testing of operating scenarios
without physical risk.
3. Deep Learning for RUL: Replace the parameterized RUL model with an LSTM or
Transformer architecture trained on sequential sensor data for long-horizon, datadriven
remaining useful life prediction.
12202130501047 CONCLUSION
AND DISCUSSIONS bh
CVM University 55 GCET
4. Mobile Application: Develop a React Native or Flutter mobile application for onfloor
maintenance technicians, providing push notifications for fault alerts and onetap
access to gear health status.
5. ERP/SAP Integration: Automatically generate work orders in Elecon's SAP PM
(Plant Maintenance) module when GearMind AI raises a fault alert above a
configurable severity threshold.
6. Edge Deployment: Deploy a lightweight ML inference engine (using ONNX
Runtime) on industrial edge devices such as NVIDIA Jetson Orin or Raspberry Pi
5 for low-latency, offline-capable fault detection.
7. Multi-Plant Dashboard: Extend the system to monitor gear units across multiple
Elecon plant locations (Vitthal Udyognagar, Vallabh Vidyanagar, international
sites) from a centralized web dashboard.
Table 8.2 Future Enhancement Roadmap
Enhancement Technology Priority Estimated Effort
Live IoT Integration MQTT, OPC-UA,
AWS IoT Core
Critical 3–4 months
Digital Twin FEniCS, Unity /
Unreal Engine
High 6–8 months
LSTM/Transformer
RUL
PyTorch, Hugging
Face
High 2–3 months
Mobile App React Native /
Flutter
Medium 2–3 months
SAP Integration SAP BAPI/RFC High 2–3 months
Edge Deployment
(ONNX)
ONNX Runtime,
Jetson Orin
Medium 1–2 months
Multi-Plant
Dashboard
React, PostgreSQL,
AWS
Medium 3–4 months
12202130501047 REFERENCES bh
CVM University 56 GCET
9. REFERENCES
1. American Gear Manufacturers Association (1997) AGMA 2003-B97: Rating the Pitting
Resistance and Bending Strength of Generated Straight Bevel, Zerol Bevel, and Spiral
Bevel Gear Teeth. AGMA, Alexandria, VA.
2. Breiman, L. (2001) 'Random Forests', Machine Learning, Vol. 45, No. 1, pp. 5–32.
3. Chen, T. and Guestrin, C. (2016) 'XGBoost: A Scalable Tree Boosting System',
Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge
Discovery and Data Mining, San Francisco, CA, pp. 785–794.
4. FastAPI Documentation (2024) 'FastAPI — Modern, Fast Web Framework for Building
APIs with Python'. Available at: https://fastapi.tiangolo.com (Accessed: April 2026).
5. Friedman, J.H. (2001) 'Greedy Function Approximation: A Gradient Boosting Machine',
Annals of Statistics, Vol. 29, No. 5, pp. 1189–1232.
6. Groq API Documentation (2025) 'Groq API — Ultra-Fast Inference for LLaMA 3
Models'. Available at: https://console.groq.com/docs (Accessed: April 2026).
7. ISO 10816-3 (2009) Mechanical Vibration — Evaluation of Machine Vibration by
Measurements on Non-Rotating Parts. ISO, Geneva, Switzerland.
8. Lei, Y., Li, N., Guo, L., Li, N., Yan, T. and Lin, J. (2018) 'Machinery health prognostics:
A systematic review from data acquisition to RUL prediction', Mechanical Systems and
Signal Processing, Vol. 104, pp. 799–834.
9. Liu, F.T., Ting, K.M. and Zhou, Z.H. (2008) 'Isolation Forest', Proceedings of the IEEE
International Conference on Data Mining (ICDM), Pisa, Italy, pp. 413–422.
10. Lundberg, S.M. and Lee, S.I. (2017) 'A Unified Approach to Interpreting Model
Predictions', Advances in Neural Information Processing Systems (NeurIPS), Vol. 30, pp.
4765–4774.
11. MLflow Documentation (2025) 'MLflow: A Machine Learning Lifecycle Platform',
v4.0. Available at: https://mlflow.org/docs/latest/index.html (Accessed: April 2026).
12. React Documentation (2024) 'React — The Library for Web and Native User
Interfaces'. Available at: https://react.dev (Accessed: April 2026).
13. Recharts Library (2024) 'Recharts — A Composable Charting Library Built on React
Components'. Available at: https://recharts.org (Accessed: April 2026).
14. Ribeiro, M.T., Singh, S. and Guestrin, C. (2016) 'Why Should I Trust You? Explaining
the Predictions of Any Classifier', Proceedings of the 22nd ACM SIGKDD International
Conference on Knowledge Discovery and Data Mining, San Francisco, CA, pp. 1135–
1144.
12202130501047 REFERENCES bh
CVM University 57 GCET
15. Scipy Documentation (2024) 'scipy.optimize.differential_evolution — Differential
Evolution Optimizer'. Available at:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.differential_evolution
.html (Accessed: April 2026).
16. Vite Documentation (2024) 'Vite — Next Generation Frontend Tooling'. Available at:
https://vitejs.dev (Accessed: April 2026).




























