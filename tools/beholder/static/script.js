const captureButton = document.getElementById('captureButton');
const imageInput = document.getElementById('imageInput');
const promptList = document.getElementById('promptList');
const resultElement = document.getElementById('result');

captureButton.addEventListener('click', function() {
  imageInput.click(); // Trigger file input
});

imageInput.addEventListener('change', handleImageUpload);

let imageData;

function handleImageUpload(event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      imageData = e.target.result;
      displayPrompts();
    };
    reader.readAsBinaryString(file);
  }
}

function displayPrompts() {
  // Clear the current interface
  captureButton.style.display = 'none';
  promptList.innerHTML = '';
  
  // Show some prompts (replace with actual prompts you need)
  const prompts = ["Elves working", "Reticulating splines"];
  prompts.forEach(prompt => {
    const promptElement = document.createElement('div');
    promptElement.innerText = prompt;
    promptElement.className = 'button';
    promptElement.addEventListener('click', () => analyzeImage(prompt));
    promptList.appendChild(promptElement);
  });
}

function analyzeImage(prompt) {
  promptList.style.display = 'none'; // Hide the prompts
  
  fetch('http://localhost:8000/analyze_image/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/octet-stream'
    },
    body: JSON.stringify({ prompt: prompt, file: imageData })
  })
  .then(response => response.json())
  .then(data => {
    displayResult(data.response);
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

function displayResult(result) {
  resultElement.innerText = result;
  resultElement.style.display = 'block'; // Show the result
}

// This is just to demonstrate. An actual implementation would need to handle
// things like error states, user feedback during loading, re-trying, etc.
// Add your existing JavaScript code here

const analyzeButton = document.getElementById('analyzeButton');
const promptInput = document.getElementById('promptInput');
const randomWordsElement = document.getElementById('randomWords');

analyzeButton.addEventListener('click', analyzeImage);

let randomWordsTimer;

function analyzeImage() {
  if (!imageData) {
    alert('Please capture an image first.');
    return;
  }

  const prompt = promptInput.value.trim();
  if (!prompt) {
    alert('Please enter a prompt for analysis.');
    return;
  }

  analyzeButton.style.display = 'none'; // Hide the analyze button
  randomWordsElement.style.display = 'block';
  showRandomWords();

  // Assuming imageData is already populated
  fetch('http://localhost:8000/analyze_image/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ prompt: prompt, file: imageData })
  })
  .then(response => response.json())
  .then(data => {
    displayResult(data.response);
  })
  .catch(error => {
    console.error('Error:', error);
  });
}

function showRandomWords() {
  const words = ["Reticulating splines", "Elves working", "Computing possibilities", "Generating insights"];
  randomWordsTimer = setInterval(() => {
    const randomIndex = Math.floor(Math.random() * words.length);
    randomWordsElement.innerText = words[randomIndex];
  }, 2000); // Change text every 2 seconds
}

function displayResult(result) {
  clearInterval(randomWordsTimer);
  randomWordsElement.style.display = 'none';
  resultElement.innerText = result;
  resultElement.style.display = 'block'; // Show the result
}
