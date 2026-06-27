(function () {

    const menuBtn = document.getElementById('menu-btn');
    if (menuBtn) {
        menuBtn.addEventListener('click', () => document.body.classList.toggle('sidebar-open'));
    }

    const wrapper = document.getElementById('avatarWrapper');
    const btn = document.getElementById('avatarBtn');
    if (btn) {
        btn.addEventListener('click', e => { e.stopPropagation(); wrapper.classList.toggle('open'); });
        document.addEventListener('click', e => { if (!wrapper.contains(e.target)) wrapper.classList.remove('open'); });
    }

    const streakEl = document.getElementById('streak-count');
    if (streakEl) {
        const v = parseInt(streakEl.dataset.streak, 10);
        streakEl.textContent = isNaN(v) ? 0 : v;
    }


    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {

        const saved = localStorage.getItem('theme');
        if (saved === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
            themeBtn.setAttribute('aria-label', 'Switch to dark mode');
            themeBtn.innerHTML = iconSun();
        } else {
            themeBtn.setAttribute('aria-label', 'Switch to light mode');
            themeBtn.innerHTML = iconMoon();
        }

        themeBtn.addEventListener('click', () => {
            const isLight = document.documentElement.getAttribute('data-theme') === 'light';
            if (isLight) {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'dark');
                themeBtn.setAttribute('aria-label', 'Switch to light mode');
                themeBtn.innerHTML = iconMoon();
            } else {
                document.documentElement.setAttribute('data-theme', 'light');
                localStorage.setItem('theme', 'light');
                themeBtn.setAttribute('aria-label', 'Switch to dark mode');
                themeBtn.innerHTML = iconSun();
            }
        });
    }

    function iconMoon() {
        return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
        </svg>`;
    }

    function iconSun() {
        return `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"/>
            <line x1="12" y1="1" x2="12" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/>
            <line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>`;
    }

})();