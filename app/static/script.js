// Get elements from the DOM
const teamForm = document.getElementById('teamForm');
const searchForm = document.getElementById('searchForm');
const nextButton = document.getElementById('nextButton');
const errorMessage = document.getElementById('error'); // Element for displaying error messages

// Function to show alerts
function showAlert(message) {
    alert(message);
}

// Function to handle successful team registration and match submission
function handleTeamSubmission(data) {
    showAlert('Team registration and match result submitted successfully!');
    console.log('Updated team data:', data);
}

// Function to handle errors in both submission and searching
function handleError(error, customMessage) {
    console.error('Error:', error);
    showAlert(customMessage || 'An error occurred during the process. Please try again.');
}

// Handle team registration form submission
if (teamForm) {
    teamForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        // Get form values
        const teamName = document.getElementById('teamName').value.trim();
        const group = document.getElementById('group').value;
        const won = document.querySelector('input[name="win"]:checked');
        const kills = document.getElementById('kills').value.trim(); // Get kills input value

        // Validate form inputs before sending
        if (!teamName || !group || !won || !kills) {
            handleError(null, 'All fields must be filled out before submitting.');
            return;
        }

        // Prepare the data to send to the Flask backend
        const formData = {
            team_name: teamName,
            group: group,
            won: won.value,
            kills: kills // Include kills in the data sent
        };

        // Send a POST request to the Flask backend
        fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to submit team data');
            }
            return response.json();
        })
        .then(handleTeamSubmission)
        .catch(error => handleError(error, 'An error occurred during team registration. Please try again.'));
    });
}

// Handle Next button click to navigate to the second page
if (nextButton) {
    nextButton.addEventListener('click', function() {
        window.location.href = '/second'; // Redirect to the second page
    });
}

// Handle team search form submission on the second page
if (searchForm) {
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        const teamName = document.getElementById('searchTeamName').value.trim();

        // Check if the search input is not empty
        if (!teamName) {
            handleError(null, 'Please enter a team name to search.');
            return;
        }

        // Send a GET request to the Flask backend to check if the team exists
        fetch(`/search_team?team_name=${encodeURIComponent(teamName)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Team not found');
                }
                return response.json();
            })
            .then(data => {
                // Display team details (you can create a separate div or use existing elements to display data)
                showAlert(`Team found: ${JSON.stringify(data)}`);
                console.log('Team details:', data);
                errorMessage.textContent = ""; // Clear previous error
            })
            .catch(error => {
                console.error('Error:', error);
                errorMessage.textContent = "Team name does not exist."; // Show error
            });
    });
}

function revealWinner() {
    audio.play(); // Play background music
    let index = 0; // Index to track the current letter
    winnerElement.style.display = 'block'; // Show the winner element
    winnerElement.innerHTML = ''; // Clear previous content

    // Start confetti shower
    startConfetti();

    const typeLetter = setInterval(() => {
        if (index < winnerName.length) {
            winnerElement.innerHTML += `<span class="highlight">${winnerName[index]}</span>`;
            index++;
        } else {
            clearInterval(typeLetter); // Stop typing when done
            stopConfetti(); // Stop confetti when done
        }
    }, 500); // Adjust the interval for typing speed (500ms)
}

let canvas, context;
let particles = [];

function startConfetti() {
    canvas = document.createElement('canvas');
    document.body.appendChild(canvas);
    context = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Create particles
    for (let i = 0; i < 100; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            radius: Math.random() * 5 + 2,
            color: `hsl(${Math.random() * 360}, 100%, 50%)`,
            speed: Math.random() * 3 + 1,
            direction: Math.random() * 2 * Math.PI
        });
    }

    // Start animation
    draw();
}

function draw() {
    context.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
        context.beginPath();
        context.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        context.fillStyle = p.color;
        context.fill();
        p.x += Math.cos(p.direction) * p.speed;
        p.y += Math.sin(p.direction) * p.speed;

        // Reset particles when they go off screen
        if (p.y > canvas.height) {
            p.y = Math.random() * -100; // Reset to the top
            p.x = Math.random() * canvas.width; // Randomize x position
        }
    });
    requestAnimationFrame(draw); // Keep animating
}

function stopConfetti() {
    if (canvas) {
        document.body.removeChild(canvas); // Remove the canvas from the DOM
        particles = []; // Clear particles
        canvas = null; // Reset canvas variable
    }
}

