function setErr(inputId, errId, show) {
    const el = document.getElementById(inputId);
    if (el) el.classList.toggle('invalid', show);
    document.getElementById(errId).classList.toggle('show', show);
}

document.getElementById('profileForm').addEventListener('submit', function (e) {
    e.preventDefault();
    document.getElementById('globalErr').classList.remove('show');

    const name = document.getElementById('f-name').value.trim();
    const age = parseInt(document.getElementById('f-age').value, 10);
    const gender = document.getElementById('f-gender').value;
    const height = parseFloat(document.getElementById('f-height').value);
    const weight = parseFloat(document.getElementById('f-weight').value);
    const goal_weight = parseFloat(document.getElementById('f-goal-weight').value);
    const level = document.getElementById('f-level').value;
    const going_to_gym = document.getElementById('f-gym').value;
    const goal = document.getElementById('f-goal').value;

    const checks = [
        ['f-name', 'err-name', !name],
        ['f-age', 'err-age', !age || age < 10 || age > 90],
        ['f-gender', 'err-gender', !gender],
        ['f-height', 'err-height', !height || height < 100 || height > 250],
        ['f-weight', 'err-weight', !weight || weight < 30 || weight > 300],
        ['f-goal-weight', 'err-goal-weight', !goal_weight || goal_weight < 30 || goal_weight > 300],
        ['f-level', 'err-level', !level],
        ['f-gym', 'err-gym', !going_to_gym],
        ['f-goal', 'err-goal', !goal],
    ];

    let valid = true;
    checks.forEach(([inputId, errId, isInvalid]) => {
        setErr(inputId, errId, isInvalid);
        if (isInvalid) valid = false;
    });

    if (!valid) return;

    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.classList.add('loading');

    fetch('/api/setup-profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, age, gender, height, weight, goal_weight, level, going_to_gym, goal })
    })
        .then(res => {
            if (!res.ok) throw new Error('Server error: ' + res.status);
            return res.json();
        })
        .then(data => {
            if (data.status === 'success') {
                alert('Your details have been recorded!\nIf any changes are required, you can update them anytime from your Profile page.');
                window.location.href = data.redirect;
            } else {
                throw new Error(data.message || 'Unexpected response');
            }
        })
        .catch(err => {
            console.error('Setup error:', err);
            const globalErr = document.getElementById('globalErr');
            globalErr.textContent = 'Something went wrong: ' + err.message + '. Please try again.';
            globalErr.classList.add('show');
            btn.disabled = false;
            btn.classList.remove('loading');
        });
});