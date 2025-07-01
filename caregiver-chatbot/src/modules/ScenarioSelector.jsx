import React, { useState } from 'react';

export default function ScenarioSelector({ scenarios, onScenarioSelect, isExpanded, onToggleExpanded }) {

  return (
    <div className={`scenario-selector-container ${isExpanded ? 'expanded' : ''}`}>
      <div className="panel-header">
        <h3>Scenario Selection</h3>
        <p>Choose a conversation scenario</p>
      </div>
      
      <div 
        className="scenario-selector-header"
        onClick={onToggleExpanded}
      >
        <h4 className="scenario-selector-title">Available Scenarios</h4>
        <button className="scenario-selector-toggle">
          {isExpanded ? 'Hide' : 'Show'} Scenarios
        </button>
      </div>
      
      <div className="scenario-selector-content">
        {scenarios.map(scenario => (
          <div
            key={scenario.id}
            className="scenario-card"
            onClick={() => onScenarioSelect(scenario.id)}
          >
            <div className="scenario-card-content">
              <h4>{scenario.name}</h4>
              <p>{scenario.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 