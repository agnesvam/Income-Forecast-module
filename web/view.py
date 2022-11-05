from flask import Blueprint, render_template, request, flash, jsonify
import cx_Oracle

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return '<h1> fdfddff</h1>'