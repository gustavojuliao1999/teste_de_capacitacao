#!/usr/bin/env python
# coding: utf-8

# In[1]:


import io
from flask import Flask, render_template, request, jsonify, current_app as app, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import defer
from werkzeug.utils import secure_filename
import json
import base64
import codecs
from base64 import b64encode
from PIL import Image
import os
import PIL
import glob

# In[2]:


# Start Fask Service
app = Flask(__name__)

# DataBase Connection postgreesql
DATABASE_URI = 'postgresql://test:test123@35.188.159.86:5432/test_db'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# In[3]:


class Produtos(db.Model):
    __tablename__ = "produtos"
    __table_args__ = dict(schema="public")
    id = db.Column(db.Integer, primary_key=True)
    produto = db.Column(db.String(64))
    descricao = db.Column(db.String(256))
    marca = db.Column(db.String(64))
    preco_custo = db.Column(db.Float())
    preco_venda = db.Column(db.Float())
    imagem = db.Column(db.String(256))
    embalagens = db.Column(db.String(2))
    img = db.Column(BYTEA, unique=True, nullable=False)
    thumb = db.Column(BYTEA, unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'produto': self.produto,
            'descricao': self.descricao,
            'marca': self.marca,
            'preco_custo': self.preco_custo,
            'preco_venda': self.preco_venda,
            'imagem': self.imagem,
            'embalagens': self.embalagens,
            'img': str(b64encode(self.img), 'utf-8'),
            'thumb': '<img src="data:image/png;base64, ' + str(b64encode(self.img),
                                                               'utf-8') + '" alt="img" style="height: 100px;" />'
        }

    db.create_all()


# In[4]:


def convert_image(base64_str):
    buffer = io.BytesIO()
    imgdata = base64.b64decode(str(b64encode(base64_str), 'utf-8'))
    # str(b64encode(self.img),'utf-8')
    # imgdata = str(str(base64_str),'utf-8')
    print(imgdata)
    print(type(imgdata))
    fixed_height = 150
    image = Image.open(io.BytesIO(imgdata))
    # image = Image.open(FileStorage(imgdata))
    # image = Image.open(imgdata)
    height_percent = (fixed_height / float(image.size[1]))
    width_size = int((float(image.size[0]) * float(height_percent)))
    image = image.resize((width_size, fixed_height), PIL.Image.NEAREST)
    image.save(buffer, format="PNG")
    img_b64 = base64.b64encode(buffer.getvalue())
    ret = base64.b64decode(str(img_b64))
    return ret


# In[5]:


@app.route('/')
def index():
    return render_template('inicio.html', title='Inicio')


# In[6]:


@app.route('/produtos')
def produtos():
    return render_template('produtos.html', title='Produtos')


# In[7]:


@app.route('/editar', methods=['GET'])
def editar():
    return render_template('edit.html', title='Editar')


# In[8]:


@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html', title='Cadastro')


# In[9]:


@app.route('/api/editdata', methods=['POST', 'GET'])
def editdata():
    if request.method == 'GET':
        vid = request.args.get('id')
        rtn = {'data': [Produtos.query.get(vid).to_dict()]}
        return rtn
    if request.method == 'POST':
        try:
            delet = json.loads(request.form.get("delet"))
            if delet:
                print("delet")
                print(delet)
                Produtos.query.filter(Produtos.id == int(delet)).delete()
                db.session.commit()
        except:
            pass
        pic = request.files.get("file")
        data = json.loads(request.form.get("data"))
        if pic:
            rpic = pic.read()
            filename = secure_filename(pic.filename)
            print("Filename: " + str(filename))
            result = Produtos.query.filter(Produtos.id == int(data['id'])).update({"imagem": filename})
            result = Produtos.query.filter(Produtos.id == int(data['id'])).update({"img": rpic})
            result = Produtos.query.filter(Produtos.id == int(data['id'])).update({"thumb": convert_image(rpic)})
        else:
            print("Pic not Exist")
            filename = None
            pic = None

        arr = ["produto",
               'descricao',
               'marca',
               'preco_custo',
               'preco_venda',
               'embalagens']
        for x in arr:

            val = str(data[x])
            if (x == 'embalagens'):
                if (val == "OT"):
                    val = data["emb_outro"]
            print(data['id'])
            if val == "" or val == None or val == "{}" or val == "[]":
                print(x + "está vazio")
                print(val)
            else:
                result = Produtos.query.filter(Produtos.id == int(data['id'])).update({x: val})
        db.session.commit()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


# In[10]:


@app.route('/api/data')
def data():
    # rtn = {'data': [produtos.to_dict() for produtos in Produtos.query]}
    prod = {'data': []}
    for produtos in Produtos.query:
        var = produtos.to_dict()
        var["img"] = ""
        prod['data'].append(var)
    return prod


# In[11]:


@app.route('/api/savedata', methods=['POST'])
def save():
    if request.method == 'POST':
        # data = request.get_json()
        pic = request.files.get("file")
        data = json.loads(request.form.get("data"))
        print(pic)
        if pic:
            filename = secure_filename(pic.filename)
            # print("Filename: "+str(filename))
            rpic = pic.read()
        else:
            print("Pic not Exist")
            filename = None
            rpic = None
        if (data['embalagens'] == "OT"):
            data['embalagens'] = data["emb_outro"]
        print(data['id'])
        produto = Produtos(produto=str(data['produto']),
                           descricao=str(data['descricao']),
                           marca=str(data['marca']),
                           preco_custo=data['preco_custo'].replace(',', '.'),
                           preco_venda=data['preco_venda'].replace(',', '.'),
                           imagem=str(filename),
                           embalagens=str(data['embalagens']),
                           img=rpic,
                           thumb=convert_image(rpic)
                           )
        db.session.add(produto)
        db.session.commit()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


# In[ ]:


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)

# In[ ]:




