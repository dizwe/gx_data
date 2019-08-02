const googleTrends = require('google-trends-api');
const moment = require('moment');

let optionsObject = {
    keyword : ['klaytn','클레이튼'],
    startTime : new Date('2018-05-01'),
    endTime : new Date(Date.now()),
    category : 13, // 13 인터넷 통신, 5 컴퓨터 전자제품,
    // https://github.com/pat310/google-trends-api/wiki/Google-Trends-Categories 
}

googleTrends.interestOverTime(optionsObject)
.then(function(results){
    // console.log(JSON.parse(results).default);
    // res = JSON.parse(results).default.timelineData.filter(x=>x.hasData[0]==true);
    // 클레이튼 영어랑 한글 정보 합치고 데이터 보여주기
    // 문제 : 가장 높은 것 기준으로 보여주는것이니까(증감세는 보여줄수 있을듯!)
    let res_json = JSON.parse(results).default.timelineData;
    // console.log(res_json);

    let result = res_json.map(x=>{
        let trends_sum = x.value.reduce((acc,cur)=>acc+cur,0);
        let k = moment(x.formattedTime, "MMM DD, YYYY").format("YYYY-MM-DD");;
        
        return {'data_date':k, 'val':trends_sum}
    });

    console.log(result);
})
.catch(function(err){
    console.error('Oh no there was an error', err);
});



// realTimeTrends(이건 진짜 trend), interestOVerTime, interestByRegion