import { useEffect, useState } from "react";
import "./App.css";

import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

import {
  getOverview,
  getStations,
  getStationById,
  getAnomalies,
  getForecast,
  getAlerts,
} from "./services/api";

const pages = [
  "overview",
  "stations",
  "anomalies",
  "forecast",
  "alerts",
];

function App() {
  const [activePage, setActivePage] = useState("overview");

  const [overview, setOverview] = useState(null);
  const [stations, setStations] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [forecast, setForecast] = useState([]);
  const [alerts, setAlerts] = useState([]);

  const [selectedStation, setSelectedStation] = useState(null);

  const [loading, setLoading] = useState(false);
  const [stationLoading, setStationLoading] = useState(false);

  const [error, setError] = useState("");
  const [stationError, setStationError] = useState("");

  useEffect(() => {
    loadPageData(activePage);
  }, [activePage]);

  async function loadPageData(page) {
    setLoading(true);
    setError("");

    try {
      if (page === "overview") {
        const data = await getOverview();
        setOverview(data);
      }

      if (page === "stations") {
        const data = await getStations();
        setStations(data);
      }

      if (page === "anomalies") {
        const data = await getAnomalies();
        setAnomalies(data);
      }

      if (page === "forecast") {
        const data = await getForecast();
        setForecast(data);
      }

      if (page === "alerts") {
        const data = await getAlerts();
        setAlerts(data);
      }
    } catch (err) {
      console.error(`${page} API error:`, err);
      setError(`Could not load ${page} data.`);
    } finally {
      setLoading(false);
    }
  }

  async function investigateStation(stationCode) {
    setStationLoading(true);
    setStationError("");

    try {
      const data = await getStationById(stationCode);
      setSelectedStation(data);
    } catch (err) {
      console.error("Station API error:", err);

      setStationError("Could not load station details.");
      setSelectedStation(null);
    } finally {
      setStationLoading(false);
    }
  }

  function closeInvestigation() {
    setSelectedStation(null);
    setStationError("");
  }

  function goTo(page) {
    setSelectedStation(null);
    setStationError("");
    setActivePage(page);
  }

  return (
    <div className="app-shell">

      {/* TOP NAVIGATION */}
      <header className="topbar">

        <button
          className="brand"
          type="button"
          onClick={() => goTo("overview")}
        >
          <div className="brand-mark">N</div>

          <div className="brand-text">
            <strong>NIVORA</strong>
            <span>Groundwater Intelligence</span>
          </div>
        </button>

        <nav className="main-nav">
          {pages.map((page) => (
            <button
              key={page}
              type="button"
              className={activePage === page ? "active" : ""}
              onClick={() => goTo(page)}
            >
              {page}
            </button>
          ))}
        </nav>

        <div className="system-status">
          <span />
          LIVE
        </div>

      </header>


      {/* MAIN CONTENT */}
      <main className="page-container">

        {loading && (
          <div className="api-loading">
            Loading intelligence...
          </div>
        )}

        {error && (
          <div className="api-error">
            {error}
          </div>
        )}


        {/* OVERVIEW */}
        {activePage === "overview" && (
          <Overview
            overview={overview}
            goTo={goTo}
          />
        )}


        {/* STATIONS */}
        {activePage === "stations" && (
          <Stations
            stations={stations}
            selectedStation={selectedStation}
            investigateStation={investigateStation}
            closeInvestigation={closeInvestigation}
            stationLoading={stationLoading}
            stationError={stationError}
          />
        )}


        {/* ANOMALIES */}
        {activePage === "anomalies" && (
          <Anomalies
            anomalies={anomalies}
            investigateStation={investigateStation}
            selectedStation={selectedStation}
            closeInvestigation={closeInvestigation}
            stationLoading={stationLoading}
            stationError={stationError}
          />
        )}


        {/* FORECAST */}
        {activePage === "forecast" && (
          <Forecast
            forecast={forecast}
          />
        )}


        {/* ALERTS */}
        {activePage === "alerts" && (
          <Alerts
            alerts={alerts}
            investigateStation={investigateStation}
            selectedStation={selectedStation}
            closeInvestigation={closeInvestigation}
            stationLoading={stationLoading}
            stationError={stationError}
          />
        )}

      </main>


      {/* FOOTER */}
      <footer className="bottom-bar">
        <span>NIVORA / 2026</span>
        <span>Groundwater Intelligence Platform</span>
      </footer>

    </div>
  );
}


