if(!requestScreenCapture()){
    toast("请求截图失败");
    exit();
}
launchApp("今日头条");
//开启无障碍服务
//关闭通知
sleep(5000);
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
/*
while(true){
    swipe_up();
    sleep(10000);
    break
}
*/
for(var i = 0; i < 2; i++){
    swipe_up();
    sleep(10000);
}

toast("程序结束");
exit();

function swipe_up(){
    var fresh = false
    var top = 210;
    var bottom = 1190;

    for(var i = 0; i < 20; i++){
        var img = captureScreen();
        var y_top = -1;
        var y_bottom = -1;
        for (var y = top; y < bottom; y += 3){
            if (detect_grey_line(img, 10, y)){
                y_top = y;
                break;
            }
        }
        for (var y = y_top + 450; y < bottom; y += 5){
            if (detect_grey_line(img, 10, y)){
                y_bottom = y;
                break;
            }
        }
        if (y_top != -1 && y_bottom != -1) {
            swipe(10, y_bottom, 10, y_top, 500);
        } else if (y_top != -1 && y_bottom == -1){
            if (y_top - 450 > 0)
                swipe(10, y_top, 10, y_top - 450, 500);
            if (y_top + 450 < 1280)
                swipe(10, y_top + 450, 10, y_top, 500);
        } else {
            swipe(10, 1000, 10, 300, 1000);
        }
        sleep(1000);  //等待图片加载
        if (click("点击刷新")){
            fresh = true;
            break;
        }
    }
    if (!fresh)
        click("首页");
}

function detect_grey_line(img, x, y){
    var c = colors.toString(images.pixel(img, x, y));
    var flag = true;
    for (var i = x; i < x + 20 && flag; i++)
        for (var j = y; j < y + 2; j++)
            if (colors.toString(images.pixel(img, i, j)) != "#fff4f5f6"){
                flag = false;
                break;
            }
    return flag;
}
