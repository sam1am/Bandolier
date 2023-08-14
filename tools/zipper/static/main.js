document.getElementById('add-form').addEventListener('submit', function(event) {
    event.preventDefault();

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/add_to_timeline', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        'tag': document.getElementById('tag').value,
        'value': document.getElementById('value').value
    }));

    xhr.onload = function() {
        if (xhr.status === 200) {
            alert('Data added to timeline');
            loadTimeline();
        } else {
            alert('Failed to add data to timeline');
        }
    };
});

function loadTimeline() {
    fetch('/get_timeline')
    .then(response => response.json())
    .then(data => {
        let timeline = document.getElementById('timeline').getElementsByTagName('tbody')[0];

        timeline.innerHTML = ''; // Clear previous entries
        data.reverse(); // Reverse the data list to display the latest entry first
        data.forEach(entry => {
            let entryRow = document.createElement('tr');

            let entryTimestamp = document.createElement('td');
            entryTimestamp.textContent = new Date(entry.timestamp).toLocaleString();
            entryRow.appendChild(entryTimestamp);

            let entryType = document.createElement('td');
            entryType.textContent = entry.type;
            entryRow.appendChild(entryType);

            let entryValue = document.createElement('td');
            entryValue.textContent = entry.value;
            entryRow.appendChild(entryValue);

            timeline.appendChild(entryRow);
            

            let deleteButton = document.createElement('button');
            // entryRow.appendChild(deleteButton);
            deleteButton.textContent = '❌'; // use any icon or emoji you want
            deleteButton.addEventListener('click', () => {
                var xhr = new XMLHttpRequest();
                xhr.open('POST', '/delete_from_timeline', true);
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.send(JSON.stringify({
                    'timestamp': entry.timestamp
                }));

                xhr.onload = function() {
                    if (xhr.status === 200) {
                        alert('Data deleted from timeline');
                        loadTimeline();
                    } else {
                        alert('Failed to delete data from timeline');
                    }
                };
            });
        });
    })
    .catch(error => console.error('Error:', error));
}





loadTimeline();
