from flask import Flask, render_template, request
import requests

app = Flask(__name__)

attempts = {}
total_attempts = 0
attacks = 0
phishing_checks = 0


# IP Location function
def get_location(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = response.json()

        if data.get("status") == "success":
            country = data.get("country", "Unknown")
            city = data.get("city", "")
            return f"{city}, {country}"

        return "Unknown Location"

    except:
        return "Unknown Location"


def read_logs():
    try:
        with open("attack_log.txt","r") as file:
            return file.read()
    except:
        return "No attacker IP detected yet"


# HOME PAGE
@app.route('/')
def home():
    return render_template("home.html")


# LOGIN ATTACK TEST
@app.route('/login', methods=['GET','POST'])
def login():

    global attacks
    global total_attempts

    message = ""

    if request.method == "POST":

        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        ip = ip.split(",")[0].strip()

        username = request.form.get("username","").strip()
        password = request.form.get("password","").strip()

        if ip not in attempts:
            attempts[ip] = 0

        # Correct login (dashboard open होणार नाही)
        if username == "admin" and password == "ayush21@":
            attempts[ip] = 0
            message = "Login Successful"

        else:

            # Wrong login
            attempts[ip] += 1
            total_attempts += 1

            location = get_location(ip)

            try:
                with open("attack_log.txt","a") as file:
                    file.write(ip + " - " + location + "\n")
            except:
                pass

            if attempts[ip] >= 3:
                attacks += 1
                attempts[ip] = 0
                message = "⚠ Brute Force Attack Detected"
            else:
                message = f"Wrong Password (Attempt {attempts[ip]}/3)"

    return render_template("login.html", message=message)


# PHISHING SCANNER
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

@app.route('/admin', methods=['GET','POST'])
def admin():

    message=""

    if request.method=="POST":

        username=request.form.get("username")
        password=request.form.get("password")

        if username=="admin" and password=="1234":

            return render_template(
                "dashboard.html",
                attempts=total_attempts,
                attacks=attacks,
                phishing=phishing_checks,
                ip_logs=read_logs()
            )

        else:
            message="Invalid Admin Credentials"

    return render_template("admin.html", message=message)

# DASHBOARD (Admin साठी)
@app.route('/dashboard')
def dashboard():

    return render_template(
        "dashboard.html",
        attempts=total_attempts,
        attacks=attacks,
        phishing=phishing_checks,
        ip_logs=read_logs()
    )


if __name__ == "__main__":
    app.run(debug=True)
