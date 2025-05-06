from flask import render_template
from project693.controller import app


# Catch request of page_not_found
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error/404.html"), 404


# Catch request of internal_server_error
@app.errorhandler(500)
def internal_server_error(error):
    return render_template("error/500.html"), 500


# Catch request of Method Not Allowed
@app.errorhandler(405)
def internal_server_error(error):
    return render_template("error/405.html"), 405


# Catch request of forbidden
@app.errorhandler(403)
def forbidden_server_error(error):
    return render_template("error/403.html"), 403
