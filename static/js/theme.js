// Theme toggle functionality
function initializeTheme() {
    console.log('Initializing theme toggle...');
    
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (!themeToggleBtn) {
        console.error('❌ Theme toggle button not found!');
        return;
    }
    
    const sunIcon = themeToggleBtn.querySelector('.fa-sun');
    const moonIcon = themeToggleBtn.querySelector('.fa-moon');
    
    if (!sunIcon || !moonIcon) {
        console.error('❌ Theme toggle icons not found!', {
            sunIcon: !!sunIcon,
            moonIcon: !!moonIcon
        });
        return;
    }
    
    const html = document.documentElement;
    
    // Function to update icon and theme
    function setTheme(isDark) {
        try {
            console.log(`🌓 Setting theme: ${isDark ? 'Dark' : 'Light'}`);
            
            // Update theme
            if (isDark) {
                html.classList.add('dark');
                themeToggleBtn.classList.add('dark');
                
                // Sun icon
                sunIcon.classList.remove('opacity-100', 'rotate-0');
                sunIcon.classList.add('opacity-0', 'rotate-90');
                
                // Moon icon
                moonIcon.classList.remove('opacity-0', 'rotate-90');
                moonIcon.classList.add('opacity-100', 'rotate-0');
            } else {
                html.classList.remove('dark');
                themeToggleBtn.classList.remove('dark');
                
                // Sun icon
                sunIcon.classList.remove('opacity-0', 'rotate-90');
                sunIcon.classList.add('opacity-100', 'rotate-0');
                
                // Moon icon
                moonIcon.classList.remove('opacity-100', 'rotate-0');
                moonIcon.classList.add('opacity-0', 'rotate-90');
            }
            
            // Save theme preference
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            
            console.log('✅ Theme updated successfully');
        } catch (error) {
            console.error('❌ Error setting theme:', error);
        }
    }

    // Set initial theme based on localStorage or system preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme === 'dark' || (!savedTheme && prefersDark);
    
    console.log('🔍 Initial theme settings:', {
        savedTheme,
        prefersDark,
        initialTheme
    });

    setTheme(initialTheme);

    // Toggle theme on click
    themeToggleBtn.addEventListener('click', () => {
        const isDark = !html.classList.contains('dark');
        setTheme(isDark);
    });

    console.log('✨ Theme toggle initialized successfully');
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', () => {
    try {
        initializeTheme();
    } catch (error) {
        console.error('❌ Error initializing theme:', error);
    }
});