/* =========================================================
   OVERVIEW
========================================================= */

function Overview({ overview, goTo }) {

  if (!overview) {
    return (
      <section className="overview-page">
        <PageHeader
          eyebrow="GROUNDWATER INTELLIGENCE"
          title="Monitoring groundwater conditions."
          description="NIVORA transforms monitoring-station data into understandable groundwater intelligence."
        />
      </section>
    );
  }

  return (
    <section className="overview-page">

      <div className="overview-hero">

        <div className="hero-copy">

          <div className="eyebrow">
            GROUNDWATER INTELLIGENCE PLATFORM
          </div>

          <h1>
            Know which
            <br />
            stations need
            <br />
            attention.
          </h1>

          <p>
            NIVORA monitors groundwater conditions using
            real station observations, anomaly detection,
            risk analysis and forecasting.
          </p>

          <div className="hero-actions">

            <button
              type="button"
              className="primary-button"
              onClick={() => goTo("stations")}
            >
              Explore stations
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={() => goTo("anomalies")}
            >
              View anomalies
            </button>

          </div>

        </div>


        <div className="hero-orb">

          <div className="orb-ring ring-one" />
          <div className="orb-ring ring-two" />
          <div className="orb-core">
            <span>LIVE</span>
            <strong>{formatNumber(overview.totalStations)}</strong>
            <small>MONITORING STATIONS</small>
          </div>

        </div>

      </div>


      <div className="overview-intelligence">

        <div className="overview-summary">
          <span>CURRENT NETWORK STATE</span>

          <strong>
            {formatNumber(overview.safeStations)} stations
            currently within the safe monitoring range.
          </strong>
        </div>


        <div className="risk-strip">

          <RiskValue
            label="SAFE"
            value={overview.safeStations}
            className="safe"
          />

          <RiskValue
            label="WATCH"
            value={overview.watchStations}
            className="watch"
          />

          <RiskValue
            label="WARNING"
            value={overview.warningStations}
            className="warning"
          />

          <RiskValue
            label="CRITICAL"
            value={overview.criticalStations}
            className="critical"
          />

        </div>

      </div>

    </section>
  );
}


/* =========================================================
   STATIONS
========================================================= */

