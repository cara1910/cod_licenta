import secrets
import cv2
import time

from surveillance import draw_boxes, save_event, should_save_image
from manager_stocare import cleanup_storage_if_needed
from config import DETECT_EVERY_N_FRAMES
from flask import Response
from camera import Camera
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from detection import PersonDetector

from database import (
    init_db,
    create_user,
    get_user_by_email,
    save_reset_token,
    get_user_by_reset_token,
    update_user_password
)

from email_notifier import (
    send_password_reset_email,
    send_surveillance_alert
)

app = Flask(__name__)
app.secret_key = "schimba_aceasta_cheie_secret"

init_db()

camera = Camera()
detector=PersonDetector()

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        mode = request.form.get("mode")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if mode == "register":
            if password != confirm_password:
                return render_template(
                    "index.html",
                    error="Parolele nu coincid."
                )

            username = email.split("@")[0]
            password_hash = generate_password_hash(password)

            try:
                create_user(username, email, password_hash)
                return render_template(
                    "index.html",
                    success="Cont creat cu succes. Te poți autentifica."
                )
            except Exception:
                return render_template(
                    "index.html",
                    error="Există deja un cont cu acest email."
                )

        user = get_user_by_email(email)

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["email"] = user["email"]

            return redirect(url_for("dashboard"))

        return render_template(
            "index.html",
            error="Email sau parolă incorectă."
        )

    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("home"))

    from datetime import datetime
    from database import get_detections_by_date
    from manager_stocare import get_disk_usage_percent
    from config import IMAGE_FOLDER

    selected_date = request.args.get(
        "date",
        datetime.now().strftime("%Y-%m-%d")
    )

    detections = get_detections_by_date(selected_date)
    disk_usage = get_disk_usage_percent(IMAGE_FOLDER)

    return render_template(
        "dashboard.html",
        username=session["username"],
        detections=detections,
        selected_date=selected_date,
        record_count=len(detections),
        disk_usage=round(disk_usage)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/reset-request", methods=["GET", "POST"])
def reset_request():
    if request.method == "POST":
        email = request.form.get("email")
        user = get_user_by_email(email)

        if user:
            token = secrets.token_urlsafe(32)
            expires_at = (
                datetime.now() + timedelta(minutes=30)
            ).strftime("%Y-%m-%d %H:%M:%S")

            save_reset_token(email, token, expires_at)

            reset_link = f"http://172.20.10.14:5000/reset-password/{token}"

            send_password_reset_email(email, reset_link)

        return redirect(url_for("send_link"))

    return render_template("reset-request.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password_with_token(token):
    user = get_user_by_reset_token(token)

    if not user:
        return redirect(url_for("home"))

    if not user["reset_token_expires"]:
        return redirect(url_for("home"))

    expires_at = datetime.strptime(
        user["reset_token_expires"],
        "%Y-%m-%d %H:%M:%S"
    )

    if datetime.now() > expires_at:
        return redirect(url_for("home"))

    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if new_password != confirm_password:
            return render_template(
                "reset-password.html",
                error="Parolele nu coincid."
            )

        password_hash = generate_password_hash(new_password)

        update_user_password(
            user["id"],
            password_hash
        )

        return redirect(url_for("reset_confirmation"))

    return render_template("reset-password.html")

@app.route("/send-link")
def send_link():
    return render_template("send-link.html")

@app.route("/reset-password")
def reset_password():
    return render_template("reset-password.html")


@app.route("/reset-confirmation")
def reset_confirmation():
    return render_template("reset-confirmation.html")

current_live_persons = 0


@app.route("/live")
def live():
    if "user_id" not in session:
        return redirect(url_for("home"))

    return render_template(
        "live.html",
        username=session["username"]
    )

def generate_frames():
    global current_live_persons

    frame_counter = 0
    previous_person_count = 0
    last_save_time = None
    last_boxes = []

    while True:
        frame = camera.get_frame()

        if frame is None:
            continue

        frame_counter += 1

        if frame_counter % DETECT_EVERY_N_FRAMES == 0:
            current_live_persons, last_boxes = detector.detect(frame)

            if previous_person_count == 0 and current_live_persons > 0:
                send_surveillance_alert(
                    "A fost detectată o persoană în birou."
                )

            elif current_live_persons > previous_person_count:
                difference = current_live_persons - previous_person_count

                if difference == 1:
                    send_surveillance_alert(
                        "A mai intrat o persoană în birou."
                    )
                else:
                    send_surveillance_alert(
                        f"Au mai intrat {difference} persoane în birou."
                    )

            elif previous_person_count > 0 and current_live_persons == 0:
                send_surveillance_alert(
                    "Biroul este liber. Nu mai este nicio persoană detectată."
                )

            if should_save_image(
                current_live_persons,
                previous_person_count,
                last_save_time
            ):
                frame_to_save = frame.copy()
                draw_boxes(frame_to_save, last_boxes)

                save_event(frame_to_save, current_live_persons)
                cleanup_storage_if_needed()

                last_save_time = time.time()

            if current_live_persons == 0:
                previous_person_count = 0
                last_save_time = None
            else:
                previous_person_count = current_live_persons

        draw_boxes(frame, last_boxes)

        cv2.putText(
            frame,
            f"Persoane: {current_live_persons}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        ret, buffer = cv2.imencode(".jpg", frame)

        if not ret:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() +
            b"\r\n"
        )

@app.route("/video_feed")
def video_feed():
    if "user_id" not in session:
        return redirect(url_for("home"))

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=--frame"
    )


@app.route("/live_status")
def live_status():
    if "user_id" not in session:
        return redirect(url_for("home"))

    return {
        "persons": current_live_persons
    }

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )


