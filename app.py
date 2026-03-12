from flask import Flask, render_template, request

app = Flask(__name__)

attempts = {}
total_attempts = 0
attacks = 0
phishing_checks = 0


@app.route('/', methods=['GET','POST'])
def login():

    global attacks
    global total_attempts

    if request.method == "POST":

        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        ip = ip.split(",")[0].strip()

        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()

        if ip not in attempts:
            attempts[ip] = 0

        if username == "admin" and password == "1234":
            attempts[ip] = 0
            return "Login Successful"

        attempts[ip] += 1
        total_attempts += 1

        try:
            with open("attack_log.txt","a") as file:
                file.write(ip + "\n")
        except:
            pass

        if attempts[ip] >= 3:
            attacks += 1
            attempts[ip] = 0
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

    return render_template(
        "dashboard.html",
        attempts=total_attempts,
        attacks=attacks,
        phishing=phishing_checks,
        ip_logs=ip_logs
    )
