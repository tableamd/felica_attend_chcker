#include <ESP8266WiFi.h>
#include "DHT.h"
extern "C" {
#include "user_interface.h"
}
#define DHTPIN 12
#define DHTTYPE DHT11 //使用するセンサはDHT11
#define STEW_URL "stewgate-u.appspot.com" //stewgateのドメイン名
#define STEW_TOKEN "TOKEN"

//int sendData(float temp, float humid, int blight){
//  int count = 0;
//  String sentence = "";
//  sentence += "【委員会室の温度・湿度】\n";
//  sentence += "温度: ";
//  sentence += temp;
//  sentence += "度\n";
//  sentence += "湿度: ";
//  sentence += humid;
//  sentence += "％\n\n";
//  if(blight > 500)
//    sentence += "現在, 委員会室に人が居ます。";
//  else
//    sentence += "現在, 委員会室に人は居ません。";
//
//  Serial.print("connecting to ");
//  Serial.println(STEW_URL);
//  String content = "_t=";
//         content += STEW_TOKEN;
//         content += "&msg=";
//         content += sentence;
//
//  String httpCmd = "POST /api/post/ HTTP/1.0\r\n";
//  httpCmd       += "Host: stewgate-u.appspot.com\r\n";
//  httpCmd       += "Content-Length: ";
//  httpCmd       +=  content.length();
//  httpCmd       += "\r\n\r\n";
//  httpCmd       +=  content;
//  httpCmd       += "\r\n\r\n";
//  
//  // Use WiFiClient class to create TCP connections
//  WiFiClient client;
//  const int httpPort = 80;
//
//  Serial.println("connecting");
//  while (!client.connect(STEW_URL, httpPort)) {
//    Serial.print(".");
//    delay(200);
//    count++;
//    if(count == 5){
//      return 0;  
//    }
//  }
//
//  // This will send the request to the server
//  client.print(httpCmd);
//  delay(50);
//  client.stop();
//  return 1;
//}

char toSSID[] = "SSID";
char ssidPASSWD[] = "PASSWORD";

DHT dht(DHTPIN, DHTTYPE, 15);

void setup() {
  //デバッグ用にシリアルを開く
  Serial.begin(115200);
  Serial.println("PG start");
  dht.begin();
  delay(2000);
  randomSeed(system_adc_read());
  delay(1000);

  //WiFiクライアントモード
  WiFi.mode(WIFI_STA);

  //WiFiを繋ぐ前に、WiFi状態をシリアルに出力
  //WiFi.printDiag(Serial);

  WiFi.begin(toSSID, ssidPASSWD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");

  //WiFiの状態を表示
  //WiFi.printDiag(Serial);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  int count = 0;
  delay(1000);
  int blight = system_adc_read(); //分解能は10bitらしい
  
  delay(2000);
  float h = dht.readHumidity();
  delay(500);
  float t = dht.readTemperature();
  
  while (((isnan(h) || isnan(t)) || (h == 0 && t == 0)) && (count<5)) { 
    delay(1000);
    h = dht.readHumidity();
    delay(500);                              
    t = dht.readTemperature();
    count++;
  }
  
  delay(20);
  
  //-------------------ここからデータ送信開始----------------------
  int counter = 0;
  int f = 0;
  String sentence = "";
  sentence += "【委員会室の温度・湿度】\n";
  sentence += "温度: ";
  sentence += String(t);
  sentence += "度\n";
  sentence += "湿度: ";
  sentence += String(h);
  sentence += "％\n\n";
  if(blight > 500)
    sentence += "現在, 委員会室に人が居ます。\n";
  else
    sentence += "現在, 委員会室に人は居ません。\n";

  sentence += String(random(21474835));

  Serial.print("connecting to ");
  Serial.println(STEW_URL);
  String content = "_t=";
  content       += STEW_TOKEN;
  content       += "&msg=";
  content       += sentence;

  String httpCmd = "POST /api/post/ HTTP/1.0\r\n";
  httpCmd       += "Host: stewgate-u.appspot.com\r\n";
  httpCmd       += "Content-Length: ";
  httpCmd       +=  content.length();
  httpCmd       += "\r\n\r\n";
  httpCmd       +=  content;
  httpCmd       += "\r\n\r\n";
  
  // Use WiFiClient class to create TCP connections
  WiFiClient client;

  Serial.println("connecting");
  while (!client.connect(STEW_URL, 80)) {
    Serial.print(".");
    delay(500);
    counter++;
    if(counter == 7){
      f = 0; //送信失敗
      break;
    }
  }

  // This will send the request to the server
  client.print(httpCmd);
  delay(2000);

  if(client.status() == 200){
      f = 1; //送信成功
  }
  else{
    f = 0;
  }
  
  client.stop();
  //---------------------ここまで------------------------

  if(f==1){
    Serial.println("send ok!!");
  }
  else{
    Serial.println("send fail...");
  }

  delay(20);
  WiFi.disconnect();
  delay(1000);

  //Deep-Sleep
  ESP.deepSleep(30 * 60 * 1000 * 1000, WAKE_RF_DEFAULT);
  
  delay(1000);

}
