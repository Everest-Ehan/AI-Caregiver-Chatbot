import React from 'react';
import { createRoot } from 'react-dom/client';
import Chatbot from './modules/Chatbot.jsx';
import './index.css';
import './styles/chatbot.css';

const root = createRoot(document.getElementById('app'));
root.render(<Chatbot />); 