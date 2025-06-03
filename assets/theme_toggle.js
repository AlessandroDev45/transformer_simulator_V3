window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.clientside = {
    toggleTheme: function(n_clicks_theme) {
        const lightThemeClass = 'theme-light';
        const iconComponentId = 'theme-toggle-icon'; // Assuming this is the ID of your icon component
        const textComponentId = 'theme-toggle-text'; // Assuming this is the ID of your text component

        let currentTheme = document.body.classList.contains(lightThemeClass) ? 'light' : 'dark';
        
        // On initial load (n_clicks_theme is undefined or null for the first call if not persisted)
        // Or if triggered by something other than a direct click (e.g. page load with persisted state)
        if (n_clicks_theme === undefined || n_clicks_theme === null) {
            const storedTheme = localStorage.getItem('theme');
            if (storedTheme) {
                currentTheme = storedTheme;
            }
            // Apply initial theme based on stored or default (dark)
            if (currentTheme === 'light') {
                document.body.classList.add(lightThemeClass);
            } else {
                document.body.classList.remove(lightThemeClass);
            }
        } else { // Theme toggle on click
            if (currentTheme === 'light') {
                document.body.classList.remove(lightThemeClass);
                currentTheme = 'dark';
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.add(lightThemeClass);
                currentTheme = 'light';
                localStorage.setItem('theme', 'light');
            }
        }

        let newIconClassName, newButtonText;
        if (currentTheme === 'light') {
            newIconClassName = 'fas fa-moon'; // Show moon icon (to switch to dark)
            newButtonText = ' Escuro';
        } else {
            newIconClassName = 'fas fa-sun';   // Show sun icon (to switch to light)
            newButtonText = ' Claro';
        }
        
        // This function in Dash clientside_callback needs to return values for Outputs
        // The order of returned values must match the order of Output() in Python
        // Example: Output("theme-toggle-icon", "className"), Output("theme-toggle-text", "children")
        // The actual update of the icon and text components will be handled by Dash
        // based on what this JS function returns.
        // We need to ensure the Python callback definition matches this.
        // For now, this JS function will return the new class for the icon and new text.
        // The Dash machinery will then update the components with these IDs if they exist.
        
        // The return value should be an array where each element corresponds to an Output.
        // If there are two Outputs (icon className, text children), it returns [newIconClassName, newButtonText]
        return [newIconClassName, newButtonText];
    }
};
