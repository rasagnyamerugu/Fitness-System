(function () {
    const formCard = document.getElementById('form-card');
    const resultsWrap = document.getElementById('results-wrap');
    const predBtn = document.getElementById('pred-btn');
    const errDiv = document.getElementById('pred-error');

    function showError(msg) { errDiv.textContent = msg; errDiv.style.display = 'block'; }
    function clearError() { errDiv.style.display = 'none'; }

    predBtn.addEventListener('click', async () => {
        clearError();

        const gender = document.getElementById('inp-gender').value;
        const goal = document.getElementById('inp-goal').value;
        const bmi = document.getElementById('inp-bmi').value;
        const exercise = document.getElementById('inp-exercise').value;

        predBtn.disabled = true;
        predBtn.textContent = 'Predicting…';

        try {
            const res = await fetch('/api/predict-meal-plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ gender, goal, bmi_category: bmi, exercise_schedule: exercise })
            });
            const data = await res.json();

            if (data.status !== 'ok') {
                showError(data.message || 'Something went wrong. Please try again.');
                return;
            }

            document.getElementById('ml-meal-text').textContent = data.meal_plan;
            document.getElementById('ml-exercise-text').textContent = data.exercise_plan || exercise;
            document.getElementById('chip-gender').textContent = gender;
            document.getElementById('chip-goal').textContent = goal.replace('_', ' ');
            document.getElementById('chip-bmi').textContent = bmi;

            formCard.style.display = 'none';
            resultsWrap.style.display = 'block';

            fetchExplanation(gender, goal, bmi, exercise, data.meal_plan, data.exercise_plan);

        } catch {
            showError('Network error. Please try again.');
        } finally {
            predBtn.disabled = false;
            predBtn.textContent = 'Get My Meal Plan';
        }
    });

    async function fetchExplanation(gender, goal, bmi, exerciseSchedule, mealPlan, exercisePlan) {
        const explainDiv = document.getElementById('ai-explain-text');
        explainDiv.textContent = '';

        const prompt = `You are GymTracker AI Coach. Explain in 3-5 warm sentences (no bullet points, no headers) why this meal plan suits this user.

User: Gender=${gender}, Goal=${goal.replace('_', ' ')}, BMI=${bmi}, Exercise=${exerciseSchedule}
Recommended Meal Plan: ${mealPlan}
Recommended Exercise: ${exercisePlan || exerciseSchedule}

Write directly to the user. Be specific about their goal and BMI. Keep it under 80 words.`;

        try {
            const res = await fetch('/chatbot-api', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: prompt, context: prompt })
            });
            const data = await res.json();
            explainDiv.textContent = data.reply || 'Unable to generate explanation.';
        } catch {
            explainDiv.textContent = 'Could not load AI explanation. Your meal plan above is still accurate.';
        }
    }

    document.getElementById('pred-reset-btn').addEventListener('click', () => {
        resultsWrap.style.display = 'none';
        formCard.style.display = 'block';
        clearError();
        document.getElementById('ai-explain-text').textContent = '';
    });
})();