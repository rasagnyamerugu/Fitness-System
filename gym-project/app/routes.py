from flask import render_template, request, redirect, url_for, jsonify, session, make_response
from flask_login import login_user, logout_user, current_user, login_required
from models import User, Persondetails, DailyLog, WorkoutLog
from app import client
from app import meal_model, le_meal, le_exercise
from datetime import date, timedelta
import random
import json

WORKOUT_PLANS = {
    "beginner": [
        {  
            "day": 1, "name": "Abs & Core", "focus": "Core Stability",
            "duration": "~35 min",
            "exercises": [
                {"name": "Plank",               "sets": 3, "reps": "1 hold", "rest": "60s"},
                {"name": "Crunches",            "sets": 3, "reps": "15",     "rest": "45s"},
                {"name": "Leg Raises",          "sets": 3, "reps": "10",     "rest": "45s"},
                {"name": "Bird-Dog",            "sets": 3, "reps": "10/side","rest": "45s"},
            ]
        },
        {   
            "day": 2, "name": "Arms & Shoulders", "focus": "Upper Body",
            "duration": "~35 min",
            "exercises": [
                {"name": "Wall Push-ups",                  "sets": 3, "reps": "10",  "rest": "45s"},
                {"name": "Dumbbell Shoulder Press (light)","sets": 3, "reps": "12",  "rest": "60s"},
                {"name": "Bicep Curls",                    "sets": 3, "reps": "12",  "rest": "45s"},
                {"name": "Arm Circles",                    "sets": 2, "reps": "15",  "rest": "30s"},
            ]
        },
        {  
            "day": 3, "name": "Rest Day", "focus": "Recovery",
            "duration": "—", "exercises": []
        },
        {   
            "day": 4, "name": "Legs & Glutes", "focus": "Lower Body",
            "duration": "~40 min",
            "exercises": [
                {"name": "Bodyweight Squats", "sets": 3, "reps": "12",     "rest": "60s"},
                {"name": "Glute Bridges",     "sets": 3, "reps": "12",     "rest": "45s"},
                {"name": "Lunges",            "sets": 3, "reps": "10/leg", "rest": "60s"},
                {"name": "Calf Raises",       "sets": 3, "reps": "15",     "rest": "30s"},
            ]
        },
        {   
            "day": 5, "name": "Cardio & HIIT", "focus": "Endurance",
            "duration": "~40 min",
            "exercises": [
                {"name": "March in Place",         "sets": 3, "reps": "30s",  "rest": "30s"},
                {"name": "Jumping Jacks",          "sets": 3, "reps": "20",   "rest": "30s"},
                {"name": "High Knees",             "sets": 3, "reps": "20",   "rest": "30s"},
                {"name": "Light Jog / Brisk Walk", "sets": 1, "reps": "10 min","rest": "—"},
            ]
        },
        {   
            "day": 6, "name": "Rest Day", "focus": "Recovery",
            "duration": "—", "exercises": []
        },
        {  
            "day": 7, "name": "Optional Active Recovery", "focus": "Mobility",
            "duration": "~20 min",
            "exercises": [
                {"name": "Gentle Stretching or Walk", "sets": 1, "reps": "20 min", "rest": "—"},
            ]
        },
    ],
    "intermediate": [
        {   
            "day": 1, "name": "Abs & Core", "focus": "Core Strength",
            "duration": "~40 min",
            "exercises": [
                {"name": "Plank",              "sets": 3, "reps": "1 hold", "rest": "60s"},
                {"name": "Bicycle Crunches",   "sets": 3, "reps": "20",     "rest": "45s"},
                {"name": "Leg Raises",         "sets": 3, "reps": "15",     "rest": "45s"},
                {"name": "Russian Twists",     "sets": 3, "reps": "20",     "rest": "45s"},
            ]
        },
        {   
            "day": 2, "name": "Arms & Shoulders", "focus": "Upper Body",
            "duration": "~45 min",
            "exercises": [
                {"name": "Push-ups",               "sets": 3, "reps": "12", "rest": "60s"},
                {"name": "Dumbbell Shoulder Press","sets": 3, "reps": "15", "rest": "60s"},
                {"name": "Bicep Curls",            "sets": 3, "reps": "15", "rest": "45s"},
                {"name": "Tricep Dips",            "sets": 3, "reps": "12", "rest": "60s"},
            ]
        },
        {   
            "day": 3, "name": "Rest Day", "focus": "Recovery",
            "duration": "—", "exercises": []
        },
        {   
            "day": 4, "name": "Legs & Glutes", "focus": "Lower Body",
            "duration": "~50 min",
            "exercises": [
                {"name": "Squats",        "sets": 3, "reps": "15",     "rest": "60s"},
                {"name": "Lunges",        "sets": 3, "reps": "12/leg", "rest": "60s"},
                {"name": "Glute Bridges", "sets": 3, "reps": "15",     "rest": "45s"},
                {"name": "Step-ups",      "sets": 3, "reps": "10/leg", "rest": "60s"},
            ]
        },
        {   
            "day": 5, "name": "Cardio & HIIT", "focus": "Endurance",
            "duration": "~45 min",
            "exercises": [
                {"name": "Warm-up Jog",      "sets": 1, "reps": "5 min",  "rest": "—"},
                {"name": "Jumping Jacks",    "sets": 4, "reps": "25",     "rest": "30s"},
                {"name": "Burpees",          "sets": 3, "reps": "10",     "rest": "60s"},
                {"name": "Mountain Climbers","sets": 3, "reps": "20",     "rest": "45s"},
                {"name": "Cool-down Jog",    "sets": 1, "reps": "5 min",  "rest": "—"},
            ]
        },
        {   
            "day": 6, "name": "Rest Day", "focus": "Recovery",
            "duration": "—", "exercises": []
        },
        {   
            "day": 7, "name": "Optional Active Recovery", "focus": "Mobility",
            "duration": "~30 min",
            "exercises": [
                {"name": "Mobility Exercises / Yoga / Light Cycling", "sets": 1, "reps": "30 min", "rest": "—"},
            ]
        },
    ],
    "advanced": [
        {   
            "day": 1, "name": "Abs & Core", "focus": "Core Power",
            "duration": "~50 min",
            "exercises": [
                {"name": "Plank",                              "sets": 3, "reps": "1 hold", "rest": "60s"},
                {"name": "Hanging Leg Raises / Captain's Chair","sets": 3, "reps": "12",    "rest": "60s"},
                {"name": "Bicycle Crunches",                   "sets": 3, "reps": "25",     "rest": "45s"},
                {"name": "Russian Twists with Weight",         "sets": 3, "reps": "20",     "rest": "45s"},
            ]
        },
        {   
            "day": 2, "name": "Arms & Shoulders", "focus": "Upper Body Strength",
            "duration": "~55 min",
            "exercises": [
                {"name": "Push-ups",                         "sets": 4, "reps": "15", "rest": "60s"},
                {"name": "Dumbbell Shoulder Press",          "sets": 4, "reps": "15", "rest": "60s"},
                {"name": "Bicep Curls (heavier)",            "sets": 4, "reps": "15", "rest": "60s"},
                {"name": "Tricep Dips / Close Grip Push-ups","sets": 3, "reps": "15", "rest": "60s"},
            ]
        },
        {   
            "day": 3, "name": "Rest Day", "focus": "Recovery",
            "duration": "—", "exercises": []
        },
        {   
            "day": 4, "name": "Legs & Glutes", "focus": "Lower Body Strength",
            "duration": "~60 min",
            "exercises": [
                {"name": "Squats with Weights",         "sets": 4, "reps": "15",     "rest": "90s"},
                {"name": "Lunges",                      "sets": 4, "reps": "12/leg", "rest": "60s"},
                {"name": "Deadlifts / Romanian Deadlift","sets": 3, "reps": "12",    "rest": "90s"},
                {"name": "Glute Bridges with Weight",   "sets": 3, "reps": "15",     "rest": "60s"},
                {"name": "Step-ups",                    "sets": 3, "reps": "15/leg", "rest": "60s"},
            ]
        },
        {   
            "day": 5, "name": "Cardio & HIIT", "focus": "Peak Conditioning",
            "duration": "~60 min",
            "exercises": [
                {"name": "Warm-up Run",                     "sets": 1, "reps": "5–10 min", "rest": "—"},
                {"name": "Jumping Jacks",                   "sets": 4, "reps": "25",       "rest": "30s"},
                {"name": "Burpees",                         "sets": 4, "reps": "12",       "rest": "60s"},
                {"name": "Mountain Climbers",               "sets": 4, "reps": "20",       "rest": "45s"},
                {"name": "Sprints / High-Intensity Intervals","sets": 1,"reps": "10 min",  "rest": "—"},
            ]
        },
        {   
            "day": 6, "name": "Rest Day", "focus": "Recovery",
            "duration": "—", "exercises": []
        },
        {   
            "day": 7, "name": "Optional Active Recovery", "focus": "Mobility",
            "duration": "~30 min",
            "exercises": [
                {"name": "Mobility / Stretching / Light Activity", "sets": 1, "reps": "30 min", "rest": "—"},
            ]
        },
    ],
}


