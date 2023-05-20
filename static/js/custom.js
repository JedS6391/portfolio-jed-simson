const Themes = {
    Dark: "dark",
    Light: "light"
};

/**
 * Provides the functionality of the portfolio application.
 */
class PortfolioApp {

    /**
     * Gets the name of the current theme.
     */
    get currentTheme() {
        var currentTheme = localStorage.getItem("theme");

        // Default to dark theme.
        return currentTheme !== null ?
            currentTheme :
            Themes.Dark;
    }

    /**
     * Initialises icons in the application.
     */
    initialiseIcons() {
        feather.replace();
    }

    /**
     * Initialises the application theme.
     */
    initialiseTheme() {
        if (this.currentTheme == Themes.Dark) {
            halfmoon.toggleDarkMode();
        }
    }

    /**
     * Changes the application theme.
     */
    changeTheme() {
        // Only two modes are currently supported: light mode or dark mode.
        if (this.currentTheme == Themes.Dark) {
            localStorage.setItem("theme", Themes.Light);
        } else {
            localStorage.setItem("theme", Themes.Dark);
        }
    
        halfmoon.toggleDarkMode();
    }

    /**
     * Toggles the application sidebar.
     */
    toggleSidebar() {
        halfmoon.toggleSidebar();
    }
}