function Stations({
  stations,
  selectedStation,
  investigateStation,
  closeInvestigation,
  stationLoading,
  stationError,
}) {

  return (
    <section className="data-page">

      <PageHeader
        eyebrow="MONITORING NETWORK"
        title="Stations"
        description="Explore monitoring locations and investigate individual groundwater conditions."
      />


      <div className="stations-layout">

        <div className="map-panel">

          <MapContainer
            center={[14.5, 76.5]}
            zoom={6}
            scrollWheelZoom={true}
            className="station-map"
          >

            <TileLayer
              attribution='&copy; OpenStreetMap contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {stations.map((station) => {

              const riskClass = getRiskClass(
                station.risk_level
              );

              const latitude = Number(station.latitude);
              const longitude = Number(station.longitude);

              if (
                Number.isNaN(latitude) ||
                Number.isNaN(longitude)
              ) {
                return null;
              }

              return (
                <CircleMarker
                  key={station.station_code}
                  center={[latitude, longitude]}
                  radius={6}
                  pathOptions={{
                    className: riskClass,
                  }}
                >

                  <Popup>

                    <div className="map-popup">

                      <strong>
                        {station.station_code}
                      </strong>

                      <span>
                        {station.block_name || "Unknown block"}
                      </span>

                      <span>
                        {station.district || "Unknown district"}
                      </span>

                      <span>
                        Risk:{" "}
                        <b>
                          {station.risk_level || "UNKNOWN"}
                        </b>
                      </span>

                      <button
                        type="button"
                        onClick={() =>
                          investigateStation(
                            station.station_code
                          )
                        }
                      >
                        Investigate station
                      </button>

                    </div>

                  </Popup>

                </CircleMarker>
              );
            })}

          </MapContainer>

        </div>


        <aside className="station-side">

          <div className="side-heading">
            <span>NETWORK</span>
            <strong>
              {formatNumber(stations.length)} stations
            </strong>
          </div>


          <div className="station-list">

            {stations.slice(0, 8).map((station) => (

              <button
                key={station.station_code}
                type="button"
                className="station-item"
                onClick={() =>
                  investigateStation(
                    station.station_code
                  )
                }
              >

                <div>

                  <strong>
                    {station.station_code}
                  </strong>

                  <span>
                    {station.block_name ||
                      station.district ||
                      "Unknown location"}
                  </span>

                </div>

                <span
                  className={`risk-badge ${getRiskClass(
                    station.risk_level
                  )}`}
                >
                  {station.risk_level || "UNKNOWN"}
                </span>

              </button>

            ))}

          </div>

        </aside>

      </div>


      {stationLoading && (
        <div className="investigation-loading">
          Loading station intelligence...
        </div>
      )}

      {stationError && (
        <div className="station-error">
          {stationError}
        </div>
      )}

      {selectedStation && (
        <StationInvestigation
          station={selectedStation}
          onClose={closeInvestigation}
        />
      )}

    </section>
  );
}


/* =========================================================
   STATION INVESTIGATION
========================================================= */

function StationInvestigation({
  station,
  onClose,
}) {

  if (!station) {
    return null;
  }

  return (
    <section className="station-investigation">

      <div className="investigation-header">

        <div>

          <span className="investigation-eyebrow">
            STATION INVESTIGATION
          </span>

          <h2>
            {station.station_code}
          </h2>

          <p className="investigation-location">
            {station.block_name || "Unknown block"}
            {station.district
              ? ` · ${station.district}`
              : ""}
            {station.state
              ? ` · ${station.state}`
              : ""}
          </p>

        </div>


        <button
          type="button"
          className="investigation-close"
          onClick={onClose}
          aria-label="Close station investigation"
          title="Close investigation"
        >
          ×
        </button>

      </div>


      <div className="investigation-grid">

        <InvestigationMetric
          label="GROUNDWATER LEVEL"
          value={formatNumber(
            station.ground_water_level
          )}
          unit="m"
        />

        <InvestigationMetric
          label="ANOMALY SCORE"
          value={formatNumber(
            station.anomaly_score
          )}
        />

        <InvestigationMetric
          label="FORECAST LEVEL"
          value={formatNumber(
            station.forecast_level
          )}
          unit="m"
        />

        <div className="investigation-metric">

          <span>RISK LEVEL</span>

          <strong
            className={`investigation-risk ${getRiskClass(
              station.risk_level
            )}`}
          >
            {station.risk_level || "UNKNOWN"}
          </strong>

        </div>

      </div>


      <div className="investigation-footer">

        <span>
          LAST MONITORED
        </span>

        <strong>
          {formatDate(station.monitoring_date)}
        </strong>

      </div>

    </section>
  );
}


function InvestigationMetric({
  label,
  value,
  unit,
}) {

  return (
    <div className="investigation-metric">

      <span>{label}</span>

      <strong>
        {value}

        {unit && (
          <small>
            {" "}
            {unit}
          </small>
        )}
      </strong>

    </div>
  );
}


/* =========================================================
   ANOMALIES
========================================================= */

