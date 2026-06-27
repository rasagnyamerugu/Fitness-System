
(function () {


    const quoteBtn = document.getElementById('quote-refresh-btn');
    if (quoteBtn) {
        quoteBtn.addEventListener('click', async () => {
            const res = await fetch('/api/daily-quote?refresh=1').catch(() => null);
            if (!res) return;
            const data = await res.json();
            document.getElementById('quote-text').textContent = data.quote;
            document.getElementById('quote-author').textContent = '— ' + data.author;
        });
    }


    function openModal(id) { document.getElementById(id).classList.add('open'); }
    function closeModal(id) { document.getElementById(id).classList.remove('open'); }

    document.getElementById('pre-workout-trigger')?.addEventListener('click', () => openModal('pre-modal-overlay'));
    document.getElementById('post-workout-trigger')?.addEventListener('click', () => openModal('post-modal-overlay'));

    document.querySelectorAll('[data-close-modal]').forEach(btn =>
        btn.addEventListener('click', () => closeModal(btn.dataset.closeModal))
    );
    document.querySelectorAll('.modal-overlay').forEach(overlay =>
        overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(overlay.id); })
    );


    document.querySelectorAll('input[type="range"][data-val-target]').forEach(r => {
        const el = document.getElementById(r.dataset.valTarget);
        if (el) { r.addEventListener('input', () => { el.textContent = r.value; }); el.textContent = r.value; }
    });

    const preForm = document.getElementById('pre-workout-form');
    if (preForm) {
        preForm.addEventListener('submit', async e => {
            e.preventDefault();
            const btn = preForm.querySelector('button[type="submit"]');
            btn.textContent = 'Saving…'; btn.disabled = true;
            const data = Object.fromEntries(new FormData(preForm).entries());
            const res = await fetch('/api/pre-modal', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).catch(() => null);
            const json = res ? await res.json() : null;
            if (json?.water_today !== undefined) updateWaterUI(json.water_today);
            btn.textContent = '✓ Saved!';
            const trigger = document.getElementById('pre-workout-trigger');
            if (trigger) { trigger.classList.add('submitted'); trigger.querySelector('.bar-sub').textContent = '✓ Logged for today'; }
            setTimeout(() => closeModal('pre-modal-overlay'), 900);
        });
    }


    const postForm = document.getElementById('post-workout-form');
    if (postForm) {
        postForm.addEventListener('submit', async e => {
            e.preventDefault();
            const btn = postForm.querySelector('button[type="submit"]');
            btn.textContent = 'Saving…'; btn.disabled = true;
            const data = Object.fromEntries(new FormData(postForm).entries());
            const res = await fetch('/api/post-modal', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) }).catch(() => null);
            const json = res ? await res.json() : null;
            if (json?.feedback) { document.getElementById('feedback-text').textContent = json.feedback; document.getElementById('feedback-bar')?.classList.remove('empty'); }
            if (json?.consistency_score !== undefined) {
                document.getElementById('score-num').textContent = json.consistency_score;
                document.getElementById('consistency-bar-fill').style.width = json.consistency_score + '%';
                if (json.consistency_feedback) document.getElementById('consistency-feedback-text').textContent = json.consistency_feedback;
            }
            const trigger = document.getElementById('post-workout-trigger');
            if (trigger) { trigger.classList.add('submitted'); trigger.querySelector('.bar-sub').textContent = '✓ Session logged for today'; }
            btn.textContent = '✓ Logged!';
            setTimeout(() => closeModal('post-modal-overlay'), 1000);
        });
    }



    function updateWaterUI(count) {
        const el = document.getElementById('water-count');
        if (el) el.textContent = count;
        const fill = document.getElementById('water-fill');
        if (fill) fill.style.width = Math.min(100, count / 12 * 100) + '%';
        document.querySelectorAll('.glass-btn').forEach(btn => btn.classList.toggle('filled', parseInt(btn.dataset.glass) <= count));
    }

    document.querySelectorAll('.glass-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const g = parseInt(btn.dataset.glass);
            const cur = parseInt(document.getElementById('water-count')?.textContent || '0');
            const next = cur === g ? g - 1 : g;
            updateWaterUI(next);
            await fetch('/api/pre-modal', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ water_intake: next, _water_only: true }) }).catch(() => { });
        });
    });


    document.getElementById('steps-save-btn')?.addEventListener('click', async () => {
        const input = document.getElementById('steps-input');
        const steps = parseInt(input?.value || '0');
        if (isNaN(steps) || steps < 0) return;
        document.getElementById('steps-display').textContent = steps.toLocaleString();
        document.getElementById('steps-fill').style.width = Math.min(100, steps / 10000 * 100) + '%';
        await fetch('/api/steps', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ steps }) }).catch(() => { });
    });


    document.querySelectorAll('.exercise-row').forEach(row => {
        const exName = row.dataset.exercise;
        const setDots = row.querySelectorAll('.set-dot');
        const check = row.querySelector('.ex-check');

        setDots.forEach((dot, i) => {
            dot.addEventListener('click', async () => {
                dot.classList.toggle('done');
                const allDone = row.querySelectorAll('.set-dot.done').length === setDots.length;
                row.classList.toggle('done', allDone);
                if (check) check.textContent = allDone ? '✓' : '';
                updateRing();
                await fetch('/api/workout-set', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ exercise: exName, set_index: i, completed: dot.classList.contains('done') }) }).catch(() => { });
            });
        });

        check?.addEventListener('click', async () => {
            const willDone = !row.classList.contains('done');
            row.classList.toggle('done', willDone);
            check.textContent = willDone ? '✓' : '';
            const promises = [];
            setDots.forEach((d, i) => {
                d.classList.toggle('done', willDone);
                promises.push(fetch('/api/workout-set', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ exercise: exName, set_index: i, completed: willDone }) }).catch(() => { }));
            });
            await Promise.all(promises);
            updateRing();
        });
    });

    function updateRing() {
        const done = document.querySelectorAll('.exercise-row.done').length;
        const total = document.querySelectorAll('.exercise-row').length;
        const el = document.getElementById('ring-label');
        if (el) el.textContent = done + '/' + total;
    }


    const scoreEl = document.getElementById('score-num');
    if (scoreEl) scoreEl.textContent = scoreEl.dataset.score || 0;

})();