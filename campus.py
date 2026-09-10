from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
import re
from datetime import datetime

app = Flask(__name__)

DATABASE = "campuspulsedatabase.db"


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT,
            date TEXT,
            time TEXT,
            department TEXT,
            description TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            date TEXT NOT NULL,
            department TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            building TEXT NOT NULL,
            floor TEXT,
            room TEXT,
            description TEXT
        )
    """)

    conn.commit()

    # --------------------------------------------------------
    # SAMPLE DATA ONLY IF TABLES ARE EMPTY
    # --------------------------------------------------------

    event_count = conn.execute(
        "SELECT COUNT(*) FROM events"
    ).fetchone()[0]

    if event_count == 0:

        conn.execute("""
            INSERT INTO events
            (name, location, date, time, department, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "Technical Seminar",
            "Seminar Hall",
            "2026-09-15",
            "11:00",
            "AI-DS",
            "Technical seminar for students."
        ))

        conn.execute("""
            INSERT INTO events
            (name, location, date, time, department, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "Coding Competition",
            "Computer Lab 1",
            "2026-09-18",
            "10:00",
            "Computer",
            "Coding competition for college students."
        ))

    notice_count = conn.execute(
        "SELECT COUNT(*) FROM notices"
    ).fetchone()[0]

    if notice_count == 0:

        conn.execute("""
            INSERT INTO notices
            (title, content, date, department)
            VALUES (?, ?, ?, ?)
        """, (
            "Internal Assessment Notice",
            "Students are requested to check the internal assessment schedule.",
            "2026-09-10",
            "AI-DS"
        ))

        conn.execute("""
            INSERT INTO notices
            (title, content, date, department)
            VALUES (?, ?, ?, ?)
        """, (
            "Workshop Announcement",
            "Registration is open for the upcoming technical workshop.",
            "2026-09-09",
            "General"
        ))

    location_count = conn.execute(
        "SELECT COUNT(*) FROM locations"
    ).fetchone()[0]

    if location_count == 0:

        sample_locations = [
            (
                "Computer Lab 1",
                "Main Building",
                "1st Floor",
                "Lab 1",
                "Computer laboratory."
            ),
            (
                "Computer Lab 2",
                "Main Building",
                "2nd Floor",
                "Lab 2",
                "Computer laboratory."
            ),
            (
                "Library",
                "Main Building",
                "Ground Floor",
                "Library",
                "College library."
            ),
            (
                "Seminar Hall",
                "Main Building",
                "Ground Floor",
                "Seminar Hall",
                "Seminar and presentation hall."
            ),
            (
                "Administrative Office",
                "Main Building",
                "Ground Floor",
                "Office",
                "Administrative section."
            )
        ]

        conn.executemany("""
            INSERT INTO locations
            (name, building, floor, room, description)
            VALUES (?, ?, ?, ?, ?)
        """, sample_locations)

    conn.commit()
    conn.close()


init_database()


# ============================================================
# HTML
# ============================================================

HTML = r"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>CampusPulse AI</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: #f1f5f9;
    color: #0f172a;
}

button,
input,
textarea,
select {
    font-family: inherit;
}

button {
    cursor: pointer;
    border: none;
}

.app {
    display: flex;
    min-height: 100vh;
}


/* =========================================================
   SIDEBAR
========================================================= */

.sidebar {

    width: 250px;

    background:
        linear-gradient(
            180deg,
            #0f172a,
            #172554
        );

    color: white;

    padding: 24px 16px;

    position: fixed;

    left: 0;
    top: 0;
    bottom: 0;

    overflow-y: auto;
}

.logo {

    font-size: 23px;
    font-weight: 700;

    padding: 8px 12px 25px;

}

.logo span {
    color: #60a5fa;
}

.menu-title {

    color: #94a3b8;
    font-size: 11px;
    text-transform: uppercase;

    margin:
        15px 12px 8px;

    letter-spacing: 1px;

}

.nav-btn {

    width: 100%;

    padding: 12px 14px;

    margin-bottom: 6px;

    background: transparent;

    color: #cbd5e1;

    text-align: left;

    border-radius: 9px;

    font-size: 14px;

}

.nav-btn:hover,
.nav-btn.active {

    background: #2563eb;
    color: white;

}


/* =========================================================
   MAIN
========================================================= */

.main {

    margin-left: 250px;

    width:
        calc(100% - 250px);

    min-height: 100vh;

}

.topbar {

    height: 70px;

    background: white;

    border-bottom:
        1px solid #e2e8f0;

    display: flex;

    align-items: center;

    justify-content: space-between;

    padding:
        0 30px;

}

.topbar-title {

    font-size: 20px;
    font-weight: 700;

}

.status {

    display: flex;
    align-items: center;
    gap: 8px;

    font-size: 13px;

    color: #16a34a;

}

.status-dot {

    width: 9px;
    height: 9px;

    background: #22c55e;

    border-radius: 50%;

}

.content {

    padding: 30px;

}

.page {
    display: none;
}

.page.active {
    display: block;
}


/* =========================================================
   CARDS
========================================================= */

.cards {

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(190px, 1fr)
        );

    gap: 18px;

    margin-bottom: 25px;

}

.card {

    background: white;

    border:
        1px solid #e2e8f0;

    border-radius: 14px;

    padding: 20px;

}

.card-icon {

    font-size: 25px;

    margin-bottom: 10px;

}

.card-title {

    color: #64748b;

    font-size: 13px;

}

.card-value {

    font-size: 28px;

    font-weight: 700;

    margin-top: 5px;

}


/* =========================================================
   SECTION
========================================================= */

.section {

    background: white;

    border:
        1px solid #e2e8f0;

    border-radius: 14px;

    padding: 22px;

    margin-bottom: 22px;

}

.section h2 {

    margin-top: 0;

    font-size: 19px;

}


/* =========================================================
   EVENT
========================================================= */

.event {

    border:
        1px solid #e2e8f0;

    border-radius: 10px;

    padding: 16px;

    margin-bottom: 12px;

}

.event h3 {

    margin:
        0 0 8px;

}

.event p {

    color: #475569;

    margin:
        6px 0;

}


/* =========================================================
   NOTICE
========================================================= */

.notice {

    border-left:
        4px solid #2563eb;

    background: #f8fafc;

    padding: 16px;

    margin-bottom: 12px;

    border-radius: 8px;

}

.notice h3 {

    margin:
        0 0 8px;

}

.notice p {

    color: #475569;

}


/* =========================================================
   LOCATION
========================================================= */

.location {

    border:
        1px solid #e2e8f0;

    padding: 16px;

    border-radius: 10px;

    margin-bottom: 12px;

}

.location h3 {

    margin:
        0 0 8px;

}


/* =========================================================
   BUTTONS
========================================================= */

.primary {

    background: #2563eb;

    color: white;

    padding:
        10px 16px;

    border-radius: 8px;

}

.primary:hover {

    background: #1d4ed8;

}

.danger {

    background: #dc2626;

    color: white;

    padding:
        9px 14px;

    border-radius: 8px;

    margin-top: 10px;

}

.danger:hover {

    background: #b91c1c;

}

.secondary {

    background: #e2e8f0;

    color: #0f172a;

    padding:
        9px 14px;

    border-radius: 8px;

}


/* =========================================================
   FORMS
========================================================= */

.form-grid {

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(220px, 1fr)
        );

    gap: 14px;

}

.form-group {

    display: flex;

    flex-direction: column;

    gap: 6px;

}

.form-group.full {

    grid-column:
        1 / -1;

}

.form-group label {

    font-size: 13px;

    font-weight: 600;

}

.form-group input,
.form-group textarea,
.form-group select {

    padding: 11px;

    border:
        1px solid #cbd5e1;

    border-radius: 8px;

    outline: none;

}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {

    border-color: #2563eb;

}


/* =========================================================
   AI
========================================================= */

.chat-box {

    min-height: 280px;

    max-height: 430px;

    overflow-y: auto;

    border:
        1px solid #e2e8f0;

    border-radius: 10px;

    padding: 15px;

    background: #f8fafc;

    margin-bottom: 15px;

}

.message {

    padding: 12px;

    border-radius: 10px;

    margin-bottom: 10px;

    max-width: 80%;

    white-space: pre-line;

}

.user-message {

    background: #dbeafe;

    margin-left: auto;

}

.ai-message {

    background: white;

    border:
        1px solid #e2e8f0;

}

.chat-row {

    display: flex;

    gap: 10px;

}

.chat-row input {

    flex: 1;

    padding: 12px;

    border:
        1px solid #cbd5e1;

    border-radius: 9px;

}


/* =========================================================
   MAP
========================================================= */

.map {

    min-height: 500px;

    border-radius: 14px;

    background:
        linear-gradient(
            135deg,
            #dbeafe,
            #dcfce7
        );

    border:
        1px solid #cbd5e1;

    position: relative;

    overflow: hidden;

}

.map-title {

    position: absolute;

    top: 20px;
    left: 20px;

    background: white;

    padding: 12px 16px;

    border-radius: 10px;

    box-shadow:
        0 4px 15px
        rgba(0,0,0,0.1);

    font-weight: 700;

}

.map-location {

    position: absolute;

    background: white;

    border:
        2px solid #2563eb;

    border-radius: 12px;

    padding: 12px;

    min-width: 145px;

    box-shadow:
        0 4px 15px
        rgba(0,0,0,0.12);

    text-align: center;

    cursor: pointer;

}

.map-location:hover {

    transform:
        translateY(-2px);

}

.map-location:nth-child(2) {
    top: 100px;
    left: 20%;
}

.map-location:nth-child(3) {
    top: 100px;
    right: 18%;
}

.map-location:nth-child(4) {
    top: 270px;
    left: 42%;
}

.map-location:nth-child(5) {
    bottom: 65px;
    left: 15%;
}

.map-location:nth-child(6) {
    bottom: 65px;
    right: 15%;
}


/* =========================================================
   EMPTY
========================================================= */

.empty {

    padding: 30px;

    text-align: center;

    color: #64748b;

}


/* =========================================================
   RESPONSIVE
========================================================= */

@media(max-width: 800px) {

    .sidebar {

        width: 210px;

    }

    .main {

        margin-left: 210px;

        width:
            calc(100% - 210px);

    }

    .content {

        padding: 18px;

    }

}

</style>

</head>


<body>

<div class="app">


<!-- ======================================================
     SIDEBAR
====================================================== -->

<aside class="sidebar">

    <div class="logo">
        Campus<span>Pulse</span> AI
    </div>

    <div class="menu-title">
        Main
    </div>

    <button
        class="nav-btn active"
        onclick="showPage('dashboard', this)"
    >
        🏠 Dashboard
    </button>

    <button
        class="nav-btn"
        onclick="showPage('assistant', this)"
    >
        🤖 AI Assistant
    </button>

    <button
        class="nav-btn"
        onclick="showPage('events', this)"
    >
        🎉 Events
    </button>

    <button
        class="nav-btn"
        onclick="showPage('notices', this)"
    >
        📢 Notices
    </button>

    <button
        class="nav-btn"
        onclick="showPage('locations', this)"
    >
        📍 Locations
    </button>

    <button
        class="nav-btn"
        onclick="showPage('map', this)"
    >
        🗺️ Campus Map
    </button>

    <div class="menu-title">
        Management
    </div>

    <button
        class="nav-btn"
        onclick="showPage('admin', this)"
    >
        ⚙️ Admin Panel
    </button>

</aside>


<!-- ======================================================
     MAIN
====================================================== -->

<main class="main">


<header class="topbar">

    <div
        class="topbar-title"
        id="pageTitle"
    >
        Dashboard
    </div>

    <div class="status">

        <span class="status-dot"></span>

        Campus System Online

    </div>

</header>


<div class="content">


<!-- ======================================================
     DASHBOARD
====================================================== -->

<section
    id="dashboard"
    class="page active"
>

    <div class="cards">

        <div class="card">

            <div class="card-icon">
                🎉
            </div>

            <div class="card-title">
                Today's Events
            </div>

            <div
                class="card-value"
                id="eventCount"
            >
                0
            </div>

        </div>


        <div class="card">

            <div class="card-icon">
                📢
            </div>

            <div class="card-title">
                Active Notices
            </div>

            <div
                class="card-value"
                id="noticeCount"
            >
                0
            </div>

        </div>


        <div class="card">

            <div class="card-icon">
                📍
            </div>

            <div class="card-title">
                Campus Locations
            </div>

            <div
                class="card-value"
                id="locationCount"
            >
                0
            </div>

        </div>


        <div class="card">

            <div class="card-icon">
                🤖
            </div>

            <div class="card-title">
                AI Queries
            </div>

            <div
                class="card-value"
                id="queryCount"
            >
                0
            </div>

        </div>

    </div>


    <div class="section">

        <h2>
            What's Happening Today?
        </h2>

        <div id="dashboardEvents">
            Loading...
        </div>

    </div>


    <div class="section">

        <h2>
            Latest Notices
        </h2>

        <div id="dashboardNotices">
            Loading...
        </div>

    </div>


</section>


<!-- ======================================================
     AI ASSISTANT
====================================================== -->

<section
    id="assistant"
    class="page"
>

    <div class="section">

        <h2>
            🤖 CampusPulse AI Assistant
        </h2>

        <p>
            Ask questions about campus events,
            notices, locations and facilities.
        </p>


        <div
            class="chat-box"
            id="chatBox"
        >

            <div class="message ai-message">

                Hello! 👋

                I am CampusPulse AI.

                Ask me about:
                events, notices, locations,
                classrooms, laboratories and
                campus facilities.

            </div>

        </div>


        <div class="chat-row">

            <input
                id="questionInput"
                placeholder="Ask CampusPulse something..."
                onkeydown="
                    if(event.key === 'Enter')
                    askAI();
                "
            >

            <button
                class="primary"
                onclick="askAI()"
            >
                Ask
            </button>

        </div>

    </div>

</section>


<!-- ======================================================
     EVENTS
====================================================== -->

<section
    id="events"
    class="page"
>

    <div class="section">

        <h2>
            🎉 Campus Events
        </h2>

        <div id="eventsContainer">
            Loading...
        </div>

    </div>

</section>


<!-- ======================================================
     NOTICES
====================================================== -->

<section
    id="notices"
    class="page"
>

    <div class="section">

        <h2>
            📢 Campus Notices
        </h2>

        <div id="noticesContainer">
            Loading...
        </div>

    </div>

</section>


<!-- ======================================================
     LOCATIONS
====================================================== -->

<section
    id="locations"
    class="page"
>

    <div class="section">

        <h2>
            📍 Campus Locations
        </h2>

        <div id="locationsContainer">
            Loading...
        </div>

    </div>

</section>


<!-- ======================================================
     MAP
====================================================== -->

<section
    id="map"
    class="page"
>

    <div class="section">

        <h2>
            🗺️ College Map
        </h2>

        <p>
            PESMCOE Campus
        </p>

        <div class="map">

            <div class="map-title">
                📍 CampusPulse College Map
            </div>


            <div
                class="map-location"
                onclick="mapInfo('Main Building')"
            >
                🏫
                <br>
                <b>Main Building</b>
                <br>
                <small>
                    Classrooms & Labs
                </small>
            </div>


            <div
                class="map-location"
                onclick="mapInfo('Library')"
            >
                📚
                <br>
                <b>Library</b>
                <br>
                <small>
                    Study Area
                </small>
            </div>


            <div
                class="map-location"
                onclick="mapInfo('Administration')"
            >
                🏢
                <br>
                <b>Administration</b>
                <br>
                <small>
                    Office
                </small>
            </div>


            <div
                class="map-location"
                onclick="mapInfo('Seminar Hall')"
            >
                🎤
                <br>
                <b>Seminar Hall</b>
                <br>
                <small>
                    Events
                </small>
            </div>


            <div
                class="map-location"
                onclick="mapInfo('Canteen')"
            >
                🍴
                <br>
                <b>Canteen</b>
                <br>
                <small>
                    Food Area
                </small>
            </div>


            <div
                class="map-location"
                onclick="mapInfo('Parking')"
            >
                🅿️
                <br>
                <b>Parking</b>
                <br>
                <small>
                    Vehicle Parking
                </small>
            </div>

        </div>

    </div>

</section>


<!-- ======================================================
     ADMIN PANEL
====================================================== -->

<section
    id="admin"
    class="page"
>

    <div class="section">

        <h2>
            ⚙️ Admin Panel
        </h2>

        <p>
            Manage CampusPulse campus information.
        </p>

    </div>


    <!-- EVENT ADMIN -->

    <div class="section">

        <h2>
            🎉 Add Event
        </h2>

        <form
            onsubmit="addEvent(event)"
        >

            <div class="form-grid">

                <div class="form-group">

                    <label>
                        Event Name
                    </label>

                    <input
                        id="eventName"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Location
                    </label>

                    <input
                        id="eventLocation"
                    >

                </div>


                <div class="form-group">

                    <label>
                        Date
                    </label>

                    <input
                        type="date"
                        id="eventDate"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Time
                    </label>

                    <input
                        type="time"
                        id="eventTime"
                    >

                </div>


                <div class="form-group">

                    <label>
                        Department
                    </label>

                    <input
                        id="eventDepartment"
                    >

                </div>


                <div
                    class="form-group full"
                >

                    <label>
                        Description
                    </label>

                    <textarea
                        id="eventDescription"
                        rows="3"
                    ></textarea>

                </div>

            </div>

            <br>

            <button
                class="primary"
                type="submit"
            >
                + Add Event
            </button>

        </form>

    </div>


    <!-- NOTICE ADMIN -->

    <div class="section">

        <h2>
            📢 Add Notice
        </h2>

        <form
            onsubmit="addNotice(event)"
        >

            <div class="form-grid">

                <div class="form-group">

                    <label>
                        Notice Title
                    </label>

                    <input
                        id="noticeTitle"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Date
                    </label>

                    <input
                        type="date"
                        id="noticeDate"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Department
                    </label>

                    <input
                        id="noticeDepartment"
                    >

                </div>


                <div
                    class="form-group full"
                >

                    <label>
                        Notice Content
                    </label>

                    <textarea
                        id="noticeContent"
                        rows="4"
                        required
                    ></textarea>

                </div>

            </div>

            <br>

            <button
                class="primary"
                type="submit"
            >
                + Add Notice
            </button>

        </form>

    </div>


    <!-- LOCATION ADMIN -->

    <div class="section">

        <h2>
            📍 Add Location
        </h2>

        <form
            onsubmit="addLocation(event)"
        >

            <div class="form-grid">

                <div class="form-group">

                    <label>
                        Location Name
                    </label>

                    <input
                        id="locationName"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Building
                    </label>

                    <input
                        id="locationBuilding"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Floor
                    </label>

                    <input
                        id="locationFloor"
                    >

                </div>


                <div class="form-group">

                    <label>
                        Room
                    </label>

                    <input
                        id="locationRoom"
                    >

                </div>


                <div
                    class="form-group full"
                >

                    <label>
                        Description
                    </label>

                    <textarea
                        id="locationDescription"
                        rows="3"
                    ></textarea>

                </div>

            </div>

            <br>

            <button
                class="primary"
                type="submit"
            >
                + Add Location
            </button>

        </form>

    </div>


    <!-- DELETE MANAGEMENT -->

    <div class="section">

        <h2>
            🗑️ Manage Events & Notices
        </h2>

        <p>
            Delete unwanted events or notices
            from the CampusPulse database.
        </p>


        <h3>
            Events
        </h3>

        <div id="adminEvents">
            Loading...
        </div>


        <h3 style="margin-top:25px;">
            Notices
        </h3>

        <div id="adminNotices">
            Loading...
        </div>

    </div>

</section>


</div>

</main>

</div>


<script>

/* =========================================================
   GLOBAL
========================================================= */

let queryCount = 0;


/* =========================================================
   PAGE NAVIGATION
========================================================= */

function showPage(pageId, button) {

    document
        .querySelectorAll(".page")
        .forEach(function(page) {

            page.classList.remove("active");

        });


    const page =
        document.getElementById(pageId);

    if (page) {

        page.classList.add("active");

    }


    document
        .querySelectorAll(".nav-btn")
        .forEach(function(btn) {

            btn.classList.remove("active");

        });


    if (button) {

        button.classList.add("active");

    }


    const titles = {

        dashboard:
            "Dashboard",

        assistant:
            "AI Assistant",

        events:
            "Campus Events",

        notices:
            "Campus Notices",

        locations:
            "Campus Locations",

        map:
            "College Map",

        admin:
            "Admin Panel"

    };


    document.getElementById("pageTitle")
        .textContent =
            titles[pageId] || "CampusPulse";


    if (pageId === "dashboard") {

        loadDashboard();

    }

    if (pageId === "events") {

        loadEvents();

    }

    if (pageId === "notices") {

        loadNotices();

    }

    if (pageId === "locations") {

        loadLocations();

    }

    if (pageId === "admin") {

        loadAdminData();

    }

}


/* =========================================================
   HTML ESCAPE
========================================================= */

function escapeHTML(value) {

    if (value === null ||
        value === undefined) {

        return "";

    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


/* =========================================================
   LOAD DASHBOARD
========================================================= */

async function loadDashboard() {

    try {

        const [
            eventsResponse,
            noticesResponse,
            locationsResponse
        ] = await Promise.all([

            fetch("/api/events"),
            fetch("/api/notices"),
            fetch("/api/locations")

        ]);


        const events =
            await eventsResponse.json();

        const notices =
            await noticesResponse.json();

        const locations =
            await locationsResponse.json();


        document.getElementById(
            "eventCount"
        ).textContent = events.length;


        document.getElementById(
            "noticeCount"
        ).textContent = notices.length;


        document.getElementById(
            "locationCount"
        ).textContent = locations.length;


        const eventContainer =
            document.getElementById(
                "dashboardEvents"
            );


        if (!events.length) {

            eventContainer.innerHTML =
                '<div class="empty">No events available.</div>';

        }
        else {

            eventContainer.innerHTML =
                events.slice(0, 5)
                    .map(eventHTML)
                    .join("");

        }


        const noticeContainer =
            document.getElementById(
                "dashboardNotices"
            );


        if (!notices.length) {

            noticeContainer.innerHTML =
                '<div class="empty">No notices available.</div>';

        }
        else {

            noticeContainer.innerHTML =
                notices.slice(0, 5)
                    .map(noticeHTML)
                    .join("");

        }

    }
    catch(error) {

        console.error(error);

    }

}


/* =========================================================
   EVENT HTML
========================================================= */

function eventHTML(event) {

    return `

        <div class="event">

            <h3>
                🎉 ${escapeHTML(event.name)}
            </h3>

            <p>
                📍 ${escapeHTML(
                    event.location || "Not specified"
                )}
            </p>

            <p>
                📅 ${escapeHTML(
                    event.date || "Not specified"
                )}

                ${
                    event.time
                    ? " • " + escapeHTML(event.time)
                    : ""
                }
            </p>

            <p>
                🏫 ${escapeHTML(
                    event.department || "General"
                )}
            </p>

            ${
                event.description
                ? `<p>${escapeHTML(event.description)}</p>`
                : ""
            }

        </div>

    `;

}


/* =========================================================
   NOTICE HTML
========================================================= */

function noticeHTML(notice) {

    return `

        <div class="notice">

            <h3>
                📢 ${escapeHTML(notice.title)}
            </h3>

            <p>
                ${escapeHTML(notice.content)}
            </p>

            <p style="
                margin-top:8px;
                color:#64748b;
                font-size:13px;
            ">

                📅 ${escapeHTML(notice.date)}

                &nbsp;&nbsp;

                🏫 ${escapeHTML(
                    notice.department || "General"
                )}

            </p>

        </div>

    `;

}


/* =========================================================
   LOAD EVENTS
========================================================= */

async function loadEvents() {

    try {

        const response =
            await fetch("/api/events");

        const events =
            await response.json();


        const container =
            document.getElementById(
                "eventsContainer"
            );


        if (!events.length) {

            container.innerHTML =
                '<div class="empty">No events found.</div>';

            return;

        }


        container.innerHTML =
            events
                .map(eventHTML)
                .join("");

    }
    catch(error) {

        console.error(error);

    }

}


/* =========================================================
   LOAD NOTICES
========================================================= */

async function loadNotices() {

    try {

        const response =
            await fetch("/api/notices");

        const notices =
            await response.json();


        const container =
            document.getElementById(
                "noticesContainer"
            );


        if (!notices.length) {

            container.innerHTML =
                '<div class="empty">No notices found.</div>';

            return;

        }


        container.innerHTML =
            notices
                .map(noticeHTML)
                .join("");

    }
    catch(error) {

        console.error(error);

    }

}


/* =========================================================
   LOAD LOCATIONS
========================================================= */

async function loadLocations() {

    try {

        const response =
            await fetch("/api/locations");

        const locations =
            await response.json();


        const container =
            document.getElementById(
                "locationsContainer"
            );


        if (!locations.length) {

            container.innerHTML =
                '<div class="empty">No locations found.</div>';

            return;

        }


        container.innerHTML =
            locations
                .map(function(location) {

                    return `

                        <div class="location">

                            <h3>
                                📍 ${escapeHTML(
                                    location.name
                                )}
                            </h3>

                            <p>
                                🏢 ${escapeHTML(
                                    location.building
                                )}
                            </p>

                            <p>
                                Floor:
                                ${escapeHTML(
                                    location.floor || "-"
                                )}

                                &nbsp;&nbsp;

                                Room:
                                ${escapeHTML(
                                    location.room || "-"
                                )}
                            </p>

                            ${
                                location.description
                                ? `<p>${escapeHTML(
                                    location.description
                                )}</p>`
                                : ""
                            }

                        </div>

                    `;

                })
                .join("");

    }
    catch(error) {

        console.error(error);

    }

}


/* =========================================================
   AI ASSISTANT
========================================================= */

async function askAI() {

    const input =
        document.getElementById(
            "questionInput"
        );

    const question =
        input.value.trim();


    if (!question) {

        return;

    }


    const chatBox =
        document.getElementById(
            "chatBox"
        );


    chatBox.innerHTML += `

        <div class="message user-message">

            ${escapeHTML(question)}

        </div>

    `;


    input.value = "";


    try {

        const response =
            await fetch(
                "/api/ask",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question: question
                    })

                }
            );


        const result =
            await response.json();


        chatBox.innerHTML += `

            <div class="message ai-message">

                ${escapeHTML(
                    result.answer ||
                    "I could not find an answer."
                )}

            </div>

        `;


        queryCount++;

        document.getElementById(
            "queryCount"
        ).textContent = queryCount;


        chatBox.scrollTop =
            chatBox.scrollHeight;

    }
    catch(error) {

        chatBox.innerHTML += `

            <div class="message ai-message">

                Sorry, I could not connect
                to the CampusPulse server.

            </div>

        `;

    }

}


/* =========================================================
   ADD EVENT
========================================================= */

async function addEvent(event) {

    event.preventDefault();


    const data = {

        name:
            document.getElementById(
                "eventName"
            ).value.trim(),

        location:
            document.getElementById(
                "eventLocation"
            ).value.trim(),

        date:
            document.getElementById(
                "eventDate"
            ).value,

        time:
            document.getElementById(
                "eventTime"
            ).value,

        department:
            document.getElementById(
                "eventDepartment"
            ).value.trim(),

        description:
            document.getElementById(
                "eventDescription"
            ).value.trim()

    };


    try {

        const response =
            await fetch(
                "/api/events",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(data)

                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            alert(
                result.error ||
                "Unable to add event."
            );

            return;

        }


        alert(
            "✓ Event added successfully."
        );


        event.target.reset();


        await loadDashboard();
        await loadEvents();
        await loadAdminData();

    }
    catch(error) {

        console.error(error);

        alert(
            "Unable to connect to server."
        );

    }

}


/* =========================================================
   ADD NOTICE
========================================================= */

async function addNotice(event) {

    event.preventDefault();


    const data = {

        title:
            document.getElementById(
                "noticeTitle"
            ).value.trim(),

        content:
            document.getElementById(
                "noticeContent"
            ).value.trim(),

        date:
            document.getElementById(
                "noticeDate"
            ).value,

        department:
            document.getElementById(
                "noticeDepartment"
            ).value.trim()

    };


    try {

        const response =
            await fetch(
                "/api/notices",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(data)

                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            alert(
                result.error ||
                "Unable to add notice."
            );

            return;

        }


        alert(
            "✓ Notice added successfully."
        );


        event.target.reset();


        await loadDashboard();
        await loadNotices();
        await loadAdminData();

    }
    catch(error) {

        console.error(error);

        alert(
            "Unable to connect to server."
        );

    }

}


/* =========================================================
   ADD LOCATION
========================================================= */

async function addLocation(event) {

    event.preventDefault();


    const data = {

        name:
            document.getElementById(
                "locationName"
            ).value.trim(),

        building:
            document.getElementById(
                "locationBuilding"
            ).value.trim(),

        floor:
            document.getElementById(
                "locationFloor"
            ).value.trim(),

        room:
            document.getElementById(
                "locationRoom"
            ).value.trim(),

        description:
            document.getElementById(
                "locationDescription"
            ).value.trim()

    };


    try {

        const response =
            await fetch(
                "/api/locations",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(data)

                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            alert(
                result.error ||
                "Unable to add location."
            );

            return;

        }


        alert(
            "✓ Location added successfully."
        );


        event.target.reset();


        await loadDashboard();
        await loadLocations();
        await loadAdminData();

    }
    catch(error) {

        console.error(error);

        alert(
            "Unable to connect to server."
        );

    }

}


/* =========================================================
   DELETE EVENT
========================================================= */

async function deleteEvent(eventId) {

    const confirmed =
        confirm(
            "Are you sure you want to delete this event?"
        );


    if (!confirmed) {

        return;

    }


    try {

        const response =
            await fetch(
                "/api/events/" + eventId,
                {
                    method: "DELETE"
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            alert(
                result.error ||
                "Unable to delete event."
            );

            return;

        }


        alert(
            "✓ Event deleted successfully."
        );


        await loadDashboard();
        await loadEvents();
        await loadAdminData();

    }
    catch(error) {

        console.error(error);

        alert(
            "Unable to connect to server."
        );

    }

}


/* =========================================================
   DELETE NOTICE
========================================================= */

async function deleteNotice(noticeId) {

    const confirmed =
        confirm(
            "Are you sure you want to delete this notice?"
        );


    if (!confirmed) {

        return;

    }


    try {

        const response =
            await fetch(
                "/api/notices/" + noticeId,
                {
                    method: "DELETE"
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            alert(
                result.error ||
                "Unable to delete notice."
            );

            return;

        }


        alert(
            "✓ Notice deleted successfully."
        );


        await loadDashboard();
        await loadNotices();
        await loadAdminData();

    }
    catch(error) {

        console.error(error);

        alert(
            "Unable to connect to server."
        );

    }

}


/* =========================================================
   ADMIN DATA
========================================================= */

async function loadAdminData() {

    try {

        const [
            eventsResponse,
            noticesResponse
        ] = await Promise.all([

            fetch("/api/events"),
            fetch("/api/notices")

        ]);


        const events =
            await eventsResponse.json();

        const notices =
            await noticesResponse.json();


        const eventContainer =
            document.getElementById(
                "adminEvents"
            );


        if (!events.length) {

            eventContainer.innerHTML =
                '<div class="empty">No events available.</div>';

        }
        else {

            eventContainer.innerHTML =
                events.map(function(event) {

                    return `

                        <div class="event">

                            <h3>
                                🎉 ${escapeHTML(
                                    event.name
                                )}
                            </h3>

                            <p>
                                📍 ${escapeHTML(
                                    event.location ||
                                    "Not specified"
                                )}
                            </p>

                            <p>
                                📅 ${escapeHTML(
                                    event.date ||
                                    "Not specified"
                                )}
                            </p>

                            <button
                                class="danger"
                                onclick="
                                    deleteEvent(
                                        ${event.id}
                                    )
                                "
                            >
                                🗑 Delete Event
                            </button>

                        </div>

                    `;

                }).join("");

        }


        const noticeContainer =
            document.getElementById(
                "adminNotices"
            );


        if (!notices.length) {

            noticeContainer.innerHTML =
                '<div class="empty">No notices available.</div>';

        }
        else {

            noticeContainer.innerHTML =
                notices.map(function(notice) {

                    return `

                        <div class="notice">

                            <h3>
                                📢 ${escapeHTML(
                                    notice.title
                                )}
                            </h3>

                            <p>
                                ${escapeHTML(
                                    notice.content
                                )}
                            </p>

                            <p style="
                                color:#64748b;
                                font-size:13px;
                            ">

                                📅 ${escapeHTML(
                                    notice.date
                                )}

                            </p>

                            <button
                                class="danger"
                                onclick="
                                    deleteNotice(
                                        ${notice.id}
                                    )
                                "
                            >
                                🗑 Delete Notice
                            </button>

                        </div>

                    `;

                }).join("");

        }

    }
    catch(error) {

        console.error(error);

    }

}


/* =========================================================
   MAP
========================================================= */

function mapInfo(location) {

    alert(
        "📍 " +
        location +
        "\n\nCampusPulse location selected."
    );

}


/* =========================================================
   START
========================================================= */

loadDashboard();

</script>

</body>

</html>
"""


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template_string(HTML)


# ============================================================
# EVENTS GET
# ============================================================

@app.route("/api/events", methods=["GET"])
def get_events():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM events
        ORDER BY date ASC, time ASC
    """).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# EVENTS POST
# ============================================================

@app.route("/api/events", methods=["POST"])
def add_event():

    data = request.get_json(silent=True) or {}

    name = str(
        data.get("name", "")
    ).strip()

    location = str(
        data.get("location", "")
    ).strip()

    date = str(
        data.get("date", "")
    ).strip()

    time = str(
        data.get("time", "")
    ).strip()

    department = str(
        data.get("department", "")
    ).strip()

    description = str(
        data.get("description", "")
    ).strip()


    if not name:

        return jsonify({
            "error":
                "Event name is required."
        }), 400


    if not date:

        return jsonify({
            "error":
                "Event date is required."
        }), 400


    conn = get_db()

    conn.execute("""
        INSERT INTO events
        (
            name,
            location,
            date,
            time,
            department,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        location,
        date,
        time,
        department,
        description
    ))

    conn.commit()
    conn.close()


    return jsonify({
        "success": True,
        "message":
            "Event added successfully."
    })


