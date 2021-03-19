function initialiseTheme() {
    if (isDarkThemeSelected()) {
        halfmoon.toggleDarkMode();
    }
}

function changeTheme() {
    if (isDarkThemeSelected()) {
        localStorage.removeItem("darkSwitch");
    } else {
        localStorage.setItem("darkSwitch", "dark");
    }

    halfmoon.toggleDarkMode();
}

function isDarkThemeSelected() {
    return (
        localStorage.getItem("darkSwitch") !== null &&
        localStorage.getItem("darkSwitch") === "dark"
    );
}

function toggleSidebar() {
    halfmoon.toggleSidebar();
}