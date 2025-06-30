export default function QuickResponses(onResponseSelect) {
  const container = document.createElement('div');
  container.className = 'quick-responses-container';

  // Response categories organized by type
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

  // Create category bubbles
  const categoryBubbles = document.createElement('div');
  categoryBubbles.className = 'response-categories';

  Object.entries(responseCategories).forEach(([categoryKey, category]) => {
    const bubble = document.createElement('button');
    bubble.className = 'category-bubble';
    bubble.textContent = category.name;
    bubble.dataset.category = categoryKey;
    
    bubble.addEventListener('click', () => {
      // Remove active class from all bubbles
      categoryBubbles.querySelectorAll('.category-bubble').forEach(b => b.classList.remove('active'));
      // Add active class to clicked bubble
      bubble.classList.add('active');
      // Show the selected category
      showCategory(categoryKey);
    });
    
    categoryBubbles.appendChild(bubble);
  });

  // Create responses container
  const responsesContainer = document.createElement('div');
  responsesContainer.className = 'quick-responses-list'; // changed from 'quick-responses'
  responsesContainer.id = 'quickResponses';

  function showCategory(categoryKey) {
    const category = responseCategories[categoryKey];
    if (!category) return;

    // Remove all previous category containers
    responsesContainer.innerHTML = '';

    // Create and show the selected category
    createCategoryContainer(categoryKey, category);
  }

  function createCategoryContainer(categoryKey, category) {
    const categoryContainer = document.createElement('div');
    categoryContainer.className = 'quick-responses active';
    categoryContainer.dataset.category = categoryKey;

    const categoryTitle = document.createElement('h4');
    categoryTitle.className = 'response-category-title';
    categoryTitle.textContent = category.name;

    const responseButtons = document.createElement('div');
    responseButtons.className = 'response-category-buttons';

    category.responses.forEach(response => {
      const button = document.createElement('button');
      button.className = 'quick-response-btn';
      button.textContent = response;
      button.addEventListener('click', () => {
        onResponseSelect(response);
      });
      responseButtons.appendChild(button);
    });

    categoryContainer.appendChild(categoryTitle);
    categoryContainer.appendChild(responseButtons);
    responsesContainer.appendChild(categoryContainer);
  }

  // Show first category by default
  const firstCategoryKey = Object.keys(responseCategories)[0];
  if (firstCategoryKey) {
    const firstBubble = categoryBubbles.querySelector(`[data-category="${firstCategoryKey}"]`);
    if (firstBubble) {
      firstBubble.classList.add('active');
      // Create and show the first category immediately
      createCategoryContainer(firstCategoryKey, responseCategories[firstCategoryKey]);
      showCategory(firstCategoryKey);
    }
  }

  // Add quick responses header
  const quickResponsesHeader = document.createElement('div');
  quickResponsesHeader.className = 'panel-header';
  quickResponsesHeader.innerHTML = `
    <h3>Quick Responses</h3>
    <p>Select a response to quickly reply</p>
  `;
  container.appendChild(quickResponsesHeader);

  container.appendChild(categoryBubbles);
  container.appendChild(responsesContainer);

  return {
    element: container,
    showCategory: showCategory
  };
}