import os
import uuid

from flask import Flask, render_template, redirect, url_for, flash, abort
from werkzeug.utils import secure_filename

from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user
)

from models import db, University, User
from forms import PublicUniversityForm, EditUniversityForm, LoginForm, RegisterForm


app = Flask(__name__)


app.config["SECRET_KEY"] = "secretkey"


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.root_path, "instance", "site.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "images", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024 

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_folders():  
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    path = app.config["UPLOAD_FOLDER"]

    if os.path.exists(path) and not os.path.isdir(path):
        raise RuntimeError(
            f"'{path}' არსებობს როგორც ფაილი, არა როგორც ფოლდერი. "
            f"წაშალე/გადაარქვი და შექმენი ფოლდერი: {path}"
        )

    os.makedirs(path, exist_ok=True)


def admin_required():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def seed_data_if_empty():
    """
    თუ ბაზა ცარიელია:
    - შექმნას admin user
    - შექმნას 10 უნივერსიტეტი (approved=True)
    """
    if User.query.count() == 0:
        admin = User(username="admin", password="admin123", is_admin=True)
        db.session.add(admin)
        db.session.commit()

    if University.query.count() == 0:

        default_image = "default_uni.jpg"

        seeds = [
            ("თბილისის სახელმწიფო უნივერსიტეტი", "საქართველოს პირველი და ერთ-ერთი ყველაზე პრესტიჟული სახელმწიფო უნივერსიტეტი, რომელიც დაარსდა 1918 წელს. ის მდებარეობს თბილისში და მნიშვნელოვან როლს ასრულებს ქვეყნის საგანმანათლებლო და სამეცნიერო განვითარებაში. თსუ აერთიანებს მრავალ ფაკულტეტს, მათ შორის ჰუმანიტარულ, ზუსტ და საბუნებისმეტყველო მეცნიერებებს, იურიდიულ, ეკონომიკისა და მედიცინის მიმართულებებს. უნივერსიტეტი გამოირჩევა ძლიერი აკადემიური ტრადიციებით, კვალიფიციური პროფესორ-მასწავლებლებითა და აქტიური სტუდენტური ცხოვრებით, ხოლო მისი კურსდამთავრებულები მნიშვნელოვან წვლილს იძლევიან საქართველოს მეცნიერებაში, პოლიტიკაში, კულტურასა და საზოგადოებრივ ცხოვრებაში.", default_image, "https://www.tsu.ge/"),
            ("საქართველოს ტექნიკური უნივერსიტეტი", "ერთ-ერთი ყველაზე დიდი და წამყვანი სახელმწიფო უნივერსიტეტი, რომელიც სპეციალიზებულია ინჟინერიაში, ტექნოლოგიებსა და ზუსტ მეცნიერებებში. უნივერსიტეტი დაარსდა 1922 წელს და მდებარეობს თბილისში. იგი ამზადებს სპეციალისტებს ისეთ სფეროებში, როგორიცაა ინჟინერია, არქიტექტურა, ინფორმაციული ტექნოლოგიები, ენერგეტიკა, ტრანსპორტი, მშენებლობა და ეკონომიკა. ტექნიკური უნივერსიტეტი გამოირჩევა პრაქტიკულ სწავლებაზე ორიენტაციით, ლაბორატორიული მუშაობითა და ტექნიკურ-ინდუსტრიულ მიმართულებებთან კავშირით, ხოლო მისი კურსდამთავრებულები მოთხოვნადები არიან როგორც საქართველოში, ისე უცხოეთში.", default_image, "https://gtu.ge/"),
            ("ილიას სახელმწიფო უნივერსიტეტი", "თანამედროვე და სწრაფად განვითარებადი სახელმწიფო უნივერსიტეტი საქართველოში, რომელიც დაარსდა 2006 წელს. ის მდებარეობს თბილისში და გამოირჩევა ინოვაციური სწავლების მიდგომებით, კვლევაზე ორიენტირებული გარემოთი და საერთაშორისო სტანდარტებთან შესაბამისი პროგრამებით. უნივერსიტეტი სთავაზობს სტუდენტებს მრავალ მიმართულებას, მათ შორის სოციალურ და ჰუმანიტარულ მეცნიერებებს, ბიზნესს, სამართალს, განათლებას, საბუნებისმეტყველო და ზუსტ მეცნიერებებს. ილიას უნივერსიტეტი განსაკუთრებულ ყურადღებას აქცევს აკადემიურ თავისუფლებას, კრიტიკულ აზროვნებასა და პრაქტიკულ ცოდნას, რის გამოც იგი პოპულარული არჩევანია აქტიური და მოტივირებული ახალგაზრდებისთვის..", default_image, "https://iliauni.edu.ge/ge"),
            ("თავისუფალი უნივერსიტეტი", "ერთ-ერთი ყველაზე ძლიერი და პრესტიჟული კერძო უნივერსიტეტი საქართველოში, რომელიც გამოირჩევა მაღალი აკადემიური სტანდარტებითა და დასავლურ საგანმანათლებლო მოდელზე დაფუძნებული სწავლებით. უნივერსიტეტი მდებარეობს თბილისში და განსაკუთრებულ ყურადღებას უთმობს კრიტიკულ აზროვნებას, დამოუკიდებელ მუშაობასა და პრაქტიკულ ცოდნას. თავისუფალი უნივერსიტეტი განსაკუთრებით ცნობილია ბიზნესის, ეკონომიკის, სამართლის, საერთაშორისო ურთიერთობებისა და კომპიუტერული მეცნიერებების მიმართულებებით. სწავლა მოითხოვს მაღალ შრომისმოყვარეობას, თუმცა კურსდამთავრებულები გამოირჩევიან კონკურენტუნარიანობით და წარმატებით აგრძელებენ კარიერას როგორც საქართველოში, ისე საზღვარგარეთ..", default_image, ""),
            ("აგრარული უნივერსიტეტი", "თანამედროვე კერძო უნივერსიტეტი, რომელიც სპეციალიზებულია აგრარულ, საბუნებისმეტყველო და გამოყენებით მეცნიერებებში. უნივერსიტეტი მდებარეობს თბილისში და გამოირჩევა პრაქტიკულ განათლებაზე ორიენტაციით, თანამედროვე ლაბორატორიებითა და საერთაშორისო სტანდარტებთან შესაბამისი პროგრამებით. აქ სწავლება მიმდინარეობს ისეთ მიმართულებებზე, როგორიცაა აგრონომია, ვეტერინარია, კვების ტექნოლოგიები, ბიოტექნოლოგია, გარემოს დაცვა და ბიზნესის აგრარული მიმართულებები. აგრარული უნივერსიტეტი აქტიურად თანამშრომლობს საერთაშორისო პარტნიორებთან და სტუდენტებს აძლევს შესაძლებლობას მიიღონ რეალურ პრაქტიკაზე დაფუძნებული ცოდნა, რაც მათ კონკურენტუნარიანებს ხდის შრომის ბაზარზე.", default_image, "https://agruni.edu.ge/ge/"),
            ("თბილისის სამედიცინო უნივერსიტეტი", "საქართველოს მთავარი და ყველაზე ავტორიტეტული სახელმწიფო უნივერსიტეტი სამედიცინო განათლების სფეროში. მისი ისტორია იწყება 1918 წლიდან და დღეს იგი ამზადებს მაღალკვალიფიციურ ექიმებს, სტომატოლოგებს, ფარმაცევტებსა და საზოგადოებრივი ჯანმრთელობის სპეციალისტებს. უნივერსიტეტი გამოირჩევა ძლიერი თეორიული ბაზით, კლინიკურ პრაქტიკაზე ორიენტირებული სწავლებითა და მრავალ პროფილურ საუნივერსიტეტო კლინიკასთან თანამშრომლობით. თბილისის სახელმწიფო სამედიცინო უნივერსიტეტი პოპულარულია როგორც ქართველ, ისე უცხოელ სტუდენტებს შორის და მისი დიპლომი აღიარებულია საერთაშორისო დონეზე.", default_image, "https://tsmu.edu/ts/"),
        ]

        for name, desc, img, link in seeds:
            db.session.add(
                University(
                    name=name,
                    description=desc,
                    image=img,
                    link=link,
                    approved=True
                )
            )
        db.session.commit()