function Anomalies({
  anomalies,
  investigateStation,
  selectedStation,
  closeInvestigation,
  stationLoading,
  stationError,
}) {

  const watchCount = anomalies.filter(
    (item) => item.risk_level === "WATCH"
  ).length;

  const warningCount = anomalies.filter(
    (item) => item.risk_level === "WARNING"
  ).length;

  const criticalCount = anomalies.filter(
    (item) => item.risk_level === "CRITICAL"
  ).length;

  return (
    <section className="data-page">

      <PageHeader
        eyebrow="ANOMALY DETECTION"
        title="Anomalies"
        description="Stations where observed groundwater behaviour differs from expected conditions."
      />


      <div className="anomaly-summary">

        <RiskValue
          label="WATCH"
          value={watchCount}
          className="watch"
        />

        <RiskValue
          label="WARNING"
          value={warningCount}
          className="warning"
        />

        <RiskValue
          label="CRITICAL"
          value={criticalCount}
          className="critical"
        />

      </div>


      <div className="anomaly-list">

        {anomalies.slice(0, 10).map((item) => (

          <div
            className="anomaly-row"
            key={item.station_code}
          >

            <div className="anomaly-station">

              <strong>
                {item.station_code}
              </strong>

              <span>
                {item.block_name ||
                  item.district ||
                  "Unknown location"}
              </span>

            </div>


            <div className="anomaly-score">

              <span>
                SCORE
              </span>

              <strong>
                {formatNumber(item.anomaly_score)}
              </strong>

            </div>


            <div
              className={`anomaly-level ${getRiskClass(
                item.risk_level
              )}`}
            >
              {item.risk_level}
            </div>


            <button
              type="button"
              className="investigate-button"
              onClick={() =>
                investigateStation(
                  item.station_code
                )
              }
            >
              Investigate
            </button>

          </div>

        ))}

      </div>


      {stationLoading && (
        <div className="investigation-loading">
          Loading station intelligence...
        </div>
      )}

      {stationError && (
        <div className="station-error">
          {stationError}
        </div>
      )}

      {selectedStation && (
        <StationInvestigation
          station={selectedStation}
          onClose={closeInvestigation}
        />
      )}

    </section>
  );
}


/* =========================================================
   FORECAST
========================================================= */

function Forecast({ forecast }) {

  const current = forecast[0];

  if (!current) {
    return (
      <section className="data-page">

        <PageHeader
          eyebrow="PREDICTIVE INTELLIGENCE"
          title="Forecast"
          description="Groundwater level projections from the forecasting pipeline."
        />

        <div className="empty-state">
          No forecast data available.
        </div>

      </section>
    );
  }

  const currentLevel = Number(
    current.ground_water_level
  );

  const forecastLevel = Number(
    current.forecast_level
  );

  const difference =
    forecastLevel - currentLevel;

  return (
    <section className="data-page">

      <PageHeader
        eyebrow="PREDICTIVE INTELLIGENCE"
        title="Forecast"
        description="Compare the latest observed groundwater level with the forecast produced by NIVORA."
      />


      <div className="forecast-layout">

        <div className="forecast-intro">

          <span>
            STATION
          </span>

          <strong>
            {current.station_code}
          </strong>

          <small>
            {current.block_name ||
              "Monitoring station"}
          </small>

        </div>


        <div className="forecast-chart">

          <div className="chart-heading">

            <div>
              <span>
                CURRENT → FORECAST
              </span>

              <strong>
                {formatNumber(currentLevel)} m
                {" → "}
                {formatNumber(forecastLevel)} m
              </strong>
            </div>

            <span className="forecast-risk">
              {current.risk_level}
            </span>

          </div>


          <svg
            viewBox="0 0 700 240"
            className="forecast-svg"
            preserveAspectRatio="none"
          >

            <line
              x1="20"
              y1="190"
              x2="680"
              y2="190"
              className="chart-axis"
            />

            <line
              x1="20"
              y1="50"
              x2="20"
              y2="190"
              className="chart-axis"
            />

            <polyline
              points="20,155 150,145 280,150 410,120 540,100 680,75"
              className="forecast-line"
            />

            <circle
              cx="20"
              cy="155"
              r="6"
              className="forecast-point"
            />

            <circle
              cx="680"
              cy="75"
              r="7"
              className="forecast-point"
            />

          </svg>


          <div className="chart-labels">

            <span>
              Current
            </span>

            <span>
              Forecast
            </span>

          </div>

        </div>


        <div className="forecast-status">

          <span>
            CHANGE
          </span>

          <strong>
            {difference >= 0 ? "+" : ""}
            {formatNumber(difference)} m
          </strong>

          <small>
            Projected groundwater level
          </small>

        </div>

      </div>

    </section>
  );
}


