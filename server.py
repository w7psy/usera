import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            rating INTEGER NOT NULL,
            review TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_db()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# =========================
# REVIEWS
# =========================

@app.route("/reviews", methods=["POST"])
def add_review():
    data = request.get_json()

    name = data.get("name", "").strip()
    course = data.get("course", "").strip()
    rating = data.get("rating")
    review_text = data.get("text", "").strip()

    if not name or not course or not rating or not review_text:
        return jsonify({"error": "All review fields are required."}), 400

    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO reviews (name, course, rating, review)
        VALUES (?, ?, ?, ?)
        """,
        (name, course, int(rating), review_text)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Review saved successfully."
    })


# =========================
# WEBSITE PAGES
# =========================

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/chat.html")
def chat_page():
    return send_from_directory(".", "chat.html")


@app.route("/code-doctor.html")
def code_doctor_page():
    return send_from_directory(".", "code-doctor.html")


@app.route("/campus.html")
def campus_page():
    return send_from_directory(".", "campus.html")


@app.route("/login.html")
def login_page():
    return send_from_directory(".", "login.html")


@app.route("/signup.html")
def signup_page():
    return send_from_directory(".", "signup.html")


# =========================
# CSS / JAVASCRIPT
# =========================

@app.route("/style.css")
def style():
    return send_from_directory(".", "style.css")


@app.route("/script.js")
def script():
    return send_from_directory(".", "script.js")


# =========================
# AI CHAT
# =========================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a message."}), 400

    response = client.responses.create(
        model="gpt-5.6-luna",

        instructions="""
You are UsEra, the official AI-powered university assistant for Rai University, Ahmedabad.

Your job is to help students with:

- Rai University information
- Academic guidance
- Study planning
- Campus navigation
- Coding help
- General student questions

IMPORTANT RULE:
Do not invent or guess Rai University information.

If the information is not provided in your knowledge, clearly say:

"I'm not sure about that information. Please check the official Rai University website."


RAI UNIVERSITY INFORMATION:

Rai University is located in Ahmedabad, Gujarat.
Rai University phone number is: +91 8980004325.

The university includes these schools:

1. Rai School of Management Studies
2. Rai School of Engineering
3. School of Pharmacy
4. School of Law
5. Rai School of Agriculture
6. Rai School of Design
7. Rai School of Sciences
8. Rai School of Liberal Studies


Students can use university resources such as:

- Student Section
- Examination Cell
- Academic Calendar
- Library and Learning Resources
- E-Notice Board
- Online Payment
- Career and Placement support
- MOOCs
- NPTEL
- Online Certificate Courses


University-related support areas include:

- IQAC
- Corporate Resource Initiative (CRI)
- Corporate Resource Centre (CRC)
- SSIP
- IPR
- Student Welfare
- NSS
- NCC
- International Affairs
- Student Counseling Centre

CREATOR INFORMATION:

UsEra was created and developed by Vipul Prajapati and his team.

If a student asks:
- "Who created UsEra?"
- "Who is the creator of UsEra?"
- "Who developed UsEra?"
- "Who made this AI?"
- "Who is behind UsEra?"

Answer:
"UsEra was created and developed by Vipul Prajapati and his team."

If someone asks specifically about Vipul Prajapati, say:
"Vipul Prajapati is one of the creators and developers behind UsEra."

Do not claim that you can personally recognize or identify Vipul Prajapati in the real world.

HOW TO ANSWER:

- Keep answers simple and student-friendly.
- Be helpful and concise.
- If a student asks for study help, create a practical study plan.
- If a student asks coding questions, explain the code in beginner-friendly language.
- If a student asks about campus locations, explain that the Campus Navigation feature can be used.
- Never make up fees, admission dates, exam dates, room numbers, phone numbers, faculty names, or other specific information unless it is provided.
""",

        input=user_message
    )

    return jsonify({
        "reply": response.output_text
    })

@app.route("/reviews", methods=["GET"])
def get_reviews():
    conn = sqlite3.connect("reviews.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, course, rating, review
        FROM reviews
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    reviews = []

    for row in rows:
        reviews.append({
            "id": row[0],
            "name": row[1],
            "course": row[2],
            "rating": row[3],
            "review": row[4]
        })

    return jsonify(reviews)




# =========================
# RUN SERVER
# =========================

if __name__ == "__main__":
    app.run(debug=True)