# -*- coding: utf-8 -*-
import flask

import models 
import forms
from sqlalchemy import create_engine
from models import Base


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "This is secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://coe:CoEpasswd@localhost:5432/coedb"
engine = create_engine("postgresql://coe:CoEpasswd@localhost:5432/coedb")
Base.metadata.create_all(engine)


models.init_app(app)


@app.route("/")
def index():
    db = models.db
    notes = db.session.execute(
        db.select(models.Note).order_by(models.Note.title)
    ).scalars()
    return flask.render_template(
        "index.html",
        notes=notes,
    )


@app.route("/notes/create", methods=["GET", "POST"])
def notes_create():
    form = forms.NoteForm()
    if not form.validate_on_submit():
        if flask.request.method == "POST":
            print("form errors:", form.errors)
        return flask.render_template(
            "notes-create.html",
            form=form,
        )
    
    try:
        note = models.Note()
        note.title = form.title.data
        note.description = form.description.data
        note.tags = []

        db = models.db
        for tag_name in form.tags.data:
            if tag_name and tag_name.strip():  # Only process non-empty tag names
                tag = (
                    db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name.strip()))
                    .scalars()
                    .first()
                )

                if not tag:
                    tag = models.Tag(name=tag_name.strip())
                    db.session.add(tag)

                note.tags.append(tag)

        db.session.add(note)
        db.session.commit()
        
        flask.flash("สร้างโน้ตเรียบร้อยแล้ว", "success")
        return flask.redirect(flask.url_for("index"))
    except Exception as e:
        db.session.rollback()
        flask.flash(f"เกิดข้อผิดพลาดในการสร้างโน้ต: {str(e)}", "error")
        print(f"Error in notes_create: {str(e)}")
        return flask.render_template(
            "notes-create.html",
            form=form,
        )


@app.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
def notes_edit(note_id):
    db = models.db
    note = db.session.execute(
        db.select(models.Note).where(models.Note.id == note_id)
    ).scalars().first()
    
    if not note:
        flask.abort(404)
    
    if flask.request.method == "POST":
        try:
            title = flask.request.form.get("title", "").strip()
            description = flask.request.form.get("description", "").strip()
            tags_input = flask.request.form.get("tags", "").strip()
            
            if not title:
                flask.flash("กรุณากรอกชื่อโน้ต", "error")
                return flask.render_template("notes-edit.html", note=note)
            
            # Update note
            note.title = title
            note.description = description
            
            # Clear existing tags
            note.tags = []
            
            # Process tags
            if tags_input:
                tag_names = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
                for tag_name in tag_names:
                    tag = db.session.execute(
                        db.select(models.Tag).where(models.Tag.name == tag_name)
                    ).scalars().first()
                    
                    if not tag:
                        tag = models.Tag(name=tag_name)
                        db.session.add(tag)
                    
                    note.tags.append(tag)
            
            db.session.commit()
            flask.flash("แก้ไขโน้ตเรียบร้อยแล้ว", "success")
            return flask.redirect(flask.url_for("index"))
            
        except Exception as e:
            db.session.rollback()
            flask.flash(f"เกิดข้อผิดพลาด: {str(e)}", "error")
    
    return flask.render_template("notes-edit.html", note=note)


@app.route("/notes/<int:note_id>/delete", methods=["POST"])
def notes_delete(note_id):
    db = models.db
    note = db.session.execute(
        db.select(models.Note).where(models.Note.id == note_id)
    ).scalars().first()
    
    if note:
        note_title = note.title
        db.session.delete(note)
        db.session.commit()
        flask.flash(f"ลบโน้ต '{note_title}' เรียบร้อยแล้ว", "success")
    else:
        flask.flash("ไม่พบโน้ตที่ต้องการลบ", "error")
    
    return flask.redirect(flask.url_for("index"))


@app.route("/notes/delete-all", methods=["POST"])
def notes_delete_all():
    db = models.db
    try:
        # นับจำนวนโน้ตก่อนลบ
        notes_count = db.session.execute(db.select(models.Note)).scalars().all()
        count = len(notes_count)
        
        if count == 0:
            flask.flash("ไม่มีโน้ตให้ลบ", "info")
            return flask.redirect(flask.url_for("index"))
        
        # ลบ relationship ใน note_tag table ก่อน
        db.session.execute(db.delete(models.note_tag_m2m))
        
        # จากนั้นลบโน้ตทั้งหมด
        db.session.execute(db.delete(models.Note))
        
        db.session.commit()
        
        flask.flash(f"ลบโน้ตทั้งหมด {count} รายการเรียบร้อยแล้ว", "success")
    except Exception as e:
        db.session.rollback()
        flask.flash(f"เกิดข้อผิดพลาดในการลบโน้ตทั้งหมด: {str(e)}", "error")
        print(f"Error in notes_delete_all: {str(e)}")
    
    return flask.redirect(flask.url_for("index"))


@app.route("/tags")
def tags_list():
    db = models.db
    tags = db.session.execute(
        db.select(models.Tag).order_by(models.Tag.name)
    ).scalars().all()  # เพิ่ม .all() เพื่อให้ได้ list
    
    print(f"Debug: Found {len(tags)} tags")
    for tag in tags:
        print(f"Tag: {tag.name}, ID: {tag.id}")
    
    return flask.render_template(
        "tags-list.html",
        tags=tags,
    )


