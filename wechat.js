if(!requestScreenCapture()){
    toast("请求截图失败");
    exit();
}
launchApp("微信");
//开启无障碍服务
//关闭通知
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
var time = 600; //间隔时间
var step = 129;

var x = 110;
var y = 157;

while(true){
    sleep(time);
    var img = captureScreen();
    for(var i = 0; i < 9; i++){
        if(detect_red_point(img, x, y + i * step)){
            click(x, y + i * step);  //点击公众号
            sleep(time);
            click(650, 50);  //点击个人档案
            sleep(time);
            swipe(300, 600, 300, 100, 1000);
            click("查看历史消息");
            sleep(8000)
            click(10, 50); //后退
            sleep(time);
            click(10, 50);
            sleep(time);
            click(10, 50);
            break;
        }
        if(i == 8) {
            toast("无新消息")
            sleep(10000);
        }
    }
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