import React from 'react';
import '../styles/LoadingScreen.css';

const LoadingScreen = () => (
  <div className="loading-inline">
    <div className="spinner"></div>
    <div className="loading-message">Loading, please wait...</div>
  </div>
);

export default LoadingScreen; 