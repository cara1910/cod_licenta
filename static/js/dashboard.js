const recordsBody = document.getElementById('records-body');
const recordCount = document.getElementById('record-count');
const diskUsage = document.getElementById('disk-usage');
const diskMeterFill = document.getElementById('disk-meter-fill');
const dateFilter = document.getElementById('date-filter');
const liveButton = document.getElementById('live-button');
const liveStatus = document.querySelector('.live-status');
const livePlaceholder = document.querySelector('.live-placeholder');

const sampleData = [
  { id: 1, timestamp: '2026-06-24 09:12:34', path: 'images/2026-06-24_091234.jpg', image: 'https://via.placeholder.com/140' },
  { id: 2, timestamp: '2026-06-24 11:03:18', path: 'images/2026-06-24_110318.jpg', image: 'https://via.placeholder.com/140' },
  { id: 3, timestamp: '2026-06-23 18:42:09', path: 'images/2026-06-23_184209.jpg', image: 'https://via.placeholder.com/140' },
  { id: 4, timestamp: '2026-06-23 21:20:51', path: 'images/2026-06-23_212051.jpg', image: 'https://via.placeholder.com/140' }
];

function formatDate(date) {
  return date.toISOString().slice(0, 10);
}

function updateSummary(records) {
  recordCount.textContent = records.length;
  const usage = 78;
  diskUsage.textContent = `${usage}%`;
  if (diskMeterFill) {
    diskMeterFill.style.width = `${usage}%`;
  }
}

function renderRecords(records) {
  recordsBody.innerHTML = '';
  records.forEach((record) => {
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${record.timestamp}</td>
      <td><img src="${record.image}" alt="Preview" /></td>
    `;
    recordsBody.appendChild(row);
  });
}

function applyFilter() {
  const selectedDate = dateFilter.value;
  const filtered = selectedDate
    ? sampleData.filter((item) => item.timestamp.startsWith(selectedDate))
    : sampleData;
  renderRecords(filtered);
  updateSummary(filtered);
}

function initDashboard() {
  dateFilter.value = formatDate(new Date());
  applyFilter();
}

liveButton.addEventListener('click', () => {
  liveStatus.textContent = 'Conexiune activă';
  livePlaceholder.textContent = 'Camera live este afișată aici. În modul real, conectează un stream RTSP/HTTP din server.';
  livePlaceholder.style.background = 'linear-gradient(180deg, rgba(180,75,140,0.08), rgba(180,75,140,0.18))';
});

initDashboard();
