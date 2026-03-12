from flask import Flask, render_template, request

app = Flask(__name__)

attempts = 0
attacks = 0
phishing_checks = 0


@app.route('/', methods=['GET','POST'])
def login():

    global attempts, attacks

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            attempts = 0
            return "Login Successful"

        else:

            attempts += 1

            ip = request.headers.get("X-Forwarded-For", request.remote_addr)

            with open("attack_log.txt","a") as file:
                file.write(ip + "\n")

            if attempts >= 3:
                attacks += 1
                return "⚠ Brute Force Attack Detected"

            return "Wrong Password"

    return render_template("login.html")


@app.route('/phishing', methods=['GET','POST'])
def phishing():

    global phishing_checks

    result = ""

    if request.method == "POST":

        phishing_checks += 1

        url = request.form["url"]

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
        attempts=attempts,
        attacks=attacks,
        phishing=phishing_checks,
        ip_logs=ip_logs
    )


@app.route('/test')
def test():
    return "Test Page Working"


if __name__ == "__main__":
    app.run(debug=True)
