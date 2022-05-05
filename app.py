from flask import Flask, render_template, request,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import defer
from werkzeug.utils import secure_filename
import json

#Start Fask Service
app = Flask(__name__)

#DataBase Connection postgreesql
DATABASE_URI = 'postgresql://test:test123@35.188.159.86:5432/test_db'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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
    #img = db.Column(BYTEA, unique=True, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'produto': self.produto,
            'descricao': self.descricao,
            'marca': self.marca,
            'preco_custo': self.preco_custo,
            'preco_venda': self.preco_venda,
            'imagem': self.imagem,
            'embalagens': self.embalagens
            #'img': self.img
        }

db.create_all()

@app.route('/')
def index():
    return render_template('inicio.html', title='Inicio')

@app.route('/produtos')
def produtos():
    return render_template('produtos.html', title='Produtos')

@app.route('/editar', methods=['GET'])
def editar():
    return render_template('edit.html', title='Cadastro')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html', title='Cadastro')

@app.route('/api/editdata',methods=['POST','GET'])
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
        if pic:
            filename = secure_filename(pic.filename)
            print("Filename: " + str(filename))
        else:
            print("Pic not Exist")
            filename = None
            pic = None
        data = json.loads(request.form.get("data"))
        arr = ["produto",
               'descricao',
             'marca',
             'preco_custo',
             'preco_venda',
             'imagem',
             'embalagens']
        for x in arr:
            val = str(data[x])
            print(data['id'])
            if val == "" or val == None or val == "{}" or val == "[]":
                print(x + "está vazio")
                print(val)
            else:
                result = Produtos.query.filter(Produtos.id == int(data['id'])).update({x : val})
        db.session.commit()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        #return "sucess",200



@app.route('/api/data')
def data():
    rtn = {'data': [produtos.to_dict() for produtos in Produtos.query]}
    return rtn

@app.route('/api/save', methods=['POST'])
def save():
    if request.method == 'POST':
            #data = request.get_json()
            pic = request.files.get("file")
            data = json.loads(request.form.get("data"))
            if pic:
                filename = secure_filename(pic.filename)
                #print("Filename: "+str(filename))
            else:
                print("Pic not Exist")
                filename = None
                pic = None
            produto = Produtos(produto=str(data['produto']),
                                descricao=str(data['descricao']),
                                marca=str(data['marca']),
                                preco_custo=data['preco_custo'].replace(',', '.'),
                                preco_venda=data['preco_venda'].replace(',', '.'),
                                imagem=str(filename),
                                embalagens=str(data['embalagens'])#,
                                #img=pic.read()
                                )
            db.session.add(produto)
            db.session.commit()
            return 'Sucesss', 200


if __name__ == '__main__':
    app.run()