# ============================================================
# EVENTS DELETE
# ============================================================

@app.route(
    "/api/events/<int:event_id>",
    methods=["DELETE"]
)
def delete_event(event_id):

    conn = get_db()

    cursor = conn.execute(
        """
        DELETE FROM events
        WHERE id = ?
        """,
        (event_id,)
    )

    conn.commit()
    conn.close()


    if cursor.rowcount == 0:

        return jsonify({
            "error":
                "Event not found."
        }), 404


    return jsonify({
        "success": True,
        "message":
            "Event deleted successfully."
    })


# ============================================================
# NOTICES GET
# ============================================================

@app.route("/api/notices", methods=["GET"])
def get_notices():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM notices
        ORDER BY date DESC
    """).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# NOTICES POST
# ============================================================

@app.route("/api/notices", methods=["POST"])
def add_notice():

    data = request.get_json(silent=True) or {}

    title = str(
        data.get("title", "")
    ).strip()

    content = str(
        data.get("content", "")
    ).strip()

    date = str(
        data.get("date", "")
    ).strip()

    department = str(
        data.get("department", "")
    ).strip()


    if not title:

        return jsonify({
            "error":
                "Notice title is required."
        }), 400


    if not content:

        return jsonify({
            "error":
                "Notice content is required."
        }), 400


    if not date:

        return jsonify({
            "error":
                "Notice date is required."
        }), 400


    conn = get_db()

    conn.execute("""
        INSERT INTO notices
        (
            title,
            content,
            date,
            department
        )
        VALUES (?, ?, ?, ?)
    """, (
        title,
        content,
        date,
        department
    ))

    conn.commit()
    conn.close()


    return jsonify({
        "success": True,
        "message":
            "Notice added successfully."
    })


# ============================================================
# NOTICES DELETE
# ============================================================

@app.route(
    "/api/notices/<int:notice_id>",
    methods=["DELETE"]
)
def delete_notice(notice_id):

    conn = get_db()

    cursor = conn.execute(
        """
        DELETE FROM notices
        WHERE id = ?
        """,
        (notice_id,)
    )

    conn.commit()
    conn.close()


    if cursor.rowcount == 0:

        return jsonify({
            "error":
                "Notice not found."
        }), 404


    return jsonify({
        "success": True,
        "message":
            "Notice deleted successfully."
    })


# ============================================================
# LOCATIONS GET
# ============================================================

@app.route("/api/locations", methods=["GET"])
def get_locations():

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM locations
        ORDER BY name ASC
    """).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# LOCATIONS POST
