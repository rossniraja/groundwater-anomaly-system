const fs = require("fs");
const csv = require("csv-parser");
const pool = require("./db");

const filePath = "../data/processed/stations_latest.csv";

function valueOrNull(value) {
    return value === undefined || value === null || value.trim() === ""
        ? null
        : value;
}

async function importStations() {
    const stations = [];

    fs.createReadStream(filePath)
        .pipe(csv())
        .on("data", (row) => {
            stations.push(row);
        })
        .on("end", async () => {
            console.log(`CSV rows found: ${stations.length}`);

            try {
                for (const station of stations) {
                    await pool.query(
                        `INSERT INTO stations
                        (
                            station_code,
                            state,
                            district,
                            block_name,
                            latitude,
                            longitude,
                            ground_water_level,
                            anomaly_score,
                            risk_level,
                            forecast_level,
                            monitoring_date
                        )
                        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
                        ON CONFLICT (station_code)
                        DO NOTHING`,
                        [
                            valueOrNull(station.station_code),
                            valueOrNull(station.state),
                            valueOrNull(station.district),
                            valueOrNull(station.block_name),
                            valueOrNull(station.latitude),
                            valueOrNull(station.longitude),
                            valueOrNull(station.ground_water_level),
                            valueOrNull(station.anomaly_score),
                            valueOrNull(station.risk_level),
                            valueOrNull(station.forecast_level),
                            valueOrNull(station.monitoring_date)
                        ]
                    );
                }

                console.log("Stations imported successfully!");
            } catch (error) {
                console.error("Import failed:", error.message);
            } finally {
                await pool.end();
            }
        });
}

importStations();