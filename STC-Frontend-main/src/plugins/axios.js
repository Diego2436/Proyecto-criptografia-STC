// src/services/axios.js

import axios from 'axios';
import localforage from 'localforage';

// Configura la base URL de Axios
axios.defaults.baseURL = 'http://localhost:5000'; // Cambia esto por la URL de tu servidor Flask

// Configura los interceptores de solicitud para agregar el token de autorización
axios.interceptors.request.use(async config => {
  const authToken = await localforage.getItem('authToken');
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

export default axios;
