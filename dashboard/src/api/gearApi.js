import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: API_BASE, timeout: 120000 }); // Increased to 120 seconds for optimizer

export const predict = (sensors, gearType = 'Helical') =>
  api.post('/api/predict', { ...sensors, gear_type: gearType }).then(r => r.data);

export const predictSpur = (sensors) =>
  api.post('/api/predict-spur', sensors).then(r => r.data);

export const getGearConfigs = () =>
  api.get('/api/gear-configs').then(r => r.data);

export const getModels = () =>
  api.get('/api/models').then(r => r.data);

export const getBevelSpecs = () =>
  api.get('/api/bevel-specs').then(r => r.data);

export const chat = (question, gearId, sensorValues, chatHistory = []) =>
  api.post('/api/chat', { question, gear_id: gearId, sensor_values: sensorValues, chat_history: chatHistory }).then(r => r.data);

export const generateReport = (gearId, sensorValues) =>
  api.post('/api/report', { gear_id: gearId, sensor_values: sensorValues }).then(r => r.data);

export const getReportPdfData = (gearId, sensorValues, gearType) =>
  api.post('/api/report-pdf-data', { gear_id: gearId, sensor_values: sensorValues, gear_type: gearType }).then(r => r.data);

export const optimize = (sensorValues, locks, targetProbability) =>
  api.post('/api/optimize', { sensor_values: sensorValues, locks, target_probability: targetProbability }).then(r => r.data);

export const getSensitivity = (sensors) =>
  api.post('/api/sensitivity', sensors).then(r => r.data);

export const getLime = (sensors) =>
  api.get('/api/lime', { params: sensors }).then(r => r.data);

export const getLimeSpur = (sensors) =>
  api.get('/api/lime-spur', { params: sensors }).then(r => r.data);

export const getLimeBevel = (sensors) =>
  api.get('/api/lime-bevel', { params: sensors }).then(r => r.data);

export const getHistory = () =>
  api.get('/api/history').then(r => r.data);

export const logHistory = (entry) =>
  api.post('/api/history', entry).then(r => r.data);

export const clearHistory = () =>
  api.delete('/api/history').then(r => r.data);

export const getConfusionMatrix = () =>
  api.get('/api/confusion-matrix').then(r => r.data);

export const getFeatureImportance = () =>
  api.get('/api/feature-importance').then(r => r.data);

export default api;
