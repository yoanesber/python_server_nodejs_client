from flask import Flask, request
from flask_restful import Resource, Api
# import mysql.connector
from sqlalchemy import create_engine
from json import dumps
from flask.ext.jsonpify import jsonify

app = Flask(__name__)
# api = Api(app)

#For MYSQL
# db_config = {
#     'user'      :'xxx', 
#     'password'  :'xxx', 
#     'host'      :'xxx', 
#     'database'  :'xxx'
# }
# conn = mysql.connector.connect(**db_config)
# cursor = conn.cursor(buffered=True)

#For SQLITE
db_connect = create_engine('sqlite:///database.db')
conn = db_connect.connect()

#Index
@app.route('/')
def index():
    return '<h1>Hi, welcome to My Portal.</h1>'

#Get data News
@app.route('/api/get/news/<string:status>/<string:topic>/<string:search>', methods=['GET'])
def get_news(status, topic, search):
    where = " WHERE 1=1 "
    if status.lower() == "draft" or status.lower() == "published" or status.lower() == "deleted" :
        where += " AND lower(ns.name) = lower('" + status + "') "

    if topic.lower() != "~":
        where += " AND t.id = " + topic.lower() + " "

    if search.lower() != "~":
        where += " AND (n.title LIKE '%" + search + "%' OR n.content LIKE '%" + search + "%' OR t.name LIKE '%" + search + "%') " 

    sql = ("SELECT " + 
                "n.id AS news_id, " + 
                "n.title AS news_title, " + 
                "n.content AS news_content, " + 
                "n.createdAt AS news_createdAt, " + 
                "n.updatedAt AS news_updatedAt, " + 
                "ns.id AS news_status_id, " + 
                "ns.name AS news_status_name, " + 
                "t.id AS topic_id, " + 
                "t.name AS topic_name, " + 
                "mtn.id AS mapping_id " + 
            "FROM " + 
                "mapping_topics_news mtn " + 
                    "LEFT JOIN " + 
                "news n ON mtn.news_id = n.id " + 
                    "LEFT JOIN " + 
                "news_status ns ON n.status_id = ns.id " + 
                    "LEFT JOIN " + 
                "topics t ON mtn.topic_id = t.id " + where +
            "ORDER BY n.createdAt DESC")
    
    lastResult = []
    try:
        query = conn.execute(sql)
    except:
        return jsonify(lastResult)
    
    for data in query.cursor.fetchall():
        i = 0
        idx = -1
        for obj in lastResult:
            if obj['news_id'] == data[0]:
                idx = i
                break

            i = i + 1

        if idx == -1:
            lastResult.append({
                'news_id':data[0], 
                'news_title':data[1], 
                'news_content':data[2], 
                'news_createdAt':data[3], 
                'news_updatedAt':data[4], 
                'news_status_id':data[5], 
                'news_status_name':data[6], 
                'topics':[{'id': data[7], 'name': data[8]}]
            })
        else:
            lastResult[idx]['topics'].append({'id': data[7], 'name': data[8]})

    return jsonify(lastResult)

#Get data News Status
@app.route('/api/get/status', methods=['GET'])
def get_news_status():
    sql = ("SELECT * FROM news_status")
    
    lastResult = []
    try:
        query = conn.execute(sql)
    except:
        return jsonify(lastResult)
    
    for data in query.cursor.fetchall():
        lastResult.append({
            'status_id':data[0], 
            'status_name':data[1], 
            'status_desc':data[2]
        })

    return jsonify(lastResult)

#Get data Topics
@app.route('/api/get/topics', methods=['GET'])
def get_topics():
    sql = ("SELECT id, name, createdAt FROM topics WHERE active = 1")
    
    lastResult = []
    try:
        query = conn.execute(sql)
    except:
        return jsonify(lastResult)
    
    for data in query.cursor.fetchall():
        lastResult.append({
            'topic_id':data[0], 
            'topic_name':data[1], 
            'topic_createdAt':data[2]
        })

    return jsonify(lastResult)

#Create data
@app.route('/api/create/news', methods=['POST'])
def create_news():
    data = {
        'news_title' : request.args.get('news_title', ''),
        'news_content' : request.args.get('news_content', ''),
        'topic_id' : request.args.get('topics'),
        'status_id' : request.args.get('news_status_id')
    }

    sql = "INSERT INTO news(title, content, active, status_id) VALUES('" + data['news_title'] + "', '" + data['news_content'] + "', 1, " + str(data['status_id']) + ");"

    try:
        query = conn.execute(sql)
        # conn.commit()

        sql = "SELECT MAX(id) FROM news"
        query = conn.execute(sql)
        last_id_news = max(row[0] for row in query.cursor.fetchall())
        topic_id_list = data['topic_id'].split('_')
        for topic_id in topic_id_list:
            sql = "INSERT INTO mapping_topics_news(topic_id, news_id) VALUES(" + str(topic_id) + ", " + str(last_id_news) + ");"
            query = conn.execute(sql)

        return jsonify({'success':True})
    except:
        return jsonify({'success':False})

#Delete data
@app.route('/api/delete/news/<string:news_id>', methods=['DELETE', 'GET'])
def delete_news(news_id):
    sql = "DELETE FROM news WHERE id = " + str(news_id)
    
    try:
        conn.execute(sql)
        # conn.commit()

        sql = "DELETE FROM mapping_topics_news WHERE news_id = " + str(news_id)
        conn.execute(sql)
        # conn.commit()

        return jsonify({'success':True})
    except:
        return jsonify({'success':False})


if __name__ == '__main__':
    # app.run(host='https://infinite-journey-34313.herokuapp.com/')
    app.run(host='127.0.0.1')

