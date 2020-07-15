	var sqlite3 = require("sqlite3").verbose();
	var record = new sqlite3.Database("./record.db"); 
	var id = 0000000;
	var recid = 4;
	var name="33"
	var recname="44"
	var content="qweq"
	var obj=new Date();
	var year=obj.getYear();
	var month=obj.getMonth();
	var day=obj.getDay();
	var hour=obj.getHours();
	var minute=obj.getMinutes();
	var second=obj.getSeconds();
	var time= year+"年"+month+"月"+day+"日"+hour+"时"+minute+"分"+second+"秒"
	
	
//record.run("INSERT INTO LiveStaff (id, name, time) VALUES (?, ?,?)", [4, "v",2]);
//	record.run("DROP TABLE Message;");
//	record.run("DROP TABLE LiveStaff;");
//	record.run("DROP TABLE AllStaff;");
	//record.run("INSERT INTO users (username, password) VALUES (?, ?)", [username, pwd]);
//	record.run("CREATE TABLE LiveStaffName (id TEXT NOT NULL,name TEXT NOT NULL);");
//	record.run("CREATE TABLE Message (id TEXT NOT NULL,name TEXT NOT NULL,time CHAR（50）, recid TEXT  NOT NULL, recname TEXT NOT NULL, content TEXT NOT NULL);");
//	record.run("CREATE TABLE AllStaff (id TEXT  PRIMARY KEY NOT NULL,name TEXT NOT NULL,time CHAR（50）,password TEXT NOT NULL);");
//	record.run("CREATE TABLE LiveStaff (id TEXT   NOT NULL,name TEXT NOT NULL,time CHAR(50),statue INT NOT NULL);");
	
//	s = record.run("SELECT time FROM STAFF WHERE id = 1;")
/*	record.get("SELECT * FROM Message", function(err, row){ 
			console.log(row)
		record.close(); 
		});*/
	//	record.run("DELETE FROM Message WHERE id = 6")
	
	record.run("INSERT INTO AllStaff (id, name, time,password) VALUES (?, ?,?,?)", [4, "v",2,2]); 
//	record.run("INSERT INTO LiveStaff (id, name, time) VALUES (?, ?,?)", [4, "aasdas",1]); 
/*	record.run("INSERT INTO Message (id, name, time,recid,recname,content) VALUES(?,?,?,?,?,?)", [id, name, time,recid,recname,content])*/
	console.log("ssssss");
	record.close(); 
	
	