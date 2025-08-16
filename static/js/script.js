const container = document.getElementById('detections');
const socket = io();

async function fetchDetections() {
  try {
    const res = await fetch('/detections');
    const data = await res.json();
    renderDetections(data);
  } catch (err) {
    console.error("Failed to fetch detections:", err);
  }
}

function renderDetections(detections) {
  container.innerHTML = '';
  detections.reverse().forEach(d => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <img src="${d.image}" alt="Detection Image" />
      <h3>${d.label} (${(d.confidence * 100).toFixed(1)}%)</h3>
      <h3>${d.timestamp}</h3>
      <p>${d.msg}</p>
    `;
    container.appendChild(card);
  });
}

socket.on('new_detection', fetchDetections);
fetchDetections();