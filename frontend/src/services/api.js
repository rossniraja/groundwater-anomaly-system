import axios from "axios";

const API = axios.create({
baseURL: "https://groundwater-anomaly-system.onrender.com",
});

export const getOverview = async () => {
  const response = await API.get("/overview");
  return response.data;
};

export const getStations = async () => {
  const response = await API.get("/stations");
  return response.data;
};

export const getAnomalies = async () => {
  const response = await API.get("/anomalies");
  return response.data;
};

export const getForecast = async () => {
  const response = await API.get("/forecast");
  return response.data;
};

export const getAlerts = async () => {
  const response = await API.get("/alerts");
  return response.data;
};
export const getStationById = async (stationCode) => {
  const response = await API.get(`/stations/${stationCode}`);
  return response.data;
};