@app.before_request
def init_app_once():
    ensure_folders()
    with app.app_context():
        db.create_all()

        try:
 
            _ = db.session.execute(db.text("SELECT approved FROM university LIMIT 1")).fetchone()
        except Exception:
  
            try:
                db.session.execute(db.text("ALTER TABLE university ADD COLUMN approved BOOLEAN NOT NULL DEFAULT 1"))
                db.session.commit()
            except Exception:
                pass

        seed_data_if_empty()

@app.route("/")
def index():

    if current_user.is_authenticated and current_user.is_admin:
        universities = University.query.order_by(University.id.asc()).all()
    else:
        universities = University.query.filter_by(approved=True).order_by(University.id.asc()).all()

    return render_template("index.html", universities=universities)


@app.route("/university/<int:uid>")
def university(uid):
    uni = University.query.get_or_404(uid)

   
    if not uni.approved:
        if not (current_user.is_authenticated and current_user.is_admin):
            abort(404)

    return render_template("university.html", uni=uni)


@app.route("/add-university", methods=["GET", "POST"])
def add_university_public():
    form = PublicUniversityForm()

    if form.validate_on_submit():
        file = form.image.data

        if not file or not file.filename:
            flash("ფოტო აუცილებელია.", "danger")
            return render_template("add_university.html", form=form)

        if not allowed_file(file.filename):
            flash("მხოლოდ png/jpg/jpeg/webp ფორმატებია დაშვებული.", "danger")
            return render_template("add_university.html", form=form)

        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(save_path)

        new_uni = University(
            name=form.name.data,
            description=form.description.data,
            image=unique_filename,
            link=form.link.data,
            approved=False
        )
        db.session.add(new_uni)
        db.session.commit()

        flash("გმადლობთ! უნივერსიტეტი გაიგზავნა და გამოჩნდება მას შემდეგ, რაც ადმინი დაადასტურებს.", "success")
        return redirect(url_for("index"))

    return render_template("add_university.html", form=form)


