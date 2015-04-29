from flask import Blueprint

stock = Blueprint('stock', __name__)

from . import views
from ..models_stock import Stock, Baseinfo, StockHistory


