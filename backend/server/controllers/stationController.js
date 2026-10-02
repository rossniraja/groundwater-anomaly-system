const fs = require("fs");
const csv = require("csv-parser");

const filePath =
    "../data/processed/karnataka_telemetry_2026_part1_ml_output.csv";

const getStations = (req, res) => {
    const stations = [];

    fs.createReadStream(filePath)
        .pipe(csv())
        .on("data", (row) => {
            stations.push({
                station_code: row.station_code,
                state: row.state,
                district: row.district,
                block_name: row.block_name,
                latitude: Number(row.latitude),
                longitude: Number(row.longitude),
                monitoring_date: row.monitoring_date,
                ground_water_level: Number(row.ground_water_level),
                water_level_change: Number(row.water_level_change),
                anomaly_flag: row.anomaly_flag,
                is_anomaly: row.is_anomaly,
                anomaly_score: Number(row.anomaly_score),
                risk_level: row.risk_level,
                forecast_level: Number(row.forecast_level)
            });
        })
        .on("end", () => {
            res.json(stations);
        })
        .on("error", (error) => {
            console.error(error);
            res.status(500).json({
                error: "Failed to read station data"
            });
        });
};

module.exports = {
    getStations
};