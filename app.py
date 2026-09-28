from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

SCENARIOS = [
    {
        "id": 1,
        "sender": "security-alert@example-training.com",
        "subject": "Urgent: Your Account Requires Verification",
        "body": (
            "We detected unusual activity on your account. "
            "Please review the message carefully and determine whether "
            "the email should be trusted."
        ),
        "red_flags": [
            "Urgent language",
            "Unexpected security warning",
            "Sender address should be verified"
        ]
    },
    {
        "id": 2,
        "sender": "hr-notice@example-training.com",
        "subject": "Important: Employee Document Review",
        "body": (
            "A document has been shared with you for review. "
            "Before opening links or attachments, verify the sender "
            "and the context of the request."
        ),
        "red_flags": [
            "Unexpected document request",
            "Sender identity should be verified",
            "Do not open unknown attachments"
        ]
    },
    {
        "id": 3,
        "sender": "support@example-training.com",
        "subject": "Your Password Will Expire Soon",
        "body": (
            "Your account password may require attention. "
            "Review the sender and message details before taking any action."
        ),
        "red_flags": [
            "Password-related urgency",
            "Unexpected account notification",
            "Verify through an official channel"
        ]
    }
]


def save_response(scenario_id, answer):
    os.makedirs("data", exist_ok=True)
    file_path = "data/responses.csv"

    file_exists = os.path.exists(file_path)

    with open(file_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["scenario_id", "answer"])

        writer.writerow([scenario_id, answer])


@app.route("/")
def index():
    return render_template("index.html", scenarios=SCENARIOS)


@app.route("/scenario/<int:scenario_id>")
def scenario(scenario_id):
    selected = next(
        (item for item in SCENARIOS if item["id"] == scenario_id),
        None
    )

    if selected is None:
        return redirect(url_for("index"))

    return render_template("email.html", scenario=selected)


@app.route("/result/<int:scenario_id>", methods=["POST"])
def result(scenario_id):
    selected = next(
        (item for item in SCENARIOS if item["id"] == scenario_id),
        None
    )

    if selected is None:
        return redirect(url_for("index"))

    answer = request.form.get("answer", "")
    save_response(scenario_id, answer)

    correct = answer == "phishing"

    return render_template(
        "result.html",
        scenario=selected,
        answer=answer,
        correct=correct
    )

@app.route("/dashboard")
def dashboard():
    file_path = "data/responses.csv"

    total = 0
    correct = 0

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                total += 1

                if row["answer"].lower() == "phishing":
                    correct += 1

    score = round((correct / total) * 100) if total else 0

    return render_template(
        "dashboard.html",
        total=total,
        correct=correct,
        score=score
    )
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
