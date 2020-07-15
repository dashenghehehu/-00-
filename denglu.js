var express = require('express'); 
var session = require('express-session');
var FileStore = require('session-file-store')(session);
var app = express();
var sqlite3 = require("sqlite3").verbose();
var bodyParser=require('body-parser');
app.use(bodyParser.urlencoded({}));
var ws = require("nodejs-websocket");
var urlencodedParser = bodyParser.urlencoded({ extended: false })

///////////***************************////////////
var arr=[];	//聊天记录
var brr=[];	//活跃用户记录
var crr=[];	//所有用户信息
var drr=[];	//活跃用户信息
var datafrompy=[];
var sessionname=false;
/********************************************/////

app.use(express.static(__dirname + '/public'));




app.use(session({
	secret: 'dev',
	resave: false,
	saveUninitialized: true,
	cookie: { maxAge: 30*24*60*1000 } //30 天免登陆
}));

app.get('/', function(req, res){
	if(req.session.username){
		//已建立会话用户直接进入 home 页面
		console.log("session直接登入，账号：",req.session.username);
		res.redirect("./admin.html"); 
	} else {
	//重定向到登录页面
		res.redirect('/dl.html');
	}
});

app.post('/logout', function(req, res){
	//退出清除 session
	console.log("退出登录")
	req.session.username = null;
	sessionname=false
	res.redirect('/dl.html');
});

app.post('/login', function(req, res){ 
	
	var username = req.body.dlusername; 
	var pwd = req.body.dlpassword;
	console.log("登录{", "账号：",username,"密码：" ,pwd,"}");
	console.log(req.body)
	//连接数据库，查询是否已注册 
	var db = new sqlite3.Database("./record.db"); 
	db.get("SELECT password FROM users WHERE username = ?", [username], function(err, row){
		if(row==undefined){ 
			res.send(" 用户不存在");
		} else if(row.password!=pwd){	
			console.log(row.password+","+pwd)
			res.send("密码错误");
		}else{
			req.session.username = username;
			sessionname=true
			res.redirect("./admin.html"); 
		}
			
	db.close(); 
	});
});
app.post('/register', function(req, res){
	
	 
	var username = req.body.reusername; 
	var pwd = req.body.repassword;
	
	console.log("登录{", "账号：",username,"密码：" ,pwd,"}");
	console.log(req.body);
//连接数据库，查询是否已注册 
	var db = new sqlite3.Database("./record.db"); 
	db.get("SELECT id FROM users WHERE username = ?", [username], function(err, row){ 
		if(row!=undefined){ 
			res.send(" 用户已注册"); 
		} else { 
		db.serialize(function(){ 
		//向数据库写入注册信息 
			db.run("INSERT INTO users (username, password) VALUES (?, ?)", [username, pwd]); 
			}); 
		res.redirect("/dl.html"); 
		}
	db.close(); 
	});
});
/*
app.post('/verify', function(req, res){
	console.log("ver:",req.textarea)
	if(sessionname==false)
	{
		res.redirect('/dl.html');
	}else{
		res.redirect('/admin.html');
	}
});
*/
app.post('/my-form-page.cgi', urlencodedParser, function (req, res) {
		console.log("服务局接收的消息：",req.body);
})
console.log("开始建立连接...")

