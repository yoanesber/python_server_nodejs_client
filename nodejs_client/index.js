var async = require("async");
var express = require("express");
var https = require("https");
var app = express();
var port = process.env.PORT || 3000;
app.use(express.static(__dirname + '/public'));
app.use(express.static(__dirname + '/assets'));

app.engine('html', require('ejs').renderFile);
app.set('view engine', 'html');

app.get("/", function(req, res){
    var data_news = [];
    var data_topics = [];
    var data_news_status = [];

    async.waterfall([
        function(cb)
        {//1. By default, get all news
            https.get("https://change_url_here.com/api/get/news/all/~/~", function(response) {
                var body = ""  ;
                response.on("data", function(chunk){
                    body += chunk;
                });

                response.on('end', function(){
                    var news = JSON.parse(body);
                    data_news = news;
                    cb(null);
                });
            });
        },
        function(cb)
        {//2. Get topics
            https.get("https://change_url_here.com/api/get/topics", function(response) {
                var body = ""  ;
                response.on("data", function(chunk){
                    body += chunk;
                });

                response.on('end', function(){
                    var topics = JSON.parse(body);
                    data_topics = topics;
                    cb(null);
                });
            });
        },
        function(cb)
        {//3. Get status
            https.get("https://change_url_here.com/api/get/status", function(response) {
                var body = ""  ;
                response.on("data", function(chunk){
                    body += chunk;
                });

                response.on('end', function(){
                    var news_status = JSON.parse(body);
                    data_news_status = news_status;
                    cb(null);
                });
            });
        },
        function()
        {//4. Render view
            // console.log(JSON.stringify(data_news));
            res.render("news_list.ejs", {news:data_news, topics:data_topics, news_status:data_news_status});
        }
    ]);
});

app.listen(port, () => console.log("Listening on port: " + port));