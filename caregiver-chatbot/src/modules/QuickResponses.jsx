import React, { useState } from 'react';

const responseCategories = {
  greetings: {
    name: 'Greetings',
    responses: [
      'I am doing well, how are you?',
      'I am doing good, thank you for asking',
      'I am doing okay, how are you?',
      'Hi, how are you?',
      'Hello, I am fine'
    ]
  },
  confirmations: {
    name: 'Confirmations',
    responses: [
      'Yes, that is correct',
      'Yes, I can confirm that',
      'Yes, that is right',
      'No, that is not correct',
      'No, I cannot confirm that'
    ]
  },
  client_info: {
    name: 'Client Info',
    responses: [
      'The client name is John Doe',
      'I am working with John Doe',
      'This is my regular client',
      'The client asked me to come today',
      'The client is available to speak'
    ]
  },
  schedule: {
    name: 'Schedule',
    responses: [
      'My regular schedule is Monday through Friday 9am to 5pm',
      'I usually work Mondays, Wednesdays and Fridays',
      'I can stay late to make up hours',
      'I will remove Friday from my schedule',
      'I can work any other day this week'
    ]
  },
  technical: {
    name: 'Technical Issues',
    responses: [
      'I forgot to clock in',
      'The app is not working',
      'I am having GPS issues',
      'I used the wrong phone number',
      'I will try using the unscheduled visit option'
    ]
  },
  time: {
    name: 'Time & Arrival',
    responses: [
      'I arrived at 9am',
      'I was here on time but forgot to clock in',
      'I arrived 5 minutes after 9',
      'I can stay late today',
      'I can make up hours on Tuesday'
    ]
  },
  location: {
    name: 'Location',
    responses: [
      'I am at the client\'s house',
      'I clocked in from the client\'s house',
      'I had to pick up groceries for the client',
      'I will go back to clock out properly',
      'I am inside the client\'s home'
    ]
  },
  phone: {
    name: 'Phone Issues',
    responses: [
      'I used the client\'s house phone',
      'The client won\'t allow me to use their phone',
      'This is the client\'s new phone number',
      'I will use the HHA app instead',
      'I need help setting up the app'
    ]
  }
};

export default function QuickResponses({ onResponseSelect }) {
  const [selectedCategory, setSelectedCategory] = useState(Object.keys(responseCategories)[0]);

  const category = responseCategories[selectedCategory];

  return (
    <div className="quick-responses-container">
      <div className="panel-header">
        <h3>Quick Responses</h3>
        <p>Select a response to quickly reply</p>
      </div>
      <div className="response-categories">
        {Object.entries(responseCategories).map(([key, cat]) => (
          <button
            key={key}
            className={`category-bubble${selectedCategory === key ? ' active' : ''}`}
            onClick={() => setSelectedCategory(key)}
          >
            {cat.name}
          </button>
        ))}
      </div>
      <div className="quick-responses-list">
        <div className="quick-responses active" data-category={selectedCategory}>
          <h4 className="response-category-title">{category.name}</h4>
          <div className="response-category-buttons">
            {category.responses.map((response, idx) => (
              <button
                key={idx}
                className="quick-response-btn"
                onClick={() => onResponseSelect(response)}
              >
                {response}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 