export default function ScenarioSelector(onScenarioSelect) {
  const element = document.createElement('div');
  element.className = 'scenario-selector';

  function updateScenarios(scenarios) {
    element.innerHTML = '';
    
    scenarios.forEach(scenario => {
      const card = document.createElement('div');
      card.className = 'scenario-card';
      card.innerHTML = `
        <div class="scenario-card-content">
          <h4>${scenario.name}</h4>
          <p>${scenario.description}</p>
        </div>
      `;
      
      card.addEventListener('click', () => {
        // Remove active class from all cards
        element.querySelectorAll('.scenario-card').forEach(c => c.classList.remove('active'));
        // Add active class to clicked card
        card.classList.add('active');
        onScenarioSelect(scenario.id);
      });
      
      element.appendChild(card);
    });
  }

  return {
    element,
    updateScenarios
  };
} 