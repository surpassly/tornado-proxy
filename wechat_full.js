if(!requestScreenCapture()){
    toast("请求截图失败");
    exit();
}
launchApp("微信");
//开启无障碍服务
//关闭通知
sleep(10000);
toast("程序开始");

threads.start(function(){
    events.observeKey();
    events.on("key_down", function(keyCode, events){
        if(keyCode == keys.volume_up || keyCode == keys.volume_down){
            toast("程序结束");
            exit();
        }
    });
});
setScreenMetrics(720, 1280);

var time = 800; //间隔时间
var step = 129;

while(true){
    var count = 0;
    sleep(time);
    var img = captureScreen();
    for(var i = 0; i < 8; i++){
        if(detect_blue_square(img, 50, 160 + i * step)) {
            click(50, 160 + i * step)  // 点击订阅号
            sleep(time);
            break
        }
    }
    sleep(time);
    var img = captureScreen();  // 订阅号部分
    for(var i = 0; i < 9; i++){
        if(detect_red_point(img, 110, 157 + i * step)){
            count += 1;
            get_history_articles(110, 157 + i * step)
            break;
        }
    }
    sleep(time);
    click(10, 50);
    sleep(time);
    var img = captureScreen();
    for(var i = 0; i < 8; i++){
        if(detect_red_point(img, 100, 160 + i * step)){
            count += 1;
            get_history_articles(100, 160 + i * step)
            break;
        }
    }
    if(count == 0) {
        toast("无新消息");
        //openAppSetting(getPackageName("微信"));
        //while(!click("强制停止"));
        launchApp("Auto.js");
        sleep(60000)
        launchApp("微信");
        sleep(5000);
    }
}

function get_history_articles(x, y) {
    click(x, y);  //点击公众号
    sleep(time);
    click(650, 50);  //点击个人档案
    sleep(time);
    swipe(300, 600, 300, 100, 1000);
    click("查看历史消息");
    p = null;
    for(var _ = 0; !p && _ < 15; _++){
        sleep(1000);
        p = images.findColor(captureScreen(), "#1aad19", {
            region: [200, 400, 50, 50],
            threshold: 0
        });
    }
    click(10, 50); //后退
    sleep(time);
    click(10, 50);
    sleep(time);
    click(10, 50);
}

function detect_blue_square(img, x, y){
    var flag = true;
    for (var i = x; i < x + 10 && flag; i++)
        for (var j = y; j < y + 10; j++)
            if (colors.toString(images.pixel(img, i, j)) != '#ff2782d7'){
                flag = false;
                break;
            }
    return flag;
}

function detect_red_point(img, x, y){
    var flag = true;
    for (var i = x; i < x + 3 && flag; i++)
        for (var j = y; j < y + 3; j++)
            if (colors.toString(images.pixel(img, i, j)) != "#ffff3e3e"){
                flag = false;
                break;
            }
    return flag;
}

