const fs = require("fs");
const sqlite3 = require("sqlite3").verbose();
const express = require("express");
const { transcode } = require("buffer");
const app = express();
const request = require("request");

const numRegEx = /^[0-9]$/g;

//가챠 id를 입력받으면 가챠 정보를 Object로 반환하는 함수
function getGachaInfoByID(id){
    var gachaInfo = fs.readFileSync(__dirname + '/gachas/pickup_'+id+'.json');
    gachaInfo = gachaInfo.toString();
    gachaInfo = JSON.parse(gachaInfo);

    var commonInfo = fs.readFileSync(__dirname + '/gachas/common_'+id+'.json');
    commonInfo = commonInfo.toString();
    commonInfo = JSON.parse(commonInfo);

    gachaInfo['common'] = commonInfo;
    return gachaInfo;
}

// api/gachainfo/(가챠 id) 로 요청이 들어오면, 가챠 정보를 반환하게 하는 함수
app.get("/api/gachainfo/:id", (req, res)=>{
    if(req.params.id != 0 && !req.params.id) res.status(400).send('The request id list is not valid.');
    else{
        valid = true;
        IDs = req.params.id.split(',');
        for(var i of IDs){
            if(i.length != 5) valid = false;
            else if(numRegEx.test(i)) valid = false;
        }

        if(!valid) res.status(400).send('The request id list is not valid.');

        try{
            result = IDs.map(getGachaInfoByID);
            res.send(result);
        }
        catch(error){
            res.status(404).send('One of the request inputs is out of range.');
        }
    }
});

// api/gachainfo/로 요청이 들어오면, 현재 진행되고 있는 가챠 정보를 반환하게 하는 함수
app.get("/api/gachainfo/", (req, res)=>{
    var currGacha = fs.readFileSync(__dirname+'/curr_gacha.json');
    currGacha = currGacha.toString();
    currGacha = JSON.parse(currGacha);
    res.send(currGacha.map(getGachaInfoByID));
});

// api/cardinfo/(가챠 id) 로 요청이 들어오면, 카드 정보를 반환하게 하는 함수
app.get("/api/cardinfo/:id", (req, res)=>{
    if(req.params.id != 0 && !req.params.id) res.status(400).send('The request id is not valid.');
    else if(numRegEx.test(req.params.id) || req.params.id.length != 6) res.status(400).send('The request id is not valid.');
    else{
        let db = new sqlite3.Database('card_info.db');
        let query = 'SELECT name, rarity, kor_name FROM cards WHERE id = (?)';

        db.get(query, [req.params.id], (err, row)=>{
            if(err) res.status(404);
            else res.send(row);
        });
    }
});

// img/(img id) 로 요청이 들어오면, 가챠 정보를 반환하게 하는 함수
app.get("/img/:imgid", (req, res) => {
    fs.readFile(__dirname + "/img/" + req.params.imgid+".png", function(
        error,
        data
    ) {
        if (error) {
            res.redirect("https://hidamarirhodonite.kirara.ca/icon_card/"+req.params.imgid+".png");
            res.end();
            request(
                (url =
                    "https://hidamarirhodonite.kirara.ca/icon_card/"+req.params.imgid+".png"),
                (method = "GET")
            ).pipe(
                fs.createWriteStream(
                    __dirname + "/img/" + req.params.imgid + ".png"
                )
            );
        } else {
            res.writeHead(200, { "Content-Type": "text/html" });
            res.end(data);
        }
    });
});

app.use("/", express.static(__dirname+"/static"));

module.exports = app;