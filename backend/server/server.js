const express = require("express");
const cors = require("cors");
const axios = require("axios");
const pool = require("./db");
require("dotenv").config();

const app = express();


// ======================================================
// MIDDLEWARE
// ======================================================

app.use(cors());
app.use(express.json());


// ======================================================
// HOME API
// ======================================================

app.get("/", (req, res) => {
    res.json({
        message: "NIVORA backend is running",
        status: "success"
    });
});


// ======================================================
// OVERVIEW API
// Node.js → PostgreSQL
// Real station counts
// ======================================================

app.get("/api/overview", async (req, res) => {
    try {
        const result = await pool.query(`
            SELECT
                COUNT(*) AS total_stations,
                COUNT(*) FILTER (WHERE risk_level = 'SAFE') AS safe_stations,
                COUNT(*) FILTER (WHERE risk_level = 'WATCH') AS watch_stations,
                COUNT(*) FILTER (WHERE risk_level = 'WARNING') AS warning_stations,
                COUNT(*) FILTER (WHERE risk_level = 'CRITICAL') AS critical_stations
            FROM stations
        `);

        const data = result.rows[0];

        res.json({
            totalStations: Number(data.total_stations),
            safeStations: Number(data.safe_stations),
            watchStations: Number(data.watch_stations),
            warningStations: Number(data.warning_stations),
            criticalStations: Number(data.critical_stations)
        });

    } catch (error) {
        console.error("Database error:", error.message);

        res.status(500).json({
            message: "Could not fetch overview data"
        });
    }
});


// ======================================================
// ALL STATIONS API
// Node.js → PostgreSQL
// ======================================================

app.get("/api/stations", async (req, res) => {
    try {
        const result = await pool.query(
            "SELECT * FROM stations ORDER BY station_code"
        );

        res.json(result.rows);

    } catch (error) {
        console.error("Database error:", error.message);

        res.status(500).json({
            message: "Could not fetch station data"
        });
    }
});


// ======================================================
// SINGLE STATION API
// Node.js → PostgreSQL
// ======================================================

app.get("/api/stations/:id", async (req, res) => {
    try {
        const stationId = req.params.id;

        const result = await pool.query(
            "SELECT * FROM stations WHERE station_code = $1",
            [stationId]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({
                message: "Station not found"
            });
        }

        res.json(result.rows[0]);

    } catch (error) {
        console.error("Database error:", error.message);

        res.status(500).json({
            message: "Could not fetch station details"
        });
    }
});


// ======================================================
// ANOMALY API
// Node.js → FastAPI → ML
// ======================================================

app.get("/api/anomalies", async (req, res) => {
    try {
        const response = await axios.get(
            "http://localhost:8000/anomalies"
        );

        res.json(response.data);

    } catch (error) {
        console.error("FastAPI error:", error.message);

        res.status(500).json({
            message: "Could not fetch anomaly data"
        });
    }
});


// ======================================================
// FORECAST API
// Node.js → FastAPI → ML
// ======================================================

app.get("/api/forecast", async (req, res) => {
    try {
        const response = await axios.get(
            "http://localhost:8000/forecast"
        );

        res.json(response.data);

    } catch (error) {
        console.error("FastAPI error:", error.message);

        res.status(500).json({
            message: "Could not fetch forecast data"
        });
    }
});


// ======================================================
// ALERTS API
// Node.js → FastAPI → ML
// ======================================================

app.get("/api/alerts", async (req, res) => {
    try {
        const response = await axios.get(
            "http://localhost:8000/alerts"
        );

        res.json(response.data);

    } catch (error) {
        console.error("FastAPI error:", error.message);

        res.status(500).json({
            message: "Could not fetch alert data"
        });
    }
});


// ======================================================
// SERVER
// ======================================================

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
    console.log(`NIVORA backend running on port ${PORT}`);
});