# ============================================================

@app.route("/api/locations", methods=["POST"])
def add_location():

    data = request.get_json(silent=True) or {}

    name = str(
        data.get("name", "")
    ).strip()

    building = str(
        data.get("building", "")
    ).strip()

    floor = str(
        data.get("floor", "")
    ).strip()

    room = str(
        data.get("room", "")
    ).strip()

    description = str(
        data.get("description", "")
    ).strip()


    if not name:

        return jsonify({
            "error":
                "Location name is required."
        }), 400


    if not building:

        return jsonify({
            "error":
                "Building name is required."
        }), 400


    conn = get_db()

    conn.execute("""
        INSERT INTO locations
        (
            name,
            building,
            floor,
            room,
            description
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        building,
        floor,
        room,
        description
    ))

    conn.commit()
    conn.close()


    return jsonify({
        "success": True,
        "message":
            "Location added successfully."
    })


# ============================================================
# AI ASSISTANT
# ============================================================

@app.route("/api/ask", methods=["POST"])
def ask_ai():

    data = request.get_json(
        silent=True
    ) or {}

    question = str(
        data.get("question", "")
    ).strip()


    if not question:

        return jsonify({
            "answer":
                "Please type a question."
        })


    q = question.lower()

    conn = get_db()


    # --------------------------------------------------------
    # GREETINGS
    # --------------------------------------------------------

    greetings = [
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]


    if any(
        re.search(
            r"\b" +
            re.escape(word) +
            r"\b",
            q
        )
        for word in greetings
    ):

        conn.close()

        return jsonify({
            "answer":
                "Hello! 👋 I am CampusPulse AI.\n\n"
                "I can help you find campus events, "
                "notices, locations, departments and "
                "other college information."
        })


    # --------------------------------------------------------
    # EVENTS
    # --------------------------------------------------------

    if (
        "event" in q
        or "events" in q
        or "program" in q
        or "programs" in q
        or "happening" in q
    ):

        rows = conn.execute("""
            SELECT *
            FROM events
            ORDER BY date ASC, time ASC
        """).fetchall()


        if not rows:

            conn.close()

            return jsonify({
                "answer":
                    "There are currently no events "
                    "listed in CampusPulse."
            })


        lines = [
            "Here are the campus events:\n"
        ]


        for row in rows[:8]:

            lines.append(
                "🎉 " +
                row["name"] +
                "\n"
                "📍 " +
                (row["location"] or
                 "Location not specified") +
                "\n"
                "📅 " +
                (row["date"] or
                 "Date not specified") +
                "\n"
            )


        conn.close()

        return jsonify({
            "answer":
                "\n".join(lines)
        })


    # --------------------------------------------------------
    # NOTICES
    # --------------------------------------------------------

    if (
        "notice" in q
        or "notices" in q
        or "announcement" in q
        or "announcements" in q
        or "circular" in q
    ):

        rows = conn.execute("""
            SELECT *
            FROM notices
            ORDER BY date DESC
        """).fetchall()


        if not rows:

            conn.close()

            return jsonify({
                "answer":
                    "There are currently no notices."
            })


        lines = [
            "Here are the latest notices:\n"
        ]


        for row in rows[:8]:

            lines.append(
                "📢 " +
                row["title"] +
                "\n" +
                row["content"] +
                "\n📅 " +
                row["date"] +
                "\n"
            )


        conn.close()

        return jsonify({
            "answer":
                "\n".join(lines)
        })


    # --------------------------------------------------------
    # LOCATION SEARCH
    # --------------------------------------------------------

    location_words = [
        "where",
        "location",
        "room",
        "classroom",
        "lab",
        "library",
        "seminar",
        "office",
        "canteen"
    ]


    if any(
        word in q
        for word in location_words
    ):

        search_terms = [
            word
            for word in q.split()
            if len(word) > 2
        ]


        rows = conn.execute("""
            SELECT *
            FROM locations
        """).fetchall()


        matched = []


        for row in rows:

            searchable = " ".join([
                str(row["name"] or ""),
                str(row["building"] or ""),
                str(row["floor"] or ""),
                str(row["room"] or ""),
                str(row["description"] or "")
            ]).lower()


            if any(
                term in searchable
                for term in search_terms
            ):

                matched.append(row)


        if matched:

            lines = [
                "I found these campus locations:\n"
            ]


            for row in matched[:6]:

                lines.append(
                    "📍 " +
                    row["name"] +
                    "\n"
                    "🏢 " +
                    row["building"] +
                    "\n"
                    "Floor: " +
                    (row["floor"] or "-") +
                    "\n"
                    "Room: " +
                    (row["room"] or "-") +
                    "\n"
                )


            conn.close()

            return jsonify({
                "answer":
                    "\n".join(lines)
            })


    # --------------------------------------------------------
    # SPECIFIC DATABASE SEARCH
    # --------------------------------------------------------

    search = "%" + q + "%"


    event = conn.execute("""
        SELECT *
        FROM events
        WHERE
            LOWER(name) LIKE ?
            OR LOWER(location) LIKE ?
            OR LOWER(department) LIKE ?
            OR LOWER(description) LIKE ?
        LIMIT 1
    """, (
        search,
        search,
        search,
        search
    )).fetchone()


    if event:

        conn.close()

        return jsonify({
            "answer":
                "🎉 Event found:\n\n"
                + event["name"] +
                "\n\n📍 " +
                (event["location"] or
                 "Location not specified") +
                "\n📅 " +
                (event["date"] or
                 "Date not specified") +
                (
                    "\n🕐 " +
                    event["time"]
                    if event["time"]
                    else ""
                )
        })


    notice = conn.execute("""
        SELECT *
        FROM notices
        WHERE
            LOWER(title) LIKE ?
            OR LOWER(content) LIKE ?
            OR LOWER(department) LIKE ?
        LIMIT 1
    """, (
        search,
        search,
        search
    )).fetchone()


    if notice:

        conn.close()

        return jsonify({
            "answer":
                "📢 Notice found:\n\n"
                + notice["title"] +
                "\n\n" +
                notice["content"] +
                "\n\n📅 " +
                notice["date"]
        })


    location = conn.execute("""
        SELECT *
        FROM locations
        WHERE
            LOWER(name) LIKE ?
            OR LOWER(building) LIKE ?
            OR LOWER(floor) LIKE ?
            OR LOWER(room) LIKE ?
            OR LOWER(description) LIKE ?
        LIMIT 1
    """, (
        search,
        search,
        search,
        search,
        search
    )).fetchone()


    if location:

        conn.close()

        return jsonify({
            "answer":
                "📍 Location found:\n\n"
                + location["name"] +
                "\n🏢 " +
                location["building"] +
                "\nFloor: " +
                (location["floor"] or "-") +
                "\nRoom: " +
                (location["room"] or "-")
        })


    # --------------------------------------------------------
    # DEFAULT RESPONSE
    # --------------------------------------------------------

    conn.close()

    return jsonify({
        "answer":
            "I couldn't find that information "
            "in the CampusPulse database yet.\n\n"
            "Try asking about an event, notice, "
            "lab, classroom, library or other "
            "campus location."
    })


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print("")
    print("==========================================")
    print("        CAMPUSPULSE AI")
    print("==========================================")
    print("")
    print(
        "Database:",
        os.path.abspath(DATABASE)
    )
    print("")
    print(
        "Open in browser:"
    )
    print(
        "http://127.0.0.1:5000"
    )
    print("")
    print(
        "Press CTRL+C to stop the server."
    )
    print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )