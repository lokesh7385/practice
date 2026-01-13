from flask import Flask, render_template, request, flash
import cv2
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'webp', 'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = "dev-key"
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(filename,operation): 
    print(f"the file name is {filename} and the operation is{operation}")
    img = cv2.imread(f"{UPLOAD_FOLDER}/{filename}")
    match operation:
        case "cgrey":
            process_image = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            new_filename = f"{UPLOAD_FOLDER}/{filename}"
            cv2.imwrite(new_filename,process_image)
            return new_filename
        case "cpng":
            new_filename = f"{UPLOAD_FOLDER}/{filename.split('.')[0]}.png'
            cv2.imwrite(new_filename,img)
            return filename
        case "cjpg":
            new_filename = f"{UPLOAD_FOLDER}/{filename.split('.')[0]}.jpg"
            cv2.imwrite(new_filename,img)
            return filename
        case "cwebp":
            new_filename = f"{UPLOAD_FOLDER}/{filename.split('.')[0]}.webp"
            cv2.imwrite(new_filename,img)
            return filename


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contacts_us")
def contacts_us():
    return render_template("contacts_us.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
        if 'file' not in request.files:
            flash('No file part')
            return render_template("index.html")

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return render_template("index.html")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            flash("Upload successful")
            new = process_image(filename,operation)
            flash(f"your file is available at <a href='/{new}'>here</a> target='_blank'")
            return render_template("index.html")


if __name__ == "__main__":
    app.run(port=5001, debug=False)
