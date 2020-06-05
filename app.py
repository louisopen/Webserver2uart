#!/usr/bin/env python
#coding= utf-8

from app_device import *

from flask import Flask, render_template, Response, request, redirect
import os

# home page
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)