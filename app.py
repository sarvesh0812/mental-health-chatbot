from flask import *
import sqlite3
from groq import Groq
import uuid
import os


import pickle
import numpy as np

# Load model
model = pickle.load(open("best_depression_model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

def predict_score(input_list):
    input_arr = np.array(input_list).reshape(1, -1)

    # scale ONLY if logistic / svm model was chosen
    try:
        input_arr = scaler.transform(input_arr)
    except:
        pass

    prediction = model.predict(input_arr)[0]
    return prediction


connection = sqlite3.connect('database.db')
cursor = connection.cursor()


from groq import Groq

client = Groq(
api_key=os.getenv("YOUR_GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": "hello"}
    ]
)

reply = response.choices[0].message.content


cursor.execute("create table if not exists user(name TEXT, email TEXT ,phone_no TEXT ,password TEXT, Age TEXT ,My_concerns TEXT, profile_pic TEXT)")

app = Flask(__name__)
chat_history = []
app.secret_key = uuid.uuid4().hex

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('mh1.html')

@app.route('/profile')
def profile():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("select * from user where email = '"+session['email']+"'")
    result = cursor.fetchone()
    return render_template('mh2.html', result=result)

@app.route('/bot')
def bot():
    return render_template('chatbot.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/result', methods=['POST'])
def result():

    # Collect answers
    answers = [int(request.form[f'question_{i}']) for i in range(1, 13)]

    # Get ML prediction
    total_score = predict_score(answers)   # <-- FIXED

    # ML-based severity levels
    if total_score <= 2:
        level = "low"
        category = "Thriving"
        result_message = "You're doing great! 🌟 Keep enjoying your life journey 🌻."
        color = "#4CAF50"

    elif total_score <= 4:
        level = "mild"
        category = "Mindful"
        result_message = "Mild concerns detected. Let's build resilience together! 😊 🌸"
        color = "#8BC34A"

    elif total_score <= 6:
        level = "moderate"
        category = "Seeking Balance"
        result_message = "Things feel heavy. You're not alone—support is here. 💕"
        color = "#FF9800"

    elif total_score <= 8:
        level = "severe"
        category = "Need Support"
        result_message = "It's a tough time. Reach out—help is available. ❤️"
        color = "#F44336"

    else:
        level = "critical"
        category = "Urgent Care"
        result_message = "Please reach out to a counselor or helpline immediately. 🩺"
        color = "#D32F2F"

    # Fetch recommendations based on severity
    communities = get_communities_by_level(level)

    return render_template(
        'result.html',
        total_score=total_score,
        result_message=result_message,
        category=category,
        level=level,
        color=color,
        communities=communities,
        max_score=10   # Because ML output max = 10
    )


def get_communities_by_level(level):
    communities = {
        "low": [
            {
                "name": "Mindful Living",
                "description": "Maintain your positive mental health",
                "platform": "Reddit: r/Mindfulness",
                "link": "https://www.reddit.com/r/Mindfulness/",
                "icon": "🌱"
            },
            {
                "name": "Positive Psychology",
                "description": "Science of happiness and wellbeing",
                "platform": "Facebook Group",
                "link": "#",
                "icon": "🧠"
            }
        ],
        "mild": [
            {
                "name": "Anxiety Support",
                "description": "Peer support for anxiety management",
                "platform": "Discord Community",
                "link": "#",
                "icon": "🤝"
            },
            {
                "name": "Mental Wellness",
                "description": "Daily tips and community support",
                "platform": "Reddit: r/MentalHealth",
                "link": "https://www.reddit.com/r/MentalHealth/",
                "icon": "💬"
            }
        ],
        "moderate": [
            {
                "name": "Depression Support",
                "description": "Safe space for sharing experiences",
                "platform": "7 Cups",
                "link": "https://www.7cups.com/",
                "icon": "🫂"
            },
            {
                "name": "Therapy Tribe",
                "description": "Professional-guided support groups",
                "platform": "Online Platform",
                "link": "https://www.therapytribe.com/",
                "icon": "🏥"
            }
        ],
        "severe": [
            {
                "name": "Crisis Support",
                "description": "Immediate help and resources",
                "platform": "Crisis Text Line",
                "link": "https://www.crisistextline.org/",
                "icon": "🚨"
            },
            {
                "name": "NAMI Support",
                "description": "National Alliance on Mental Illness",
                "platform": "Local & Online",
                "link": "https://www.nami.org/Support-Education",
                "icon": "🏛️"
            }
        ],
        "critical": [
            {
                "name": "National Suicide Prevention",
                "description": "24/7 free and confidential support",
                "platform": "Call 988",
                "link": "tel:988",
                "icon": "📞"
            },
            {
                "name": "Emergency Services",
                "description": "Immediate professional intervention",
                "platform": "Local Hospital",
                "link": "tel:911",
                "icon": "🚑"
            }
        ]
    }
    
    return communities.get(level, [])


    
@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']

        print(name, phone, email, password)
        cursor.execute("insert into user (name, phone_no, email, password) values(?,?,?,?)", [name, phone, email, password])
        connection.commit()
        return render_template('login.html')
    return render_template('login.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        
        email = request.form['email']
        password = request.form['password']

        print(email, password)
        cursor.execute("select * from user where  email=? and  password=? ", [ email, password])
        result = cursor.fetchall()
        if result:
            session['email'] = email
            return render_template("mh1.html")
        else:
            return render_template('login.html',msg="Entered wrong credentials")    
    return render_template('login.html')

@app.route('/analyse', methods=['GET', 'POST'])
def analyse():
    if request.method == 'POST':
        user_input = request.form['query']

        print(user_input)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a mental health chatbot. Answer only mental health related questions in paragraph form. If the question is unrelated to mental health, politely ask the user to ask a mental health related question."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        )

        result = response.choices[0].message.content

        print(result)

        chat_history.append([user_input, result])

        return render_template('chatbot.html', chat_history=chat_history)

    return render_template('chatbot.html')

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'email' not in session:
        return redirect('/login')

    if request.method == 'POST':

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()

        name = request.form['name']
        phone = request.form['phone']
        age = request.form['age']
        concerns = request.form.getlist('concerns')
        concerns_str = ', '.join(concerns)

        profile_pic = request.files['profile_pic']
        profile_pic_filename = None

        if profile_pic and profile_pic.filename:
            profile_pic_filename = f"static/uploads/{session['email']}.jpg"
            profile_pic.save(profile_pic_filename)

        cursor.execute("""
            UPDATE user 
            SET name=?, phone_no=?, Age=?, My_concerns=?, profile_pic=?
            WHERE email=?
        """, (name, phone, age, concerns_str, profile_pic_filename, session['email']))

        connection.commit()
        connection.close()

        return redirect('/update_profile')

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM user WHERE email = ?", (session['email'],))
    result = cursor.fetchone()
    connection.close()

    profile_pic = result[6] if result[6] else "default.png"
    
    return render_template('mh2.html', result=result, profile_pic=profile_pic)

@app.route('/hacks')
def hacks():
    return render_template('hacks.html')

@app.route('/workouts')
def workouts():
    return render_template('workout.html')

@app.route('/yoga')
def yoga():
    return render_template('yoga.html')

@app.route('/music')
def music():
    return render_template('mh3.html')

@app.route('/games')
def games():
    return render_template('game.html')


@app.route('/journaling')
def journaling():
    return render_template('journal.html')

if __name__ == "__main__":
    app.run(debug=True)