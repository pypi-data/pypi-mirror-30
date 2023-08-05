# coding: utf-8
from flask import Blueprint, render_template, redirect

bp = Blueprint('documentation', __name__)


@bp.route('/documentation')
def get_docs():
    """Help pages and documentation

    :returns html_template index.html:
    """
    return redirect("http://docs.modislock.net", code=302)
