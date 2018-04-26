if(!requestScreenCapture()){
    toast("请求截图失败");
    exit();
}
launchApp("微信");
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
var time = 600;
var wx_list = create_wx_list();
var unfollow = new Array()

sleep(time);
click(550, 50); // 点击搜索
for(var i = 0; i < wx_list.length; i++) {
    sleep(time);
    setText(wx_list[i]);
    sleep(time);
    click("搜一搜");
    var p = null;
    for(var _ = 0; !p && _ < 20; _++){
        sleep(1000);
        p = images.findColor(captureScreen(), "#feecb6", {
            region: [650, 250, 45, 350],
            threshold: 0
        });
    }
    if(p) {
        click(p.x, p.y);
        sleep(time);
        swipe(300, 600, 300, 100, 1000);
        if(click("进入公众号")){
            sleep(time);
        } else {
            //可能在其它地方出现"关注"
            p = images.findColor(captureScreen(), "#43ae42", {
                region: [0, 350, 360, 850],
                threshold: 0
            });
            click(p.x, p.y);
            sleep(5000);
        }
        click(10, 50);
        sleep(time);
        click(10, 50);
        sleep(time);
    } else {
        print(wx_list[i])
    }
    click(10, 50);
    //sleep(60000)
}
console.show();
toast("程序结束");
exit();

function create_wx_list(){
    return ("wuhanfabu,"+
"huangshifabu,"+
"syfb0719,"+
"yichangweibo,"+
"xiangyangfb,"+
"ezfb5102,"+
"jmfb2015,"+
"jingzhoufabu,"+
"hgwx5369,"+
"cnxn2015,"+
"zhongguo_suizhou,"+
"hbesfb,"+
"yangxinfabu,"+
"qiaokoufabu,"+
"gh_47fd176080a0,"+
"tianmenfabu,"+
"hbesxd,"+
"changyangfabu,"+
"hbxtfb,"+
"hbxefb,"+
"ZGLCW-7216111,"+
"zxfb2016,"+
"gh_80cd2f0ccce8,"+
"ydfbwb,"+
"dayefabu,"+
"YCFB_4212,"+
"yafabu,"+
"wuhanminzheng,"+
"Hubeicivil,"+
"esmz8224390,"+
"whjhmzj,"+
"xnmzfb,"+
"wmfwwmjk,"+
"gh_0b28368fb18a,"+
"pinganwuhan001,"+
"pinganyichang,"+
"pinganshiyan,"+
"pawcwjw,"+
"PA_xiangyang,"+
"jingmenpolice,"+
"gh_ede190ff3ec3,"+
"pinganhuanggang110,"+
"pingan_huangshi,"+
"jsxzhfw,"+
"zhangshanghanyang,"+
"suizhou-ga,"+
"hbxt-110,"+
"eszgaj,"+
"dhgxga,"+
"pinganhongshan,"+
"gh_23696e2a55ac,"+
"sssgaj,"+
"djkgaj,"+
"qjsgaj,"+
"pingantianmen,"+
"paxg_2017,"+
"hbzsxgaj,"+
"pinganmaojian,"+
"zwgafj,"+
"gh_ede190ff3ec3,"+
"xnsgaj,"+
"pingansongzi,"+
"pinganfangxian,"+
"pinganyunxi,"+
"gonganwangju,"+
"pinganqiaokou,"+
"pinganyunyang,"+
"ezsgajws110,"+
"pinganhonghu,"+
"zxjjxfh,"+
"PeaceXiShui,"+
"gh_42033b08e3d1,"+
"pinganwds,"+
"gh_0a64b60bbc0f,"+
"shashigongan,"+
"jsgaj110,"+
"ezxspagl110,"+
"hanchuanggongan,"+
"pinganjingzhou,"+
"pinganzhongxiang,"+
"gh_c1b9a83f7566,"+
"sykfqfj,"+
"essgaj,"+
"ycxlga,"+
"gh_fc6044aa0628,"+
"pingansnj,"+
"xingshangongan,"+
"jianglingpolice,"+
"hbhrmga,"+
"dwga110,"+
"duodao110,"+
"pingan-suixian,"+
"lcpcs110,"+
"gsgaj110,"+
"xyxzgaj,"+
"wufenggongan,"+
"gh_4bb4b6a19e0e,"+
"XiaoNanpolice,"+
"YCPOLICE0712,"+
"hubeigaojing,"+
"gh_52276982ef15,"+
"hbgszxdd30,"+
"gjsydd,"+
"HBGSJJXTDD,"+
"ggzd08,"+
"gjxgdd06,"+
"gjjzdd,"+
"hbgjjmdd,"+
"hbgsjj23110,"+
"hbgsjj22dd,"+
"cd02769571779,"+
"ggzd01,"+
"hbgjgadd,"+
"gjcydd,"+
"hbgsjjezdd2014,"+
"gh_e8bbce1b1c6f,"+
"gghzdd,"+
"gjmcdd,"+
"gjhcdd,"+
"gjzd_hsdd,"+
"hbgjhm,"+
"ggzdsx,"+
"ggdydd,"+
"gjjl3322433,"+
"hbgsjjxldd,"+
"HBGJHP,"+
"hbgjszdd,"+
"ggymdd,"+
"HB-HSGS,"+
"gsyxdd2014,"+
"gh_907f19c581fd,"+
"hbgjjadd001,"+
"hbgjxsdd,"+
"GJYXDD,"+
"hbgsjjzdsxdd,"+
"ggzdyl7526122,"+
"wuhanjiaojing,"+
"hbjjwx,"+
"hubeigaojing,"+
"xyjiaojing,"+
"yichangjiaojing,"+
"sy-jiaojing,"+
"jingzhoujiaojing1,"+
"hbjmjiaojing,"+
"xgjiaojing,"+
"jzjj0610,"+
"ycxljj,"+
"eszgajgj,"+
"gh_2e408730d74e,"+
"sz——jiaojing,"+
"dentalhospital_whu,"+
"jiankangyiyuan,"+
"whuh1866,"+
"rmhwhu,"+
"zxhospital,"+
"ycszxrmyy,"+
"Whuznyy,"+
"jzszxyy,"+
"luojia1893,"+
"ihuster,"+
"zueler,"+
"whutwechat,"+
"ccnuwechat,"+
"dizhidaxue,"+
"hzau_news_center,"+
"ctguedu,"+
"hubuxcb,"+
"wuhanfangda,"+
"scuec1951,"+
"wustwx,"+
"iwiter,"+
"hbutwechat,"+
"jhun-xcb,"+
"yangtzeu_dwxcb,"+
"hbnu1973,"+
"HBWAXCZF,"+
"WHWAXCZF,"+
"jzwjxczf,"+
"shiyanwangan,"+
"xnwazd,"+
"huangganwj,"+
"HBXYWA,"+
"JMWJXCZF,"+
"szwjxczf,"+
"XGWAXCZF,"+
"ycwjxczf,"+
"HSWAXCZF,"+
"ezhouwangan,"+
"eswjxczf,"+
"snjwjxczf").split(",");
}