/* =========================================================
   ALERTS
========================================================= */

function Alerts({
  alerts,
  investigateStation,
  selectedStation,
  closeInvestigation,
  stationLoading,
  stationError,
}) {

  return (
    <section className="data-page">

      <PageHeader
        eyebrow="RESPONSE CENTRE"
        title="Alerts"
        description="Stations requiring attention based on detected groundwater risk."
      />


      <div className="alert-banner">

        <div>
          <span>
            ACTIVE RESPONSE QUEUE
          </span>

          <strong>
            {alerts.length} stations
            requiring attention
          </strong>
        </div>

        <div className="alert-indicator">
          ●
        </div>

      </div>


      <div className="alert-list">

        {alerts.slice(0, 10).map((item) => (

          <div
            className="alert-row"
            key={item.station_code}
          >

            <div className="alert-station">

              <strong>
                {item.station_code}
              </strong>

              <span>
                {item.district ||
                  item.block_name ||
                  "Unknown location"}
              </span>

            </div>


            <div className="alert-level">

              <span>
                RISK
              </span>

              <strong
                className={getRiskClass(
                  item.risk_level
                )}
              >
                {item.risk_level}
              </strong>

            </div>


            <div className="alert-score">

              <span>
                ANOMALY
              </span>

              <strong>
                {formatNumber(
                  item.anomaly_score
                )}
              </strong>

            </div>


            <div className="alert-forecast">

              <span>
                FORECAST
              </span>

              <strong>
                {formatNumber(
                  item.forecast_level
                )} m
              </strong>

            </div>


            <button
              type="button"
              className="investigate-button"
              onClick={() =>
                investigateStation(
                  item.station_code
                )
              }
            >
              Investigate
            </button>

          </div>

        ))}

      </div>


      {stationLoading && (
        <div className="investigation-loading">
          Loading station intelligence...
        </div>
      )}

      {stationError && (
        <div className="station-error">
          {stationError}
        </div>
      )}

      {selectedStation && (
        <StationInvestigation
          station={selectedStation}
          onClose={closeInvestigation}
        />
      )}

    </section>
  );
}


/* =========================================================
   SHARED COMPONENTS
========================================================= */

function PageHeader({
  eyebrow,
  title,
  description,
}) {

  return (
    <div className="page-header">

      <span className="eyebrow">
        {eyebrow}
      </span>

      <h1>
        {title}
      </h1>

      <p>
        {description}
      </p>

    </div>
  );
}


function RiskValue({
  label,
  value,
  className,
}) {

  return (
    <div className={`risk-value ${className}`}>

      <span>
        {label}
      </span>

      <strong>
        {formatNumber(value)}
      </strong>

    </div>
  );
}


/* =========================================================
   HELPERS
========================================================= */

function formatNumber(value) {

  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return String(value);
  }

  return number.toLocaleString("en-IN", {
    maximumFractionDigits: 2,
  });
}


function formatDate(value) {

  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}


function getRiskClass(risk) {

  if (!risk) {
    return "";
  }

  return String(risk).toLowerCase();
}


export default App;