@app.route("/tags/<int:tag_id>/edit", methods=["GET", "POST"])
def tags_edit(tag_id):
    db = models.db
    tag = db.session.execute(
        db.select(models.Tag).where(models.Tag.id == tag_id)
    ).scalars().first()
    
    if not tag:
        flask.abort(404)
    
    if flask.request.method == "POST":
        new_name = flask.request.form.get("name", "").strip()
        
        if not new_name:
            flask.flash("กรุณากรอกชื่อ tag", "error")
            return flask.render_template("tags-edit.html", tag=tag)
        
        # Check if tag name already exists (excluding current tag)
        existing_tag = db.session.execute(
            db.select(models.Tag).where(
                models.Tag.name == new_name,
                models.Tag.id != tag_id
            )
        ).scalars().first()
        
        if existing_tag:
            flask.flash("ชื่อ tag นี้มีอยู่แล้ว", "error")
            return flask.render_template("tags-edit.html", tag=tag)
        
        try:
            tag.name = new_name
            db.session.commit()
            flask.flash("แก้ไข tag เรียบร้อยแล้ว", "success")
            return flask.redirect(flask.url_for("tags_list"))
        except Exception as e:
            db.session.rollback()
            flask.flash(f"เกิดข้อผิดพลาด: {str(e)}", "error")
    
    return flask.render_template("tags-edit.html", tag=tag)


@app.route("/tags/<int:tag_id>/delete", methods=["POST"])
def tags_delete(tag_id):
    db = models.db
    tag = db.session.execute(
        db.select(models.Tag).where(models.Tag.id == tag_id)
    ).scalars().first()
    
    if tag:
        tag_name = tag.name
        db.session.delete(tag)
        db.session.commit()
        flask.flash(f"ลบ tag '{tag_name}' เรียบร้อยแล้ว", "success")
    else:
        flask.flash("ไม่พบ tag ที่ต้องการลบ", "error")
    
    return flask.redirect(flask.url_for("tags_list"))


@app.route("/tags/delete-all", methods=["POST"])
def tags_delete_all():
    db = models.db
    try:
        # นับจำนวน tags ก่อนลบ
        tags_count = db.session.execute(db.select(models.Tag)).scalars().all()
        count = len(tags_count)
        
        if count == 0:
            flask.flash("ไม่มี tags ให้ลบ", "info")
            return flask.redirect(flask.url_for("tags_list"))
        
        # ลบ relationship ใน note_tag table ก่อน
        db.session.execute(db.delete(models.note_tag_m2m))
        
        # จากนั้นลบ tags ทั้งหมด
        db.session.execute(db.delete(models.Tag))
        
        db.session.commit()
        
        flask.flash(f"ลบ tags ทั้งหมด {count} รายการเรียบร้อยแล้ว", "success")
    except Exception as e:
        db.session.rollback()
        flask.flash(f"เกิดข้อผิดพลาดในการลบ tags ทั้งหมด: {str(e)}", "error")
        print(f"Error in tags_delete_all: {str(e)}")
    
    return flask.redirect(flask.url_for("tags_list"))


@app.route("/delete-all", methods=["POST"])
def delete_all():
    db = models.db
    try:
        # นับจำนวนข้อมูลก่อนลบ
        notes_count = len(db.session.execute(db.select(models.Note)).scalars().all())
        tags_count = len(db.session.execute(db.select(models.Tag)).scalars().all())
        
        if notes_count == 0 and tags_count == 0:
            flask.flash("ไม่มีข้อมูลให้ลบ", "info")
            return flask.redirect(flask.url_for("index"))
        
        # ลบ relationship ใน note_tag table ก่อน
        db.session.execute(db.delete(models.note_tag_m2m))
        
        # จากนั้นลบโน้ตและ tags ทั้งหมด
        db.session.execute(db.delete(models.Note))
        db.session.execute(db.delete(models.Tag))
        
        db.session.commit()
        
        flask.flash(f"ลบข้อมูลทั้งหมดเรียบร้อยแล้ว (โน้ต: {notes_count}, Tags: {tags_count})", "success")
    except Exception as e:
        db.session.rollback()
        flask.flash(f"เกิดข้อผิดพลาดในการลบข้อมูลทั้งหมด: {str(e)}", "error")
        print(f"Error in delete_all: {str(e)}")
    
    return flask.redirect(flask.url_for("index"))


@app.route("/tags/<tag_name>")
def tags_view(tag_name):
    db = models.db
    tag = (
        db.session.execute(db.select(models.Tag).where(models.Tag.name == tag_name))
        .scalars()
        .first()
    )
    
    if not tag:
        flask.abort(404)
    
    notes = db.session.execute(
        db.select(models.Note).where(models.Note.tags.any(id=tag.id))
    ).scalars()

    return flask.render_template(
        "tags-view.html",
        tag_name=tag_name,
        tag=tag,
        notes=notes,
    )


if __name__ == "__main__":
    print("Starting Flask app...")
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    try:
        app.run(debug=True, host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"Error starting app: {str(e)}")
        import traceback
        traceback.print_exc()
