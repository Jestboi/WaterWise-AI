// Theme handling
document.addEventListener('DOMContentLoaded', function() {
    const html = document.documentElement;
    const themeToggle = document.getElementById('theme-toggle');
    const sunIcon = themeToggle.querySelector('.fa-sun');
    const moonIcon = themeToggle.querySelector('.fa-moon');

    // Dynamic background generation
    function createDynamicBackground(isDark) {
        const canvas = document.createElement('canvas');
        canvas.id = 'theme-background';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.zIndex = '-1';
        canvas.style.opacity = '0.5';
        canvas.style.pointerEvents = 'none';
        
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        // Color palette
        const lightColors = ['#E6F2FF', '#B3D9FF', '#80C1FF', '#4DA6FF'];
        const darkColors = ['#1A365D', '#2C5282', '#3182CE', '#4299E1'];
        
        const colors = isDark ? darkColors : lightColors;

        // Gradient and pattern generation
        function drawGradientPattern() {
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Radial gradients
            for (let i = 0; i < 10; i++) {
                const x = Math.random() * canvas.width;
                const y = Math.random() * canvas.height;
                const radius = Math.random() * 300 + 100;
                
                const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
                gradient.addColorStop(0, colors[Math.floor(Math.random() * colors.length)] + '33');
                gradient.addColorStop(1, 'transparent');
                
                ctx.fillStyle = gradient;
                ctx.beginPath();
                ctx.arc(x, y, radius, 0, Math.PI * 2);
                ctx.fill();
            }

            // Geometric shapes
            for (let i = 0; i < 20; i++) {
                ctx.beginPath();
                const shapeType = Math.random();
                
                if (shapeType < 0.33) {
                    // Triangles
                    ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);
                    ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
                    ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
                } else if (shapeType < 0.66) {
                    // Circles
                    const x = Math.random() * canvas.width;
                    const y = Math.random() * canvas.height;
                    const radius = Math.random() * 50;
                    ctx.arc(x, y, radius, 0, Math.PI * 2);
                } else {
                    // Rectangles
                    const x = Math.random() * canvas.width;
                    const y = Math.random() * canvas.height;
                    const width = Math.random() * 100;
                    const height = Math.random() * 100;
                    ctx.rect(x, y, width, height);
                }
                
                ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)] + '22';
                ctx.fill();
            }

            // Add subtle motion
            ctx.globalAlpha = 0.7;
            ctx.filter = 'blur(50px)';
        }

        drawGradientPattern();
        
        // Remove previous background if exists
        const existingBackground = document.getElementById('theme-background');
        if (existingBackground) {
            existingBackground.remove();
        }

        document.body.appendChild(canvas);
    }

    function toggleTheme() {
        if (html.classList.contains('dark')) {
            html.classList.remove('dark');
            sunIcon.classList.remove('dark:opacity-0', 'dark:rotate-[360deg]');
            sunIcon.classList.add('rotate-0');
            moonIcon.classList.remove('dark:rotate-0', 'dark:opacity-100');
            moonIcon.classList.add('rotate-90', 'opacity-0');
            localStorage.setItem('theme', 'light');
        } else {
            html.classList.add('dark');
            sunIcon.classList.add('dark:opacity-0', 'dark:rotate-[360deg]');
            sunIcon.classList.remove('rotate-0');
            moonIcon.classList.add('dark:rotate-0', 'dark:opacity-100');
            moonIcon.classList.remove('rotate-90', 'opacity-0');
            localStorage.setItem('theme', 'dark');
        }
    }

    // Initial theme setup
    const savedTheme = localStorage.getItem('theme') === 'dark';
    createDynamicBackground(savedTheme);
    if (savedTheme) {
        html.classList.add('dark');
        sunIcon.classList.add('dark:opacity-0', 'dark:rotate-[360deg]');
        sunIcon.classList.remove('rotate-0');
        moonIcon.classList.add('dark:rotate-0', 'dark:opacity-100');
        moonIcon.classList.remove('rotate-90', 'opacity-0');
    }

    // Theme toggle event
    themeToggle.addEventListener('click', () => {
        toggleTheme();
        const isDark = html.classList.contains('dark');
        createDynamicBackground(isDark);
    });

    // Resize handler
    window.addEventListener('resize', () => {
        const isDark = html.classList.contains('dark');
        createDynamicBackground(isDark);
    });
});
