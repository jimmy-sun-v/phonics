document.addEventListener('DOMContentLoaded', async () => {
    await loadSummary();
    await loadDailyChart();
    await loadPhonemeChart();
});

async function loadSummary() {
    try {
        const resp = await fetch('/api/speech/diagnostics/summary/');
        const data = await resp.json();

        document.getElementById('totalAttempts').textContent = data.total_attempts;
        document.getElementById('avgConfidence').textContent =
            Math.round(data.avg_confidence * 100) + '%';
        document.getElementById('correctRate').textContent =
            Math.round(data.correct_rate * 100) + '%';
    } catch (err) {
        console.error('Failed to load summary:', err);
    }
}

async function loadDailyChart() {
    try {
        const resp = await fetch('/api/speech/diagnostics/daily/');
        const data = await resp.json();

        if (typeof Chart !== 'undefined') {
            new Chart(document.getElementById('dailyChart'), {
                type: 'bar',
                data: {
                    labels: data.map(d => d.day),
                    datasets: [{
                        label: 'Attempts',
                        data: data.map(d => d.attempts),
                        backgroundColor: '#4a90d9',
                        borderRadius: 4,
                    }],
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { beginAtZero: true, ticks: { stepSize: 1 } },
                    },
                },
            });
        }
    } catch (err) {
        console.error('Failed to load daily chart:', err);
    }
}

async function loadPhonemeChart() {
    try {
        const resp = await fetch('/api/speech/diagnostics/phonemes/');
        const data = await resp.json();

        if (typeof Chart !== 'undefined') {
            new Chart(document.getElementById('phonemeChart'), {
                type: 'bar',
                data: {
                    labels: data.map(d => d.phoneme),
                    datasets: [{
                        label: 'Correct Rate',
                        data: data.map(d => d.correct_rate * 100),
                        backgroundColor: '#4CAF50',
                        borderRadius: 4,
                    }],
                },
                options: {
                    responsive: true,
                    indexAxis: 'y',
                    scales: {
                        x: { min: 0, max: 100, title: { display: true, text: '%' } },
                    },
                },
            });
        }
    } catch (err) {
        console.error('Failed to load phoneme chart:', err);
    }
}
