hamburger.addEventListener('click', () => {
    navLinks.classList.toggle("active");
});

roomsBtn.addEventListener('click', () => {
    sidebar.classList.toggle("active");
    rightsidePanel.classList.toggle("active");
});

document.addEventListener('keydown', (event) => {
    if (event.key == 'Enter') {
        sendMessageBtn.click();
    }
});
