(function () {

    const DB = window.PROFILE_DB || {};


    function selectLevel(card, silent) {
        document.querySelectorAll('.level-card').forEach(c => {
            c.classList.remove('selected');
            c.querySelector('.level-check').textContent = '';
        });
        card.classList.add('selected');
        card.querySelector('.level-check').textContent = '✓';
        document.getElementById('levelSelect').value = card.dataset.level;
    }
    window.selectLevel = selectLevel;

    function selectGoal(opt) {
        document.querySelectorAll('.goal-option').forEach(o => o.classList.remove('selected'));
        opt.classList.add('selected');
        document.getElementById('goalSelect').value = opt.dataset.goal;
    }
    window.selectGoal = selectGoal;


    function setGymToggle(val) {
        document.querySelectorAll('#gymToggle .toggle-btn').forEach(b => b.classList.remove('active'));
        document.querySelector(`#gymToggle [data-val="${val}"]`)?.classList.add('active');
    }
    window.setGymToggle = setGymToggle;

    function liveUpdate() {
        const name = document.getElementById('firstName').value.trim();
        document.getElementById('heroName').textContent = name || 'Your Name';
        document.getElementById('profileAvatar').textContent = name ? name[0].toUpperCase() : '?';

        const ageEl = document.getElementById('heroAge');
        const age = document.getElementById('age').value;
        if (ageEl) { ageEl.textContent = age ? age + ' yrs' : ''; ageEl.style.display = age ? '' : 'none'; }

        const hw = document.getElementById('heroWeight');
        if (hw) hw.textContent = document.getElementById('weight').value || '—';

        const hgw = document.getElementById('heroGoalW');
        if (hgw) hgw.textContent = document.getElementById('goalWeight').value || '—';

        calcMetrics();
    }
    window.liveUpdate = liveUpdate;

    function onHeightRange() {
        const v = document.getElementById('heightRange').value;
        document.getElementById('heightVal').textContent = v;
        const hh = document.getElementById('heroHeight');
        if (hh) hh.textContent = v;
        calcMetrics();
    }
    window.onHeightRange = onHeightRange;

    function calcMetrics() {
        const w = parseFloat(document.getElementById('weight').value) || 0;
        const h = parseFloat(document.getElementById('heightRange').value) || 0;
        const age = parseFloat(document.getElementById('age').value) || 0;
        const gw = parseFloat(document.getElementById('goalWeight').value);
        const activity = parseFloat(document.getElementById('activityLevel').value) || 1.55;
        const gender = document.getElementById('gender').value;

        const bmiEl = document.getElementById('hmBMI');
        const bmiStatus = document.getElementById('hmBMIStatus');
        const heroBMI = document.getElementById('heroBMI');

        if (w > 0 && h > 0) {
            const bmi = w / ((h / 100) ** 2);
            bmiEl.textContent = bmi.toFixed(1);
            if (heroBMI) heroBMI.textContent = bmi.toFixed(1);
            if (bmi < 18.5) { bmiStatus.textContent = 'Underweight'; bmiStatus.style.color = '#60a5fa'; }
            else if (bmi < 25) { bmiStatus.textContent = 'Normal'; bmiStatus.style.color = '#4ade80'; }
            else if (bmi < 30) { bmiStatus.textContent = 'Overweight'; bmiStatus.style.color = '#f5a623'; }
            else { bmiStatus.textContent = 'Obese'; bmiStatus.style.color = '#f87171'; }
        } else {
            bmiEl.textContent = '—'; bmiStatus.textContent = 'Enter weight & height'; bmiStatus.style.color = '';
            if (heroBMI) heroBMI.textContent = '—';
        }

        const bmrEl = document.getElementById('hmBMR');
        const tdeeEl = document.getElementById('hmTDEE');
        if (w > 0 && h > 0 && age > 0) {
            const bmr = gender === 'female'
                ? 10 * w + 6.25 * h - 5 * age - 161
                : 10 * w + 6.25 * h - 5 * age + 5;
            bmrEl.textContent = Math.round(bmr).toLocaleString();
            tdeeEl.textContent = Math.round(bmr * activity).toLocaleString();
        } else {
            bmrEl.textContent = '—'; tdeeEl.textContent = '—';
        }

        const toLoseEl = document.getElementById('hmToLose');
        const toLoseEst = document.getElementById('hmToLoseEst');
        if (w > 0 && !isNaN(gw)) {
            const diff = w - gw;
            toLoseEl.textContent = Math.abs(diff).toFixed(1) + ' kg';
            toLoseEst.textContent = diff > 0 ? '~' + Math.ceil(diff / 0.5) + ' wks est.'
                : diff < 0 ? 'Bulk: +' + Math.abs(diff).toFixed(1) + 'kg'
                    : 'Goal reached!';
        } else {
            toLoseEl.textContent = '—'; toLoseEst.textContent = '—';
        }
    }
    window.calcMetrics = calcMetrics;


    document.getElementById('saveBtn')?.addEventListener('click', () => {
        const saveBtn = document.getElementById('saveBtn');
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving…';

        const payload = {
            first_name: document.getElementById('firstName').value.trim(),
            age: document.getElementById('age').value,
            gender: document.getElementById('gender').value,
            email: document.getElementById('email').value.trim(),
            phone: document.getElementById('phone').value.trim(),
            dob: document.getElementById('dob').value,
            weight: document.getElementById('weight').value,
            goal_weight: document.getElementById('goalWeight').value,
            height: document.getElementById('heightRange').value,
            waist: document.getElementById('waist').value,
            body_fat: document.getElementById('bodyFat').value,
            level: document.getElementById('levelSelect').value,
            heart_rate: document.getElementById('heartRate').value,
            activity_level: document.getElementById('activityLevel').value,
            session_len: document.getElementById('sessionLen').value,
            going_to_gym: document.querySelector('#gymToggle .toggle-btn.active')?.dataset.val || 'no',
            goal: document.getElementById('goalSelect').value,
        };

        fetch('/profile/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        })
            .then(r => r.json())
            .then(d => {
                if (d.success) alert('Changes saved successfully!');
                else alert('Error: ' + (d.error || 'Could not save'));
            })
            .catch(() => alert('Network error. Please try again.'))
            .finally(() => { saveBtn.disabled = false; saveBtn.textContent = 'Save Changes'; });
    });


    document.getElementById('cancelBtn')?.addEventListener('click', () => {
        if (confirm('Discard all changes?')) window.location.reload();
    });


    document.getElementById('resetProgressBtn')?.addEventListener('click', () => {
        if (!confirm('Reset all progress? This cannot be undone.')) return;
        fetch('/profile/reset-progress', { method: 'POST' })
            .then(r => r.json())
            .then(d => {
                if (d.success) {
                    alert('Progress has been reset!');
                    const s = document.getElementById('streak-count');
                    if (s) s.textContent = '0';
                } else {
                    alert('Error: ' + (d.error || 'Failed to reset'));
                }
            });
    });

    document.getElementById('deleteAccountBtn')?.addEventListener('click', () => {
        if (!confirm('Delete account? This is permanent and cannot be undone.')) return;
        fetch('/profile/delete-account', { method: 'POST' })
            .then(r => r.json())
            .then(d => {
                if (d.success) window.location.href = d.redirect || '/';
                else alert('Error: ' + (d.error || 'Failed to delete account'));
            });
    });

    (function init() {
        if (DB.level) { const c = document.querySelector(`.level-card[data-level="${DB.level}"]`); if (c) selectLevel(c); }
        if (DB.going_to_gym) setGymToggle(String(DB.going_to_gym).toLowerCase());
        if (DB.goal) {
            const raw = String(DB.goal).toLowerCase();
            const normalized = ({
                lose_weight: 'lose',
                build_muscle: 'muscle',
                improve_endurance: 'endurance',
                maintain_tone: 'maintain',
                sport_performance: 'sport',
            })[raw] || raw;
            const o = document.querySelector(`.goal-option[data-goal="${normalized}"]`);
            if (o) selectGoal(o);
        }
        calcMetrics();
    })();

})();