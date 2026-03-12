from flask import Flask, render_template, request
import os

app = Flask(__name__)

# store attempts per IP
attempts = {}
attacks = 0
phishing_checks = 0


@app.route('/', methods=['GET','POST'])
def login():

    global attacks

    if request.method == "POST":

        # get real client IP (first IP only)
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        ip = ip.split(",")[0].strip()

        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()

        # initialize counter
        if ip not in attempts:
            attempts[ip] = 0

        # success login
        if username == "admin" and password == "1234":
            attempts[ip] = 0
            return "Login Successful"

        # wrong login
        attempts[ip] += 1

        try:
            with open("attack_log.txt","a") as file:
                file.write(ip + "\n")
        except:
            pass

        # brute force detection
       if attempts[ip] >= 3:
    attempts[ip] = 0

    # increase attack counter in file
    try:
        with open("attack_count.txt", "r") as f:
            count = int(f.read().strip())
    except:
        count = 0

    count += 1

    with open("attack_count.txt", "w") as f:
        f.write(str(count))

    return "⚠ Brute Force Attack Detected"

        return f"Wrong Password (Attempt {attempts[ip]}/3)"

    return render_template("login.html")

@app.route('/phishing', methods=['GET','POST'])
def phishing():

    global phishing_checks

    result = ""

    if request.method == "POST":

        phishing_checks += 1

        url = request.form.get("url","")

        suspicious_words = ["login","verify","bank","secure","update"]

        for word in suspicious_words:
            if word in url.lower():
                result = "⚠ Phishing Website Detected"
                break
        else:
            result = "✅ Safe Website"

    return render_template("phishing.html", result=result)


@app.route('/dashboard')
def dashboard():

    try:
        with open("attack_log.txt","r") as file:
            ip_logs = file.read()
    except:
        ip_logs = "No attack logs yet"

    try:
        with open("attack_count.txt","r") as f:
            attack_count = int(f.read())
    except:
        attack_count = 0

    return render_template(
        "dashboard.html",
        attempts=sum(attempts.values()),
        attacks=attack_count,
        phishing=phishing_checks,
        ip_logs=ip_logs
    )
