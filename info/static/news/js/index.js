var currentCid = 1; // 当前分类 id
var cur_page = 1; // 当前页
var total_page = 1;  // 总页数
var data_querying = false;   // 是否正在向后台获取数据, false：当前用户没有在向后端请求数据 反之


$(function () {

    // 进入页面需要加载新闻列表数据
    updateNewsData()

    // 首页分类切换
    $('.menu li').click(function () {
        var clickCid = $(this).attr('data-cid')
        $('.menu li').each(function () {
            $(this).removeClass('active')
        })
        $(this).addClass('active')

        if (clickCid != currentCid) {
            // 记录当前分类id
            currentCid = clickCid

            // 重置分页参数
            cur_page = 1
            total_page = 1
            updateNewsData()
        }
    })

    //页面滚动加载相关
    $(window).scroll(function () {

        // 浏览器窗口高度
        var showHeight = $(window).height();

        // 整个网页的高度
        var pageHeight = $(document).height();

        // 页面可以滚动的距离
        var canScrollHeight = pageHeight - showHeight;

        // 页面滚动了多少,这个是随着页面滚动实时变化的
        var nowScroll = $(document).scrollTop();

        if ((canScrollHeight - nowScroll) < 100) {
            // TODO 判断页数，去更新新闻数据
            // console.log("来了 老弟")
            // 前端的特性会多次触发调用，我们限定请求次数
            // data_querying=false 表示没有人向后端请求数据
            if(!data_querying){
                // 向后端请求数据

                if(cur_page <= total_page){
                    // 当前用户正在向后端请求数据
                    data_querying = true
                    updateNewsData()
                }else{
                    // 页面超标
                    alert("页码超标")
                    data_querying = false
                }

            }

        }
    })
})

function updateNewsData() {
    // TODO 更新新闻数据
    
    // 组织参数
    var params = {
        "cid": currentCid,
        "p": cur_page
    }
    
    $.get("/news_list", params, function (resp) {
         if (resp) {

             // 将总页数赋值
             total_page = resp.data.total_page
             // 先清空原有数据
             // 注意：只有第一页的时候才有测试数据，才需要清除
             if(cur_page == 1){
                  $(".list_con").html('')
             }

             // 页面自增 请求下一页的数据
             cur_page += 1
             // 在请求数据成功后，需要将data_querying改成false，下一次下拉加载更多的判断条件才能进入
             data_querying = false

            // 显示数据
            for (var i=0;i<resp.data.news_list.length;i++) {
                var news = resp.data.news_list[i]
                var content = '<li>'
                // /news/新闻id
                content += '<a href="/news/'+ news.id +' " class="news_pic fl"><img src="' + news.index_image_url + '?imageView2/1/w/170/h/170"></a>'
                content += '<a href="/news/' + news.id + ' " class="news_title fl">' + news.title + '</a>'
                content += '<a href="/news/'+ news.id +' " class="news_detail fl">' + news.digest + '</a>'
                content += '<div class="author_info fl">'
                content += '<div class="source fl">来源：' + news.source + '</div>'
                content += '<div class="time fl">' + news.create_time + '</div>'
                content += '</div>'
                content += '</li>'
                $(".list_con").append(content)
            }
        }
    })
    
    
    
}
