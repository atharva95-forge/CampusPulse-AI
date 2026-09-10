\# CampusPulse AI



\## AI-Powered Smart College Campus Information System



CampusPulse AI is a smart campus information platform designed to help students quickly find important information about their college campus.



The system combines a web-based dashboard, campus database, AI-assisted search, events, notices, locations and campus navigation into one platform.



\---



\## 🎯 Project Objective



Students often need to search through different sources to find information about:



\- College events

\- Notices

\- Classrooms and laboratories

\- Campus locations

\- Activities

\- Important campus information



CampusPulse AI brings this information together in a single, easy-to-use platform.



\---



\## 🚀 Main Features



\### 🤖 AI Campus Assistant

Students can ask questions about campus information using natural language.



Examples:



\- "What events are happening today?"

\- "Show me the latest notices."

\- "Where is the computer lab?"

\- "What activities are happening on campus?"



\### 📅 Events \& Activities



The system stores and displays:



\- Event name

\- Location

\- Date

\- Time

\- Department

\- Description



\### 📢 Smart Notice System



Students can view important college notices with:



\- Notice title

\- Content

\- Date

\- Department



Administrators can add and delete notices.



\### 📍 Campus Locations



The system provides information about important campus locations, including:



\- Building

\- Floor

\- Room

\- Description



\### 🗺️ Campus Map



CampusPulse AI includes a campus map interface designed to help students understand where important campus facilities are located.



\### 🛠️ Admin Panel



The administrator can manage campus information including:



\- Events

\- Notices

\- Locations



\### 🗄️ Database



Campus information is stored using an SQLite database.



\---



\## 🧠 Technology Stack



| Technology | Purpose |

|---|---|

| Python | Backend programming |

| Flask | Web application framework |

| SQLite | Database |

| HTML | Frontend structure |

| CSS | User interface styling |

| JavaScript | Frontend interaction |



\---



\## 🏗️ System Architecture



```text

&#x20;               Student

&#x20;                  │

&#x20;                  ▼

&#x20;         ┌─────────────────┐

&#x20;         │  CampusPulse UI │

&#x20;         └────────┬────────┘

&#x20;                  │

&#x20;                  ▼

&#x20;         ┌─────────────────┐

&#x20;         │   Flask Backend │

&#x20;         └────────┬────────┘

&#x20;                  │

&#x20;       ┌──────────┼──────────┐

&#x20;       ▼          ▼          ▼

&#x20;    AI Logic   REST APIs   Database

&#x20;                          │

&#x20;                          ▼

&#x20;                   SQLite Database

