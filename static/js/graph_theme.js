// Graph Theme Handling
document.addEventListener('DOMContentLoaded', function() {
    const html = document.documentElement;
    const themeToggle = document.getElementById('theme-toggle');

    function updateChartTheme() {
        const isDark = html.classList.contains('dark');
        const charts = [
            { id: 'lineChart', config: getLineChartConfig(isDark) },
            { id: 'barChart', config: getBarChartConfig(isDark) },
            { id: 'radarChart', config: getRadarChartConfig(isDark) },
            { id: 'pieChart', config: getPieChartConfig(isDark) }
        ];

        charts.forEach(chart => {
            const chartInstance = Chart.getChart(chart.id);
            if (chartInstance) {
                chartInstance.data = chart.config.data;
                chartInstance.options = chart.config.options;
                chartInstance.update();
            }
        });
    }

    function getLineChartConfig(isDark) {
        return {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Sales Growth',
                    data: [12, 19, 3, 5, 2, 3],
                    borderColor: isDark ? '#60A5FA' : '#3B82F6',
                    backgroundColor: isDark ? 'rgba(96, 165, 250, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: isDark ? '#E5E7EB' : '#374151'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: isDark ? '#E5E7EB' : '#374151' },
                        grid: { color: isDark ? 'rgba(229, 231, 235, 0.1)' : 'rgba(55, 65, 81, 0.1)' }
                    },
                    y: {
                        ticks: { color: isDark ? '#E5E7EB' : '#374151' },
                        grid: { color: isDark ? 'rgba(229, 231, 235, 0.1)' : 'rgba(55, 65, 81, 0.1)' }
                    }
                }
            }
        };
    }

    function getBarChartConfig(isDark) {
        return {
            type: 'bar',
            data: {
                labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
                datasets: [{
                    label: 'Color Preference',
                    data: [12, 19, 3, 5, 2, 3],
                    backgroundColor: isDark 
                        ? ['rgba(248, 113, 113, 0.6)', 'rgba(96, 165, 250, 0.6)', 'rgba(253, 224, 71, 0.6)', 
                           'rgba(52, 211, 153, 0.6)', 'rgba(167, 139, 250, 0.6)', 'rgba(251, 146, 60, 0.6)']
                        : ['rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)', 'rgba(255, 206, 86, 0.6)', 
                           'rgba(75, 192, 192, 0.6)', 'rgba(153, 102, 255, 0.6)', 'rgba(255, 159, 64, 0.6)']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: isDark ? '#E5E7EB' : '#374151'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: isDark ? '#E5E7EB' : '#374151' },
                        grid: { color: isDark ? 'rgba(229, 231, 235, 0.1)' : 'rgba(55, 65, 81, 0.1)' }
                    },
                    y: {
                        ticks: { color: isDark ? '#E5E7EB' : '#374151' },
                        grid: { color: isDark ? 'rgba(229, 231, 235, 0.1)' : 'rgba(55, 65, 81, 0.1)' }
                    }
                }
            }
        };
    }

    function getRadarChartConfig(isDark) {
        return {
            type: 'radar',
            data: {
                labels: ['Eating', 'Drinking', 'Sleeping', 'Designing', 'Coding', 'Cycling', 'Running'],
                datasets: [{
                    label: 'Personal Performance',
                    data: [65, 59, 90, 81, 56, 55, 40],
                    backgroundColor: isDark ? 'rgba(139, 92, 246, 0.2)' : 'rgba(139, 92, 246, 0.2)',
                    borderColor: isDark ? '#A78BFA' : '#8B5CF6',
                    pointBackgroundColor: isDark ? '#A78BFA' : '#8B5CF6'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: isDark ? '#E5E7EB' : '#374151'
                        }
                    }
                },
                scales: {
                    r: {
                        ticks: { 
                            color: isDark ? '#E5E7EB' : '#374151',
                            backdropColor: isDark ? '#1F2937' : '#FFFFFF'
                        },
                        grid: { color: isDark ? 'rgba(229, 231, 235, 0.1)' : 'rgba(55, 65, 81, 0.1)' },
                        pointLabels: { color: isDark ? '#E5E7EB' : '#374151' }
                    }
                }
            }
        };
    }

    function getPieChartConfig(isDark) {
        return {
            type: 'pie',
            data: {
                labels: ['Red', 'Blue', 'Yellow'],
                datasets: [{
                    label: 'Color Distribution',
                    data: [300, 50, 100],
                    backgroundColor: isDark 
                        ? ['rgba(248, 113, 113, 0.6)', 'rgba(96, 165, 250, 0.6)', 'rgba(253, 224, 71, 0.6)']
                        : ['rgba(255, 99, 132, 0.6)', 'rgba(54, 162, 235, 0.6)', 'rgba(255, 206, 86, 0.6)']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: isDark ? '#E5E7EB' : '#374151'
                        }
                    }
                }
            }
        };
    }

    // Theme toggle event
    if (themeToggle) {
        themeToggle.addEventListener('click', updateChartTheme);
    }

    // Initial theme setup
    updateChartTheme();
});
