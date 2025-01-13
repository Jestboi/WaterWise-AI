// Farmers Theme Handling
document.addEventListener('DOMContentLoaded', function() {
    const html = document.documentElement;
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle.querySelector('i');

    function createFarmersBackground(isDark) {
        // Mevcut canvas varsa kaldır
        const existingCanvas = document.getElementById('farmers-background');
        if (existingCanvas) {
            existingCanvas.remove();
        }

        const canvas = document.createElement('canvas');
        canvas.id = 'farmers-background';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.zIndex = '-1';
        canvas.style.opacity = '0.6';
        canvas.style.pointerEvents = 'none';
        
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        // Farmers color palette
        const lightColors = ['#FF8925', '#FFA347', '#FFB669', '#FFC98B'];
        const darkColors = ['#7C2D12', '#9A3412', '#B45309', '#D97706'];
        
        const colors = isDark ? darkColors : lightColors;

        function drawFarmersPattern() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Agricultural-inspired shapes
            for (let i = 0; i < 30; i++) {
                ctx.beginPath();
                const shapeType = Math.random();
                
                if (shapeType < 0.4) {
                    // Wheat-like triangles
                    const x = Math.random() * canvas.width;
                    const y = Math.random() * canvas.height;
                    ctx.moveTo(x, y);
                    ctx.lineTo(x + Math.random() * 50, y - Math.random() * 100);
                    ctx.lineTo(x - Math.random() * 50, y - Math.random() * 100);
                } else if (shapeType < 0.7) {
                    // Crop circles
                    const x = Math.random() * canvas.width;
                    const y = Math.random() * canvas.height;
                    const radius = Math.random() * 30 + 10;
                    ctx.arc(x, y, radius, 0, Math.PI * 2);
                } else {
                    // Field-like rectangles
                    const x = Math.random() * canvas.width;
                    const y = Math.random() * canvas.height;
                    const width = Math.random() * 80;
                    const height = Math.random() * 40;
                    ctx.rect(x, y, width, height);
                }
                
                ctx.fillStyle = colors[Math.floor(Math.random() * colors.length)] + '33';
                ctx.fill();
            }

            // Soft blur and opacity
            ctx.globalAlpha = 0.6;
            ctx.filter = 'blur(40px)';
        }

        drawFarmersPattern();
        document.body.appendChild(canvas);
    }

    function toggleFarmersTheme() {
        const isDark = html.classList.toggle('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        
        // Update icon
        if (isDark) {
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
            themeIcon.classList.remove('text-yellow-500');
            themeIcon.classList.add('text-blue-400');
        } else {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
            themeIcon.classList.remove('text-blue-400');
            themeIcon.classList.add('text-yellow-500');
        }

        createFarmersBackground(isDark);
    }

    // Initial theme setup
    const savedTheme = localStorage.getItem('theme') === 'dark';
    createFarmersBackground(savedTheme);
    if (savedTheme) {
        html.classList.add('dark');
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
        themeIcon.classList.remove('text-yellow-500');
        themeIcon.classList.add('text-blue-400');
    }

    // Theme toggle event
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleFarmersTheme);
    }
});
