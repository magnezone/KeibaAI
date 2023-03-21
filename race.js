var url = location.aref;

function set2fig(num) {
   // 桁数が1桁だったら先頭に0を加えて2桁に調整する
   var ret;
   if( num < 10 ) { ret = "0" + num; }
   else { ret = num; }
   return ret;
}

function showClock2() {
   var nowTime = new Date();
   var nowHour = set2fig( nowTime.getHours() );
   var nowMin  = set2fig( nowTime.getMinutes() );
   var nowSec  = set2fig( nowTime.getSeconds() );
   //var msg = nowHour + ":" + nowMin + ":" + nowSec;
   // CSVファイルを取得
   let csv = new XMLHttpRequest(); 
   // CSVファイルへのパス
   csv.open("GET", "race.csv", true);
   var msg = csv.responseText.split(/\r\n|\n/);
   document.getElementById("RealtimeClockArea2").innerHTML = msg;
   console.log(msg);
}

setInterval('showClock2()',1000);


