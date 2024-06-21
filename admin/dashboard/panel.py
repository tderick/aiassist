import os
import requests

from bson import ObjectId
from bson.json_util import dumps
from bson.json_util import loads

from decouple import config

from flask import Blueprint, redirect, render_template, url_for, request, jsonify
from flask_login import current_user, login_required

from dashboard.database import get_database

bp = Blueprint("panel", __name__, url_prefix="/manage")


# @bp.before_request
# def _check_rights():
#     """Chef if the user is admin or not. If not, redirect to home page."""
#     if not current_user.is_admin:
#         return redirect(url_for("home.home"))


@bp.route("/")
@login_required
def dashboard():
    bots = get_database().bots.find({"owner": current_user.object_id})
    return render_template(
        "dashboard/dashboard.html",
        bots=bots,
    )


@bp.route("/users-list/")
@login_required
def user_list():
    users = get_database().users.find()
    return render_template("dashboard/users/user-list.html", users=users)


@bp.route("/bots/form", methods=["GET"])
@login_required
def create_or_edit_bot_form():
    return render_template("dashboard/bots/bot-form.html")

@bp.route("/bots/save/", methods=["POST"])
@login_required
def create_or_edit_bot():
    
    data = {
        "name": request.form.get("bot_name"),
        "description": request.form.get("bot_description"),
        "owner": current_user.object_id,
    }
    get_database().bots.insert_one(data)

    return redirect(url_for("panel.dashboard"))


@bp.route("/bots/details/")
def bot_details():
    bot = get_database().bots.find_one({"owner": current_user.object_id, "_id": ObjectId(request.args.get("id"))})
    chat_url = config("CHAT_URL")
    # import pdb; pdb.set_trace()
    return render_template("dashboard/bots/bot-details.html", bot=bot, chat_url=chat_url)

@bp.route("/bots/delete/", methods=["POST"])
def delete_bot():
    bot_id = request.form.get("bot_id")
    # get_database().bots.delete_one({"_id": ObjectId(bot_id)})
    return redirect(url_for("panel.dashboard"))

@bp.route("/bots/add-source/", methods=["POST"])
def index_webpage():
    bot_id = request.json.get("botId")
    sourceUrl = request.json.get("sourceUrl")
    sourceTitle = request.json.get("sourceTitle")
    sourcetype = request.json.get("sourcetype")
    bot = get_database().bots.find_one({"_id": ObjectId(bot_id)})

    if bot:
        get_database().bots.update_one(
            {"_id": ObjectId(bot_id)},
            {"$push": {"sources": {"title": sourceTitle, "url": sourceUrl, "sourcetype": sourcetype}}},
        )
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        rs = requests.post(config("INGESTION_URL")+"/api/v1/dataingestion/url/", headers=headers, data={"bot_id": str(bot_id), "page_url": sourceUrl})

        if rs.status_code == 200:
            return {"success": "Source added successfully."}, 200
        else:
            return {"error": "Error in adding source."}, 400
    else:
        return {"error": "Bot not found."}, 404
  

@bp.route("/bots/")
def get_bots():
    cursor = get_database().bots.aggregate([{
        "$project": {
            "_id": 0,
            "id": { "$toString": "$_id" },
            "name": 1,
            "description": 1
        }} ])
    return jsonify(loads(dumps(cursor))), 200


@bp.route('/bots/add-document-source/', methods=['POST'])
def index_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    source_title = request.form.get('sourceTitle')
    bot_id= request.form.get('botId')
    sourcetype = request.form.get('sourcetype')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    files = {'file': (file.filename, file.stream, file.mimetype)}
    data = {'bot_id': bot_id}
    
    try:
        response = requests.post(config("INGESTION_URL")+"/api/v1/dataingestion/file/", files=files, data=data)
        response.raise_for_status()
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500
    

    bot = get_database().bots.find_one({"_id": ObjectId(bot_id)})
    if bot:
        get_database().bots.update_one(
            {"_id": ObjectId(bot_id)},
            {"$push": {"sources": {"title": source_title, "url": file.filename, "sourcetype": sourcetype}}},
        )
        return jsonify({'success': 'Document added successfully.'}), 200
    else:
        return jsonify({'error': 'Bot not found.'}), 404