
(function () {

    document.querySelectorAll('.score-big[data-score]').forEach(el => {
        el.textContent = el.dataset.score || 0;
    });

    const calGrid = document.getElementById('calGrid');
    const calMonth = document.getElementById('calMonth');
    if (!calGrid || !calMonth) return;

    let logs = {};
    try { logs = JSON.parse(calGrid.dataset.logs || '{}'); } catch (e) { }

    const today = new Date();
    let viewYear = today.getFullYear();
    let viewMonth = today.getMonth();

    function buildCalendar(year, month) {
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const monthName = new Date(year, month).toLocaleString('default', { month: 'long', year: 'numeric' });
        calMonth.textContent = monthName;
        calGrid.innerHTML = '';

        for (let i = 0; i < firstDay; i++) {
            const d = document.createElement('div');
            d.className = 'cal-day other-month';
            calGrid.appendChild(d);
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const d = document.createElement('div');
            d.className = 'cal-day';
            d.textContent = day;
            const key = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const status = logs[key];
            if (status) d.classList.add(status);
            if (year === today.getFullYear() && month === today.getMonth() && day === today.getDate()) d.classList.add('today');
            calGrid.appendChild(d);
        }
    }

    buildCalendar(viewYear, viewMonth);

    document.getElementById('calPrev')?.addEventListener('click', () => {
        viewMonth--;
        if (viewMonth < 0) { viewMonth = 11; viewYear--; }
        buildCalendar(viewYear, viewMonth);
    });
    document.getElementById('calNext')?.addEventListener('click', () => {
        viewMonth++;
        if (viewMonth > 11) { viewMonth = 0; viewYear++; }
        buildCalendar(viewYear, viewMonth);
    });

})();