def nocache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


def register_routes(app, db, bcrypt):
    QUOTES = [
        {"quote": "The only bad workout is the one that didn't happen.", "author": "Unknown"},
        {"quote": "Push yourself, because no one else is going to do it for you.", "author": "Unknown"},
        {"quote": "Success usually comes to those who are too busy to be looking for it.", "author": "Henry David Thoreau"},
        {"quote": "All progress takes place outside the comfort zone.", "author": "Michael John Bobak"},
        {"quote": "No matter how slow you go, you are still lapping everybody on the couch.", "author": "Unknown"},
        {"quote": "The body achieves what the mind believes.", "author": "Unknown"},
        {"quote": "Don't limit your challenges — challenge your limits.", "author": "Jerry Dunn"},
        {"quote": "Strength does not come from the body. It comes from the will of the soul.", "author": "Gandhi"},
        {"quote": "Take care of your body. It's the only place you have to live.", "author": "Jim Rohn"},
        {"quote": "The pain you feel today will be the strength you feel tomorrow.", "author": "Arnold Schwarzenegger"},
        {"quote": "Your body can stand almost anything. It's your mind that you have to convince.", "author": "Unknown"},
        {"quote": "Energy and persistence conquer all things.", "author": "Benjamin Franklin"},
        {"quote": "If you want something you've never had, you must do something you've never done.", "author": "Thomas Jefferson"},
        {"quote": "The difference between try and triumph is just a little umph!", "author": "Marvin Phillips"},
        {"quote": "Well done is better than well said.", "author": "Benjamin Franklin"},
        {"quote": "The harder the battle, the sweeter the victory.", "author": "Les Brown"},
        {"quote": "A champion is someone who gets up when they can't.", "author": "Jack Dempsey"},
        {"quote": "Fall seven times, stand up eight.", "author": "Japanese Proverb"},
        {"quote": "It's not about having time. It's about making time.", "author": "Unknown"},
        {"quote": "Discipline is the bridge between goals and accomplishment.", "author": "Jim Rohn"},
    ]

    def get_today():

        if 'test_date' in session:
            return date.fromisoformat(session['test_date'])
        return date.today()
    @app.route('/set-test-date', methods=['POST'])
    def set_test_date():
        new_date = request.form.get('date') 

        if new_date:
            session['test_date'] = new_date

        return "Test date set successfully"

    def get_daily_quote():
        today = get_today()
        index = (today.year * 365 + today.month * 31 + today.day) % len(QUOTES)
        return QUOTES[index]

    def _int(val, default=None):
        try:
            return int(val)
        except (TypeError, ValueError):
            return default

    def _float(val, default=None):
        try:
            return float(val)
        except (TypeError, ValueError):
            return default

    def _str(val, default=None):
        if val is None:
            return default
        s = str(val).strip()
        return s if s else default

    def _get_or_create_daily_log(uid, log_date_val):
        if isinstance(log_date_val, str):
            log_date_val = date.fromisoformat(log_date_val)
        log = DailyLog.query.filter_by(uid=uid, log_date=log_date_val).first()
        if not log:
            log = DailyLog(uid=uid, log_date=log_date_val)
            db.session.add(log)
            db.session.flush()
        return log

    def _get_today_workout(level):
        level = (level or "beginner").lower()
        if level not in WORKOUT_PLANS:
            level = "beginner"
        plan = WORKOUT_PLANS[level]
        day_index = get_today().weekday()
        return plan[day_index]

    def _update_streak(uid, log_date_str):
        personal = Persondetails.query.filter_by(uid=uid).first()
        if not personal:
            return

        today = date.fromisoformat(log_date_str) if isinstance(log_date_str, str) else log_date_str
        yesterday = today - timedelta(days=1)
        yesterday_log = DailyLog.query.filter_by(uid=uid, log_date=yesterday).first()

        current_streak = personal.streak or 0

        if current_streak == 0:
            new_streak = 1
        elif yesterday_log and yesterday_log.post_submitted:
            new_streak = current_streak + 1
        else:
            new_streak = 1

        personal.streak = new_streak
        if new_streak > (personal.best_streak or 0):
            personal.best_streak = new_streak

    def _generate_consistency_score(uid):

        personal = Persondetails.query.filter_by(uid=uid).first()
        if not personal:
            return 0, "No profile found."

        today = get_today()
        thirty_days_ago = today - timedelta(days=30)
        logs = DailyLog.query.filter(
            DailyLog.uid == uid,
            DailyLog.log_date >= thirty_days_ago
        ).all()

        total_days = 30
        sessions_done = sum(1 for l in logs if l.post_submitted)
        rest_days = sum(1 for l in logs if not l.post_submitted and not l.pre_submitted)
        missed = total_days - sessions_done - rest_days
        avg_water = (
            sum(l.pre_water_intake or 0 for l in logs if l.pre_water_intake) /
            max(1, sum(1 for l in logs if l.pre_water_intake))
        )
        avg_steps = (
            sum(l.steps or 0 for l in logs if l.steps) /
            max(1, sum(1 for l in logs if l.steps))
        )
        avg_rating = (
            sum(l.post_rating or 0 for l in logs if l.post_rating) /
            max(1, sum(1 for l in logs if l.post_rating))
        )
        streak = personal.streak or 0
        best_streak = personal.best_streak or 0

        prompt = f"""
You are a fitness analytics assistant for GymTracker app.
Based on the data below, compute a Consistency Score from 0 to 100 and give brief,
motivating feedback (2-3 sentences max). Respond ONLY with valid JSON in this exact format:
{{"score": <integer 0-100>, "feedback": "<2-3 sentence motivating feedback>"}}

User data (last 30 days):
- Workout sessions completed: {sessions_done} / {total_days}
- Current streak: {streak} days
- Best streak: {best_streak} days
- Average water intake: {avg_water:.1f} / 12 glasses
- Average daily steps: {avg_steps:.0f}
- Average session rating: {avg_rating:.1f} / 10
- Level: {personal.level or 'beginner'}
- Goal: {personal.goal or 'general fitness'}

Weigh workout frequency (40%), streak (25%), water intake (15%), steps (10%), session quality (10%).
"""
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a fitness data analyst. Respond only with the JSON asked."},
                    {"role": "user",   "content": prompt}
                ]
            )
            raw = completion.choices[0].message.content.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw)
            score    = max(0, min(100, int(parsed.get("score", 0))))
            feedback = parsed.get("feedback", "Keep pushing — every session counts!")
        except Exception as e:
            print("[ConsistencyScore error]", e)
            score = min(100, int((sessions_done / total_days) * 100))
            feedback = "Keep pushing — every session counts!"

        personal.consistency_score    = score
        personal.consistency_feedback = feedback
        personal.score_updated_date   = today.isoformat()
        return score, feedback

    def _generate_session_feedback(daily_log, personal):
        try:
            uid = daily_log.uid
            thirty_ago = (get_today() - timedelta(days=30)).isoformat()
            recent_logs = DailyLog.query.filter(
                DailyLog.uid == uid,
                DailyLog.log_date >= thirty_ago,
                DailyLog.post_submitted == True
            ).order_by(DailyLog.log_date.desc()).all()

            def avg(vals):
                vals = [v for v in vals if v is not None]
                return sum(vals) / len(vals) if vals else None

            hist_energy   = avg([l.pre_energy_level for l in recent_logs])
            hist_sleep    = avg([l.pre_sleep_hours   for l in recent_logs])
            hist_rating   = avg([l.post_rating       for l in recent_logs])
            hist_fatigue  = avg([l.post_fatigue      for l in recent_logs])
            hist_duration = avg([l.post_duration     for l in recent_logs])
            hist_steps    = avg([l.steps             for l in recent_logs])

            energy_trend = "stable"
            last7  = [l.pre_energy_level for l in recent_logs[:7]  if l.pre_energy_level]
            prior7 = [l.pre_energy_level for l in recent_logs[7:14] if l.pre_energy_level]
            if last7 and prior7:
                diff = (sum(last7)/len(last7)) - (sum(prior7)/len(prior7))
                energy_trend = "improving" if diff > 0.4 else "declining" if diff < -0.4 else "stable"

            
            injury_days = sum(
                1 for l in recent_logs
                if l.pre_injuries and l.pre_injuries.strip()
                and l.pre_injuries.lower() not in ('none', 'no', 'n/a', '-', '')
            )

            sessions_count = len(recent_logs)

            
            if sessions_count > 0:
                history_block = f"""
30-Day History ({sessions_count} sessions logged):
- Avg energy level   : {f'{hist_energy:.1f}/10' if hist_energy else 'N/A'}
- Avg sleep          : {f'{hist_sleep:.1f} hrs' if hist_sleep else 'N/A'}
- Avg session rating : {f'{hist_rating:.1f}/10' if hist_rating else 'N/A'}
- Avg fatigue        : {f'{hist_fatigue:.1f}/10' if hist_fatigue else 'N/A'}
- Avg duration       : {f'{hist_duration:.0f} min' if hist_duration else 'N/A'}
- Avg daily steps    : {f'{hist_steps:.0f}' if hist_steps else 'N/A'}
- Energy trend (7-day vs prior 7): {energy_trend}
- Sessions with reported injuries: {injury_days}"""
            else:
                history_block = "30-Day History: This is their first ever logged session!"

            def s(val, fallback="unknown"):
                return val if val is not None else fallback

            prompt = f"""
You are GymTracker AI Coach — a knowledgeable, warm, motivating personal fitness coach.

STRICT RULES:
1. Write exactly 3-5 sentences as a flowing paragraph. NO bullet points, NO headers.
2. Reference at least ONE specific number from today's session.
3. If history data exists, mention ONE pattern or trend you noticed from it.
4. Give ONE practical tip tailored to their goal and today's data.
5. Add ONE genuine motivational line — not generic. Make it feel personal.
6. If fatigue >= 7 OR injuries are reported today, include a recovery/rest reminder.
7. If today's energy <= 4 OR sleep <= 5, acknowledge the low energy and validate the effort.
8. If this is their first session ever, give a warm welcome instead of history insight.
9. Never use phrases like "Keep it up!" or "Great job!" alone — be more specific.

USER PROFILE:
- Name            : {s(personal.name)}
- Age             : {s(personal.age)} yrs  |  Gender: {s(personal.gender)}
- Height          : {s(personal.height)} cm  |  Weight: {s(personal.weight)} kg
- Goal Weight     : {s(personal.goal_weight)} kg
- Fitness Goal    : {s(personal.goal)}
- Level           : {s(personal.level)}
- Goes to Gym     : {s(personal.going_to_gym)}
- Activity Level  : {s(personal.activity_level)}
- Session Length  : {s(personal.session_len)}
- Waist           : {s(personal.waist)} cm  |  Body Fat: {s(personal.body_fat)}%
- Resting HR      : {s(personal.heart_rate)} bpm

TODAY'S SESSION ({daily_log.log_date}):
Pre-workout:
- Energy level  : {s(daily_log.pre_energy_level)}/10
- Sleep         : {s(daily_log.pre_sleep_hours)} hrs
- Water (pre)   : {s(daily_log.pre_water_intake)}/12 glasses
- Mood          : {s(daily_log.pre_mood)}
- Injuries      : {daily_log.pre_injuries or 'none reported'}

Post-workout:
- Duration      : {s(daily_log.post_duration)} min
- Calories      : {s(daily_log.post_calories)}
- Session Rating: {s(daily_log.post_rating)}/10
- Fatigue       : {s(daily_log.post_fatigue)}/10
- Completion    : {s(daily_log.post_completion)}
- Steps today   : {daily_log.steps or 0}

Streak & Consistency:
- Current streak: {s(personal.streak, 0)} days
- Best streak   : {s(personal.best_streak, 0)} days
- Consistency score: {s(personal.consistency_score, 0)}/100

{history_block}

Now write the personalised coaching feedback paragraph:"""

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": (
                        "You are GymTracker AI Coach. Write warm, specific, insight-driven fitness feedback. "
                        "Always write as a flowing paragraph — no bullet points, no headers. "
                        "Speak directly to the user using 'you' and 'your'."
                    )},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.75,
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print("[SessionFeedback error]", e)
            return "Great work completing your session today! Keep up the consistency — every rep counts toward your goal."



    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'GET':
            return render_template('signup.html')
        name     = request.form.get('name')
        username = request.form.get('username')
        email    = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password)
        if User.query.filter(User.username == username).first():
            return render_template("signup.html", alert=True)
        user = User(username=username, password=hashed_password, email=email, name=name)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('setup'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template("login.html")
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(User.username == username).first()
        if user:
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('home'))
            return render_template("login.html", alert=True, message="Incorrect password, try again.")
        return render_template("login.html", alert=True, message="Incorrect username, try again.")

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        session.clear()
        response = make_response(redirect(url_for('index')))
        response.delete_cookie('session')
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    @app.route('/setup')
    def setup():
        return render_template('setup.html')

    @app.route('/api/setup-profile', methods=['POST'])
    def api_setup_profile():
        data         = request.get_json(silent=True) or {}
        name         = data.get('name')
        weight       = data.get('weight')
        height       = data.get('height')
        goal_weight  = data.get('goal_weight')
        age          = data.get('age')
        level        = data.get('level')
        going_to_gym = data.get('going_to_gym')
        gender       = data.get('gender')
        goal         = data.get('goal')

        def _norm_gym(v):
            v = _str(v)
            if not v:
                return None
            v = v.lower()
            return "yes" if v in ("yes", "y", "true", "1") else "no" if v in ("no", "n", "false", "0") else v

        def _norm_goal(v):
            v = _str(v)
            if not v:
                return None
            v = v.lower()
            return {
                "lose_weight": "lose",
                "build_muscle": "muscle",
                "improve_endurance": "endurance",
                "maintain_tone": "maintain",
                "sport_performance": "sport",
            }.get(v, v)

        user = current_user
        persondetails = Persondetails(
            user=user,
            age=age,
            name=name,
            weight=weight,
            goal_weight=goal_weight,
            going_to_gym=_norm_gym(going_to_gym),
            level=level,
            height=height,
            gender=gender,
            goal=_norm_goal(goal)
        )
        db.session.add(persondetails)
        db.session.commit()
        return jsonify({"status": "success", "redirect": url_for('home')})


    @app.after_request
    def apply_nocache_to_protected(response):
        if current_user.is_authenticated:
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    @app.route("/home")
    @login_required
    def home():
        quote   = get_daily_quote()
        today_dt = get_today()
        today   = today_dt.isoformat()
        uid     = current_user.uid
        personal = current_user.personal

        daily_log = DailyLog.query.filter_by(uid=uid, log_date=today_dt).first()

     
        level   = (personal.level if personal else None) or "beginner"
        workout = _get_today_workout(level)

        completed_sets = {}
        if workout["exercises"]:
            wlogs = WorkoutLog.query.filter_by(uid=uid, log_date=today_dt).all()
            for wl in wlogs:
                key = wl.exercise_name
                if key not in completed_sets:
                    completed_sets[key] = set()
                completed_sets[key].add(wl.set_index)

        streak = (personal.streak if personal else 0) or 0
        best_streak = (personal.best_streak if personal else 0) or 0

        consistency_score    = (personal.consistency_score if personal else 0) or 0
        consistency_feedback = (personal.consistency_feedback if personal else None) or "Complete your first session to generate your score!"

        thirty_ago = get_today() - timedelta(days=30)
        month_logs = DailyLog.query.filter(
            DailyLog.uid == uid,
            DailyLog.log_date >= thirty_ago
        ).all()
        sessions_this_month = sum(1 for l in month_logs if l.post_submitted)
        missed_days = max(0, 30 - sessions_this_month - sum(1 for l in month_logs if not l.post_submitted and not l.pre_submitted))

        week_start = today_dt - timedelta(days=today_dt.weekday())
        week_data  = []
        for i in range(7):
            d = week_start + timedelta(days=i)
            d_str = d.isoformat()
            dlog = DailyLog.query.filter_by(uid=uid, log_date=d).first()
            if d > today_dt:
                status = "future"
                height = 0
            elif dlog and dlog.post_submitted:
                status = "today" if d == today_dt else "active"
                height = min(100, max(30, (dlog.post_rating or 5) * 10))
            elif dlog and dlog.pre_submitted:
                status = "today" if d == today_dt else "partial"
                height = 20
            elif d == today_dt:
                status = "today"
                height = 10
            else:
                plan_day = WORKOUT_PLANS.get(level, WORKOUT_PLANS["beginner"])[d.weekday()]
                if plan_day["name"] in ("Rest Day", "Optional Active Recovery"):
                    status = "rest"
                    height = 10
                else:
                    status = "missed"
                    height = 5
            week_data.append({
                "label": ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][d.weekday()],
                "date": d_str,
                "status": status,
                "height": height
            })

        water_today = (daily_log.pre_water_intake if daily_log else 0) or 0
        # Steps today
        steps_today = (daily_log.steps if daily_log else 0) or 0

      
        session_feedback = (daily_log.llm_feedback if daily_log else None)

        week_logs = [l for l in DailyLog.query.filter(
            DailyLog.uid == uid,
            DailyLog.log_date >= week_start,
            DailyLog.log_date <= today_dt
        ).all()]
        weekly_sessions = sum(1 for l in week_logs if l.post_submitted)
        weekly_calories = sum(l.post_calories or 0 for l in week_logs)
        weekly_duration = sum(l.post_duration or 0 for l in week_logs)
        weekly_duration_fmt = f"{weekly_duration // 60}h {weekly_duration % 60}m" if weekly_duration >= 60 else f"{weekly_duration}m"

        return render_template(
            "home.html",
            quote={"text": quote["quote"], "author": quote["author"]},
            show_chatbot=False,
          
            workout=workout,
            completed_sets=completed_sets,
          
            streak=streak,
            best_streak=best_streak,
          
            consistency_score=consistency_score,
            consistency_feedback=consistency_feedback,
            sessions_this_month=sessions_this_month,
            missed_days=missed_days,
           
            week_data=week_data,
            weekly_sessions=weekly_sessions,
            weekly_calories=weekly_calories,
            weekly_duration_fmt=weekly_duration_fmt,
          
            pre_submitted=(daily_log.pre_submitted if daily_log else False),
            post_submitted=(daily_log.post_submitted if daily_log else False),
           
            water_today=water_today,
            steps_today=steps_today,
           
            session_feedback=session_feedback,
          
            daily_log=daily_log,
            today=today,
        )


    @app.route("/api/daily-quote")
    @login_required
    def api_daily_quote():
        refresh = request.args.get("refresh", "0") == "1"
        if refresh:
            daily = get_daily_quote()
            pool  = [q for q in QUOTES if q["quote"] != daily["quote"]]
            chosen = random.choice(pool)
        else:
            chosen = get_daily_quote()
        return jsonify({"quote": chosen["quote"], "author": chosen["author"]})


    @app.route("/api/pre-modal", methods=["POST"])
    @login_required
    def api_pre_workout():
        data = request.get_json(silent=True) or {}
        today_dt = get_today()
        today_str = today_dt.isoformat()
        uid = current_user.uid

        
        if data.get('_water_only'):
            log = _get_or_create_daily_log(uid, today_dt)
            log.pre_water_intake = _int(data.get('water_intake'), log.pre_water_intake or 0)
            db.session.commit()
            return jsonify({"status": "ok", "water_today": log.pre_water_intake})


        existing = DailyLog.query.filter_by(uid=uid, log_date=today_dt).first()
        if existing and existing.pre_submitted:
            return jsonify({"status": "already_submitted", "message": "Pre-workout already logged for today."})

        log = _get_or_create_daily_log(uid, today_dt)
        log.pre_submitted    = True
        log.pre_workout_type = _str(data.get("workout_type"))
        log.pre_energy_level = _int(data.get("energy_level"))
        log.pre_sleep_hours  = _int(data.get("sleep_hours"))
        log.pre_water_intake = _int(data.get("water_intake"))
        log.pre_mood         = _str(data.get("mood"))
        log.pre_injuries     = _str(data.get("notes"))
        log.pre_time         = _str(data.get("time"))

        db.session.commit()
        return jsonify({
            "status": "ok",
            "message": "Pre-workout check-in saved.",
            "water_today": log.pre_water_intake or 0
        })



    @app.route("/api/post-modal", methods=["POST"])
    @login_required
    def api_post_workout():
        data = request.get_json(silent=True) or {}
        today_dt = get_today()
        today_str = today_dt.isoformat()
        uid = current_user.uid

        existing = DailyLog.query.filter_by(uid=uid, log_date=today_dt).first()
        if existing and existing.post_submitted:
            return jsonify({"status": "already_submitted", "message": "Post-workout already logged for today."})

        log = _get_or_create_daily_log(uid, today_dt)
        log.post_submitted  = True
        log.post_duration   = _int(data.get("duration"))
        log.post_calories   = _int(data.get("calories"))
        log.post_rating     = _int(data.get("rating"))
        log.post_fatigue    = _int(data.get("fatigue"))
        log.post_completion = _str(data.get("completion"))

        db.session.flush()


        _update_streak(uid, today_dt)

    
        personal = current_user.personal
        feedback = _generate_session_feedback(log, personal)
        log.llm_feedback = feedback

       
        score, consistency_feedback = _generate_consistency_score(uid)

        db.session.commit()

        streak = (personal.streak if personal else 1) or 1
        return jsonify({
            "status": "ok",
            "message": "Session logged successfully.",
            "feedback": feedback,
            "streak": streak,
            "consistency_score": score,
            "consistency_feedback": consistency_feedback
        })



    @app.route("/api/steps", methods=["POST"])
    @login_required
    def api_steps():
        data = request.get_json(silent=True) or {}
        today_dt = get_today()
        uid = current_user.uid
        steps = _int(data.get("steps"), 0)

        log = _get_or_create_daily_log(uid, today_dt)
        log.steps = steps
        db.session.commit()
        return jsonify({"status": "ok", "steps": steps})


    @app.route("/api/workout-set", methods=["POST"])
    @login_required
    def api_workout_set():
        data = request.get_json(silent=True) or {}
        today_dt = get_today()
        uid = current_user.uid
        exercise_name = _str(data.get("exercise"))
        set_index     = _int(data.get("set_index"))
        completed     = bool(data.get("completed", True))

        if exercise_name is None or set_index is None:
            return jsonify({"status": "error", "message": "Missing exercise or set_index"}), 400

        existing = WorkoutLog.query.filter_by(
            uid=uid, log_date=today_dt,
            exercise_name=exercise_name, set_index=set_index
        ).first()

        if completed:
            if not existing:
                wl = WorkoutLog(
                    uid=uid, log_date=today_dt,
                    exercise_name=exercise_name, set_index=set_index,
                    completed=True
                )
                db.session.add(wl)
        else:
            if existing:
                db.session.delete(existing)

        db.session.commit()
        return jsonify({"status": "ok", "completed": completed})



    @app.route('/chatbot-api', methods=['POST'])
    @login_required
    def chatbot_api():
        data       = request.get_json(silent=True) or {}
        user_input = data.get("message", "").strip()
        context    = data.get("context", "").strip()
        if not context:
            return jsonify({"reply": "I couldn't read the page content. Please refresh and try again."})

        prompt = f"""
        You are a helpful gym assistant for GymTracker website.
        Answer ONLY using this page content:
        {context}

        If the answer is not in the content, say:
        "I can only answer questions about this page's content."

        Question: {user_input}
        """
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful gym assistant. Only answer based on the given page context."},
                {"role": "user",   "content": prompt}
            ]
        )
        return jsonify({"reply": completion.choices[0].message.content})


    @app.route("/home/profile")
    @login_required
    def profile():
        return render_template("profile.html", show_chatbot=False)

    @app.route("/home/arms_shoulder")
    @login_required
    def arms_shoulder():
        return render_template("arms_shoulder.html", show_chatbot=True)

    @app.route("/home/legs_glutes")
    @login_required
    def legs_glutes():
        return render_template("legs_glutes.html", show_chatbot=True)

    @app.route("/home/abs_core")
    @login_required
    def abs_core():
        return render_template("abs_core.html", show_chatbot=True)

    @app.route("/home/cardio_hit")
    @login_required
    def cardio_hit():
        return render_template("cardio_hit.html", show_chatbot=True)

    @app.route("/home/nutrition")
    @login_required
    def nutrition():
        personal = current_user.personal

     
        user_gender = (personal.gender if personal else None) or ""
        user_goal   = (personal.goal   if personal else None) or ""

        bmi_category = ""
        if personal and personal.weight and personal.height:
            bmi = personal.weight / ((personal.height / 100) ** 2)
            if bmi < 18.5:
                bmi_category = "Underweight"
            elif bmi < 25:
                bmi_category = "Normal weight"
            elif bmi < 30:
                bmi_category = "Overweight"
            else:
                bmi_category = "Obesity"

        return render_template(
            "nutrition.html",
            show_chatbot=True,
            user_gender=user_gender,
            user_goal=user_goal,
            bmi_category=bmi_category,
            genders=["Male", "Female"],
            goals=["muscle_gain", "fat_burn"],
            bmi_categories=["Underweight", "Normal weight", "Overweight", "Obesity"],
            exercise_schedules=[
                "Light weightlifting, Yoga, and 2000 steps walking",
                "Moderate cardio, Strength training, and 5000 steps walking",
                "High-intensity interval training (HIIT), Cardio, and 8000 steps walking",
                "Low-impact cardio, Swimming, and 10000 steps walking",
            ],
        )


    @app.route("/api/predict-meal-plan", methods=["POST"])
    @login_required
    def api_predict_meal_plan():
        data = request.get_json(silent=True) or {}

        gender            = _str(data.get("gender"))
        goal              = _str(data.get("goal"))
        bmi_category      = _str(data.get("bmi_category"))
        exercise_schedule = _str(data.get("exercise_schedule"))

        if not all([gender, goal, bmi_category, exercise_schedule]):
            return jsonify({"status": "error", "message": "All fields are required."}), 400

        try:
            import pandas as pd
            input_df = pd.DataFrame([{
                "gender":            gender,
                "goal":              goal,
                "bmi_category":      bmi_category,
                "exercise_schedule": exercise_schedule,
            }])
            pred_encoded = meal_model.predict(input_df)[0]
            exercise_plan = le_exercise.inverse_transform([pred_encoded[0]])[0] if le_exercise else pred_encoded[0]
            meal_plan     = le_meal.inverse_transform([pred_encoded[1]])[0] if le_meal else pred_encoded[1]
            return jsonify({"status": "ok", "meal_plan": str(meal_plan), "exercise_plan": str(exercise_plan)})
        except Exception as e:
            print("[MealPlan prediction error]", e)
            return jsonify({"status": "error", "message": "Prediction failed. Please try again."}), 500

    @app.route("/home/progress")
    @login_required
    def progress():
        uid      = current_user.uid
        personal = current_user.personal
        today    = get_today()

       
        all_logs = DailyLog.query.filter_by(uid=uid).order_by(DailyLog.log_date.desc()).all()
        post_logs = [l for l in all_logs if l.post_submitted]

        def _avg(vals):
            vals = [v for v in vals if v is not None]
            return round(sum(vals) / len(vals), 1) if vals else 0

        total_sessions   = len(post_logs)
        total_calories   = sum(l.post_calories or 0 for l in post_logs)
        total_duration   = sum(l.post_duration or 0 for l in post_logs)
        total_duration_fmt = (
            f"{total_duration // 60}h {total_duration % 60}m"
            if total_duration >= 60 else f"{total_duration}m"
        ) if total_duration else "0m"
        avg_water_val  = _avg([l.pre_water_intake for l in all_logs if l.pre_submitted])
        avg_water_fmt  = f"{avg_water_val}/12" if avg_water_val else "—"

        
        avg_duration = int(_avg([l.post_duration for l in post_logs]))
        avg_calories = int(_avg([l.post_calories for l in post_logs]))
        avg_rating   = _avg([l.post_rating   for l in post_logs])
        avg_fatigue  = _avg([l.post_fatigue  for l in post_logs])
        avg_energy   = _avg([l.pre_energy_level for l in post_logs if l.pre_submitted or l.pre_energy_level])
        avg_sleep    = _avg([l.pre_sleep_hours  for l in post_logs if l.pre_sleep_hours])
        avg_steps    = int(_avg([l.steps for l in all_logs if l.steps]))
        avg_water    = _avg([l.pre_water_intake for l in post_logs if l.pre_water_intake])

    
        thirty_ago = today - timedelta(days=30)          
        month_logs = [l for l in all_logs if l.log_date >= thirty_ago]
        sessions_this_month = sum(1 for l in month_logs if l.post_submitted)
        missed_days = max(0, 30 - sessions_this_month - sum(
            1 for l in month_logs if not l.post_submitted and not l.pre_submitted
        ))

        
        weight_progress_pct = 0
        if personal and personal.weight and personal.goal_weight:
            
            diff_total = abs((personal.weight or 0) - (personal.goal_weight or 0))
            
            if diff_total == 0:
                weight_progress_pct = 100
            else:
                weight_progress_pct = min(100, max(0, int((1 - diff_total / max(personal.weight, personal.goal_weight, 1)) * 100)))

       
        MOOD_COLORS = {
            "energetic": "#22c55e",
            "happy":     "#fbbf24",
            "neutral":   "#3b82f6",
            "tired":     "#a855f7",
            "stressed":  "#ef4444",
        }
        mood_counts = {}
        for l in post_logs:
            if l.pre_mood:
                mood_counts[l.pre_mood] = mood_counts.get(l.pre_mood, 0) + 1
        mood_data = []
        for mood, count in sorted(mood_counts.items(), key=lambda x: -x[1]):
            pct = round(count / total_sessions * 100) if total_sessions else 0
            mood_data.append({
                "label": mood.capitalize(),
                "count": count,
                "pct":   pct,
                "color": MOOD_COLORS.get(mood, "#555"),
            })

       
        WTYPE_COLORS = [
            "var(--accent)", "#3b82f6", "#22c55e",
            "#a855f7", "#fbbf24", "#fb7185",
        ]
        wtype_counts = {}
        for l in post_logs:
            if l.pre_workout_type:
                wtype_counts[l.pre_workout_type] = wtype_counts.get(l.pre_workout_type, 0) + 1
        workout_type_data = []
        for idx, (wtype, count) in enumerate(sorted(wtype_counts.items(), key=lambda x: -x[1])):
            pct = round(count / total_sessions * 100) if total_sessions else 0
            workout_type_data.append({
                "name":  wtype,
                "count": count,
                "pct":   pct,
                "color": WTYPE_COLORS[idx % len(WTYPE_COLORS)],
            })

        
        logs_by_date = {l.log_date: l for l in all_logs}  # keys are date objects
        level = (personal.level if personal else None) or "beginner"
        heatmap_data = []
        for offset in range(29, -1, -1):
            d     = today - timedelta(days=offset)          # date object
            log   = logs_by_date.get(d)                     # look up by date object
            if d > today:
                status = "future"
            elif log and log.post_submitted:
                status = "active"
            elif log and log.pre_submitted:
                status = "partial"
            else:
                plan_day = WORKOUT_PLANS.get(level, WORKOUT_PLANS["beginner"])[d.weekday()]
                status = "rest" if plan_day["name"] in ("Rest Day", "Optional Active Recovery") else "missed"
            heatmap_data.append({
                "date":   d.isoformat(),                    # string only for display in template
                "status": status,
                "rating": log.post_rating if log and log.post_submitted else None,
            })

        
        DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        recent_sessions = []
        for l in post_logs[:15]:
            d = l.log_date
            recent_sessions.append({
                "day_name":    DAY_NAMES[d.weekday()],
                "date_fmt":    d.strftime("%d %b"),
                "workout_type": l.pre_workout_type,
                "duration":    l.post_duration,
                "calories":    l.post_calories,
                "rating":      l.post_rating,
                "fatigue":     l.post_fatigue,
                "completion":  l.post_completion,
            })

        
        today = get_today()
        week_dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
        week_logs = DailyLog.query.filter(
            DailyLog.uid == current_user.uid,
            DailyLog.log_date >= week_dates[0],
            DailyLog.log_date <= week_dates[-1]
        ).all()
        log_map = {l.log_date: l for l in week_logs}
        week_data = []
        for d in week_dates:
            log = log_map.get(d)
            status = "missed"
            if log:
                if log.post_submitted:
                    status = "active"
                elif log.pre_submitted:
                    status = "partial"
                else:
                    status = "rest"
            week_data.append({
                "date":   d.strftime("%Y-%m-%d"),
                "day":    d.strftime("%a"),
                "num":    d.day,
                "status": status,
            })

        
        calendar_logs = DailyLog.query.filter_by(uid=current_user.uid).all()
        calendar_data = {}
        for log in calendar_logs:
            key = log.log_date.strftime("%Y-%m-%d")
            if log.post_submitted:
                calendar_data[key] = "active"
            elif log.pre_submitted:
                calendar_data[key] = "partial"
            else:
                calendar_data[key] = "missed"
        return render_template(
            "progress.html",
            show_chatbot=True,
            personal=personal,
         
            total_sessions=total_sessions,
            total_calories=total_calories,
            total_duration_fmt=total_duration_fmt,
            avg_water_fmt=avg_water_fmt,
            
            avg_duration=avg_duration,
            avg_calories=avg_calories,
            avg_rating=avg_rating,
            avg_fatigue=avg_fatigue,
            avg_energy=avg_energy,
            avg_sleep=avg_sleep,
            avg_steps=avg_steps,
            avg_water=avg_water,
            
            sessions_this_month=sessions_this_month,
            missed_days=missed_days,
            
            weight_progress_pct=weight_progress_pct,
            
            mood_data=mood_data,
            workout_type_data=workout_type_data,
            
            heatmap_data=heatmap_data,
           
            recent_sessions=recent_sessions,
            week_data=week_data,
            calendar_data=calendar_data
        )

    @app.route('/secert')
    @login_required
    def secert():
        return 'secret message ;>'

    
    @app.route('/profile/save', methods=['POST'])
    @login_required
    def profile_save():
        data = request.get_json(silent=True)
        if not data:
            return jsonify(success=False, error='No data received'), 400

        try:
            name = _str(data.get('first_name'))
            if name:
                current_user.name = name
            email = _str(data.get('email'))
            if email:
                current_user.email = email

            personal = current_user.personal
            if personal is None:
                personal = Persondetails(uid=current_user.uid)
                db.session.add(personal)

            age_val = data.get('age')
            if age_val != '' and age_val is not None:
                personal.age = _int(age_val)
            elif age_val == '':
                personal.age = None

            personal.gender = data.get('gender') or personal.gender or 'male'

            weight_val = data.get('weight')
            if weight_val != '' and weight_val is not None:
                personal.weight = _int(weight_val)
            elif weight_val == '':
                personal.weight = None

            gw_val = data.get('goal_weight')
            if gw_val != '' and gw_val is not None:
                personal.goal_weight = _int(gw_val)
            elif gw_val == '':
                personal.goal_weight = None

            height_val = data.get('height')
            if height_val != '' and height_val is not None:
                personal.height = _int(height_val)
            elif height_val == '':
                personal.height = None

            waist_val = data.get('waist')
            if waist_val != '' and waist_val is not None:
                personal.waist = _float(waist_val)
            elif waist_val == '':
                personal.waist = None

            bf_val = data.get('body_fat')
            if bf_val != '' and bf_val is not None:
                personal.body_fat = _float(bf_val)
            elif bf_val == '':
                personal.body_fat = None

            personal.phone = _str(data.get('phone'))
            personal.dob   = _str(data.get('dob'))

            level = _str(data.get('level'))
            if level:
                personal.level = level

            gym_val = data.get('going_to_gym')
            gym_val = _str(gym_val)
            if gym_val:
                gym_val = gym_val.lower()
            if gym_val in ('yes', 'no'):
                personal.going_to_gym = gym_val

            hr_val = data.get('heart_rate')
            if hr_val != '' and hr_val is not None:
                personal.heart_rate = _int(hr_val)
            elif hr_val == '':
                personal.heart_rate = None

            al_val = data.get('activity_level')
            if al_val != '' and al_val is not None:
                personal.activity_level = _float(al_val)

            sl_val = _str(data.get('session_len'))
            if sl_val:
                personal.session_len = sl_val

            goal_val = _str(data.get('goal'))
            if goal_val:
                goal_val = goal_val.lower()
                personal.goal = {
                    "lose_weight": "lose",
                    "build_muscle": "muscle",
                    "improve_endurance": "endurance",
                    "maintain_tone": "maintain",
                    "sport_performance": "sport",
                }.get(goal_val, goal_val)

            db.session.commit()
            return jsonify(success=True)

        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, error=str(e)), 500

   

    @app.route('/profile/reset-progress', methods=['POST'])
    @login_required
    def reset_progress():
        try:
            uid = current_user.uid

           
            DailyLog.query.filter_by(uid=uid).delete()
            WorkoutLog.query.filter_by(uid=uid).delete()

           
            personal = current_user.personal
            if personal:
                personal.streak               = 0
                personal.best_streak          = 0
                personal.consistency_score    = 0
                personal.consistency_feedback = None
                personal.score_updated_date   = None

            db.session.commit()
            return jsonify(success=True)

        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, error=str(e)), 500

   

    @app.route('/profile/delete-account', methods=['POST'])
    @login_required
    def delete_account():
        try:
            user = current_user._get_current_object()
            logout_user()
            session.clear()
            db.session.delete(user)
            db.session.commit()
            return jsonify(success=True, redirect=url_for('index'))
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, error=str(e)), 500