@app.route("/admin/pending")
@login_required
def pending_universities():
    admin_required()
    pendings = University.query.filter_by(approved=False).order_by(University.id.desc()).all()
    return render_template("admin_pending.html", pendings=pendings)


@app.route("/admin/approve/<int:uid>", methods=["POST"])
@login_required
def approve_university(uid):
    admin_required()
    uni = University.query.get_or_404(uid)
    uni.approved = True
    db.session.commit()
    flash("უნივერსიტეტი დადასტურდა და გამოჩნდა მთავარ გვერდზე.", "success")
    return redirect(url_for("pending_universities"))


@app.route("/admin/reject/<int:uid>", methods=["POST"])
@login_required
def reject_university(uid):
    admin_required()
    uni = University.query.get_or_404(uid)


    if uni.image and uni.image not in ["default_uni.jpg", "default_uni.png", "default_uni.jpeg"]:
        img_path = os.path.join(app.config["UPLOAD_FOLDER"], uni.image)
        if os.path.exists(img_path):
            os.remove(img_path)

    db.session.delete(uni)
    db.session.commit()
    flash("უნივერსიტეტი უარყოფილია და წაიშალა.", "warning")
    return redirect(url_for("pending_universities"))



@app.route("/edit-university/<int:uid>", methods=["GET", "POST"])
@login_required
def edit_university(uid):
    admin_required()

    uni = University.query.get_or_404(uid)
    form = EditUniversityForm(obj=uni)

    if form.validate_on_submit():
        uni.name = form.name.data
        uni.description = form.description.data
        uni.link = form.link.data

        file = form.image.data
        if file and file.filename and file.filename.strip() != "":
            if not allowed_file(file.filename):
                flash("მხოლოდ png/jpg/jpeg/webp ფორმატებია დაშვებული.", "danger")
                return render_template("edit_university.html", form=form, uni=uni)

            if uni.image and uni.image not in ["default_uni.jpg", "default_uni.png", "default_uni.jpeg"]:
                old_path = os.path.join(app.config["UPLOAD_FOLDER"], uni.image)
                if os.path.exists(old_path):
                    os.remove(old_path)

            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
            file.save(save_path)
            uni.image = unique_filename

        db.session.commit()
        flash("ცვლილებები შენახულია (Admin).", "success")
        return redirect(url_for("university", uid=uni.id))

    return render_template("edit_university.html", form=form, uni=uni)


@app.route("/delete-university/<int:uid>", methods=["POST"])
@login_required
def delete_university(uid):
    admin_required()

    uni = University.query.get_or_404(uid)

    if uni.image and uni.image not in ["default_uni.jpg", "default_uni.png", "default_uni.jpeg"]:
        img_path = os.path.join(app.config["UPLOAD_FOLDER"], uni.image)
        if os.path.exists(img_path):
            os.remove(img_path)

    db.session.delete(uni)
    db.session.commit()
    flash("უნივერსიტეტი წაიშალა (Admin).", "success")
    return redirect(url_for("index"))



@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data).first()

        if u and u.password == form.password.data:
            login_user(u)
            flash("შესვლა წარმატებულია.", "success")
            return redirect(url_for("index"))

        flash("არასწორი მომხმარებელი ან პაროლი.", "danger")

    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("ასეთი მომხმარებელი უკვე არსებობს.", "danger")
            return render_template("register.html", form=form)

        u = User(username=form.username.data, password=form.password.data, is_admin=False)
        db.session.add(u)
        db.session.commit()

        flash("რეგისტრაცია წარმატებულია. ახლა შეგიძლია შესვლა.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
