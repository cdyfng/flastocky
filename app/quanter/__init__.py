from flask import Blueprint

quanter = Blueprint('quanter', __name__)

from . import views
from ..models_quanter import BacktestingLog