app.post('/wp', function(req, res){ 
	console.log("py链接.............");

	datafrompy=req.body;
	console.log(time);
	console.log(datafrompy)
	
	/**********************************/
	var obj=new Date();
	var year=obj.getYear()+1900;
	var month=obj.getMonth();
	var day=obj.getDate();
	var hour=obj.getHours();
	var minute=obj.getMinutes();
	var second=obj.getSeconds();
	var time= year+"年"+month+"月"+day+"日"+hour+"时"+minute+"分"+second+"秒"
	var record = new sqlite3.Database("./record.db"); 
	var Sid=0;
	var Did=1;
	if(datafrompy['Type']==1)//用户上线
	{
		record.get("SELECT id FROM AllStaff WHERE id=?",[datafrompy['id']], function(err, row){ 
				if(row==undefined){
					console.log("新用户，将信息写入数据库");
					record.run("INSERT INTO AllStaff (id, name, time,password) VALUES (?, ?,?,?)", [datafrompy['id'], datafrompy['name'],time,datafrompy['key']]);  
				}else{
					console.log("该用户已存在")
				}
				console.log("用户上线");
				console.log(datafrompy);
				record.run("INSERT INTO LiveStaff (id, name, time,statue) VALUES (?, ?,?,?)", [datafrompy['id'], datafrompy['name'],time,0]);
				record.run("INSERT INTO LiveStaffName (id, name) VALUES (?,?)", [datafrompy['id'], datafrompy['name']]);
			});
	}else if(datafrompy['Type']==2){ //接收消息
		
		if(datafrompy['sort']!=3){
			record.get("SELECT id FROM LiveStaff WHERE name=?",[datafrompy['Sname']], function(err, row){ 
					if(row==undefined){
						console.log("聊天对象未上线");	
					}else{
						Sid=row;
					}
				});
		}
		
		if(datafrompy['sort']==1){	//文字
			
			if(datafrompy['Dname']=="------Group chat-------"){
				Did=0
			}else{
				record.get("SELECT id FROM LiveStaff WHERE name=?",[datafrompy['Dname']], function(err, row){ 
					if(row==undefined){
						console.log("聊天对象未上线");	
					}else{
						Did=row;
					}
				});
			}
			record.run("INSERT INTO Message (id, name, time,recid,recname,content) VALUES (?, ?,?,?,?,?)", [0,datafrompy['Sname'],time,1,datafrompy['Dname'],datafrompy['content']]);
		}else if(datafrompy['sort']==2){	//照片
			if(datafrompy['Dname']=="------Group chat-------"){
				Did=0
			}else{
				record.get("SELECT id FROM LiveStaff WHERE name=?",[datafrompy['Dname']], function(err, row){ 
					if(row==undefined){
						console.log("聊天对象未上线");	
					}else{
						Did=row;
					}
				});
			}
			record.run("INSERT INTO Message (id, name, time,recid,recname,content) VALUES (?, ?,?,?,?,?)", [0,datafrompy['Sname'],time,1,datafrompy['Dname'],"照片:"+datafrompy['content']]);
		}else if(datafrompy['sort']==3){	//文件
				record.run("INSERT INTO Message (id, name, time,recid,recname,content) VALUES (?, ?,?,?,?,?)", [00,00,time,00,00,"文件:"+datafrompy['content']]);
		}else{}
	}else if(datafrompy['Type']==3){	//用户退出
	
		var qid=0;
		record.get("SELECT id FROM AllStaff WHERE name=?",[datafrompy['id']], function(err, row){ 
				qid=row['id'];
				record.run("INSERT INTO LiveStaff (id, name, time,statue) VALUES (?, ?,?,?)",[qid, datafrompy['id'],time,1]);
				record.run("Delete FROM LiveStaffName WHERE id=?", [qid]);
			});
		
	}
	
	/*******************************/
	
	res.send("this is web")
});



var server = app.listen(8003, function () { 
	var host = server.address().address 
	var port = server.address().port 
	console.log(" 应用实例，访问地址为 http://%s:%s", host, port) 
})
/*********/
const expres2 = require('express'); 
const http = require('http');
const path = require('path');
const socket = require('socket.io');
const io = socket(server);
const app2 = express();
const server2 = http.createServer(app2);


app2.use(express.static(path.join(__dirname, 'public')));

//var socket_server = require('./chatroom-master/app.js');

		
io.on('connection', socket => {
	
	
	socket.on('upDataMsg',()=> {
		console.log("刷新聊天记录")
		var record = new sqlite3.Database("./record.db");
		record.all("SELECT * FROM Message", function(err, row){ 
			if(row.length==0)
			{
				console.log("聊天记录为空")
				//res.send("")
			}else{
				arr=row;
				console.log("发送‘Msg消息’给页面")
				io.emit('Msg',arr);
			}
			
		record.close(); 
		});
   });
   
   socket.on('upDataLive',()=> {
		console.log("刷新在线用户记录")
		var record = new sqlite3.Database("./record.db");
		record.all("SELECT * FROM LiveStaff", function(err, row){ 
			if(row.length==0)
			{
				console.log("在线用户记录为空")
			}else{
				brr=row;
				console.log("发送’Live消息‘给页面")
				io.emit('Live',brr);
			}
			
		record.close(); 
		});
   });
   
   socket.on('upDataAll',()=> {
		console.log("刷新所有用户信息")
		var record = new sqlite3.Database("./record.db");
		record.all("SELECT * FROM AllStaff", function(err, row){ 
			console.log(row)
			if(row.length==0)
			{
				console.log("暂无用户")
			}else{
				crr=row;
				console.log("发送’AllStaff消息‘给页面")
				io.emit('All',crr);
			}
			
		record.close(); 
		});
   });
   
   
   socket.on('nowStaffname',()=> {
		console.log("刷新活跃用户信息")
		var record = new sqlite3.Database("./record.db");
		record.all("SELECT * FROM LiveStaffName", function(err, row){ 
			if(row.length==0)
			{
				console.log("无用户在线")
			}else{
				drr=row;
				console.log("发送‘nowStaffname消息’给页面")
				io.emit('nowname',drr);
			}			
		record.close(); 
		});
   });

});	
