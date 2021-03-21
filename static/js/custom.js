/**
 * Provides the functionality of the portfolio application.
 */
class PortfolioApp {
    /**
     * Get a value indicating whether the dark theme is currently selected.
     */
    get isDarkThemeSelected() {
        return (
            localStorage.getItem("darkSwitch") !== null &&
            localStorage.getItem("darkSwitch") === "dark"
        );
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
        if (this.isDarkThemeSelected) {
            halfmoon.toggleDarkMode();
        }
    }

    /**
     * Changes the application theme.
     */
    changeTheme() {
        // Only two modes are currently supported: light mode or dark mode.
        if (this.isDarkThemeSelected) {
            localStorage.removeItem("darkSwitch");
        } else {
            localStorage.setItem("darkSwitch", "dark");
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