from flask import render_template, redirect, url_for
from . import quanter
from ..models_quanter import BacktestingLog


@quanter.route('/', methods=['GET', 'POST'])
def main():
     return 'test quanter'




