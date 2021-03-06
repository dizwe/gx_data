const { Pool, Client } = require('pg');
const format = require('pg-format'); // 여러개 value insert 할 때 사용.
const moment = require('moment');
var Twitter = require('twitter');
var client = new Twitter({
  consumer_key: '4RTtiiqxX4ID949CZi7Wnr62M',
  consumer_secret: process.env.CONSUMER_SECRET,
  access_token_key: '1127968910-XAALt7MLvPZuQzRS33Ksf4RtzaOBy6rXSBMzcHD',
  access_token_secret: process.env.ACCESSTOKEN_SECRET,
});

const pg_client = new Client({
    user: process.env.PGUSER,
    host: process.env.PGHOST,
    database: process.env.PGDATABASE,
    password: process.env.PGPASSWORD,
    port: process.env.PGPORT,
  });
pg_client.connect();

const googleTrends = require('google-trends-api');

let optionsObject = {
    keyword : ['klaytn','클레이튼'],
    startTime : new Date('2018-05-01'),
    endTime : new Date(Date.now()),
    category : 13, // 13 인터넷 통신, 5 컴퓨터 전자제품,
    // https://github.com/pat310/google-trends-api/wiki/Google-Trends-Categories 
}

async function Insert_go(result_obj){
    try{
        let result_arr = result_obj.map(x=>[x.data_date,x.val]);
        let sql = format(`INSERT INTO ods_google.google_trend (data_date, trend_val)
                          VALUES %L
                          ON CONFLICT (data_date) 
                          DO UPDATE SET trend_val = EXCLUDED.trend_val; 
                        `, result_arr); 
        const res = await pg_client.query(sql);
        console.log('done google');
        return res;
    }catch(e){
        console.log(e);
    }
}

async function Insert_tw(result_obj){
    try{
        let result_arr = result_obj.map(x=>[x.start,x.tweets_num,x.retweet_num, x.favorite_num]);
        let sql = format(`INSERT INTO ods_google.twitter_trend (data_date, tweets_num, retweet_num,favorite_num)
                          VALUES %L
                          ON CONFLICT (data_date) 
                          DO UPDATE SET tweets_num = EXCLUDED.tweets_num,retweet_num = EXCLUDED.retweet_num,favorite_num = EXCLUDED.favorite_num; 
                        `, result_arr); 
        const res = await pg_client.query(sql);
        console.log('done twitter');
        return res;
    }catch(e){
        console.log(e);
    }
}

// until은 7-10이면 7-9 까지의 데이터가 나온다
// since를 사용할수 없고 since_id를 통하여 since를 구현할 수 있기 때문에 따로 until 만듦.
// // Keep in mind that the search index has a 7-day limit(일주일 데이터만 받을 수 있음)
function next_promise(next_page_max_id, since_id, tweets_num, retweet_num, favorite_num, raw_data, q){
    return client.get('search/tweets', {q: q,max_id:next_page_max_id,since_id:since_id,count:100}).then((tweets)=>{
      // delete해도 length 자체를 바꾸지는 않는다. pop하면 바꾼다.(앞에서 바꾼 문서)
      // 이미 앞 페이지에서는 전체 다 읽어왔고 next_page_max_id가 앞페이지의 가장 마지막 번호이므로 다음 페이지 부터는 첫번째껀 안읽어도 된다.
      tweets.statuses.shift();
      if(tweets.statuses.length>0){
        // 트윗 확인해보기
        // for(let i =0;i<tweets.statuses.length ; i++){
        //   console.log(tweets.statuses[i].text);
        // }
        // raw_Data 추가하기 (concat은 기존 데이터를 바꾸지는 않는다.)
        raw_data = raw_data.concat(tweets.statuses);
  
        // 몇개 트윗 나왔는지 알아보기
        tweets_num += tweets.statuses.length;
        
        // 리트윗 몇번 일어나는지 확인하기 
        retweet_num += tweets.statuses.reduce((acc,cur)=>{
          // 리트윗 한게 아닐때만 카운트하기, 이렇게 안하면 리트윗 한것들 모두가 본 글 리트윗 수를 가져서 정보가 잘못된다.
          if(cur.retweeted_status===undefined){
            return acc + cur.retweet_count; 
          }else{
            return acc;
          }
        },0);
        
        // favorite 몇개 일어났는지 확인하기
        favorite_num += tweets.statuses.reduce((acc,cur)=>{
          return acc + cur.favorite_count; 
        },0);
  
        let new_next_page_max_id = Number(tweets.search_metadata.next_results.match(/max_id=([0-9]+)&/g)[0].match(/[0-9]+/g));
        return next_promise(new_next_page_max_id,since_id,tweets_num, retweet_num, favorite_num,raw_data,q);
        
      }else{
        return [tweets_num, retweet_num, favorite_num, raw_data]; 
      }
    })
  }

  function get_twitter_info(start,end,q){
    let since_id, tweets_num=0, retweet_num=0, favorite_num=0, raw_data =[];
    return new Promise(function(resolve, rejected){
      client.get('search/tweets', {q: q,until:start}) 
      .then((tweets) =>{
        // 받기 시작할 데이터 받아오기
        // [0]이 start 전 가장 마지막 데이터임
        since_id =  tweets.statuses[0].id;
        console.log('created_at',tweets.statuses[0].created_at);
        // console.log('since_id', since_id);
        return client.get('search/tweets', {q: q,since_id:since_id, until:end, count:100});
      })
      .then((tweets) => {
        // 트윗 확인해보기
        // for(let i =0;i<tweets.statuses.length ; i++){
        //   console.log(tweets.statuses[i].text);
        // }
      
        // raw_Data 추가하기 (concat은 기존 데이터를 바꾸지는 않는다.)
        raw_data = raw_data.concat(tweets.statuses);
        // 몇개 트윗 나왔는지 알아보기
        tweets_num += tweets.statuses.length;
        
        // 리트윗 몇번 일어나는지 확인하기 
        retweet_num += tweets.statuses.reduce((acc,cur)=>{
          // 리트윗 한게 아닐때만 카운트하기, 이렇게 안하면 리트윗 한것들 모두가 본 글 리트윗 수를 가져서 정보가 잘못된다.
          if(cur.retweeted_status===undefined){
            return acc + cur.retweet_count; 
          }else{
            return acc;
          }
        },0);
        
        // favorite 몇개 일어났는지 확인하기
        favorite_num += tweets.statuses.reduce((acc,cur)=>{
          return acc + cur.favorite_count; 
        },0);
      
        // 혹시 100개 넘으면 다음 페이지도 크롤링해야 함 search는 한 글자씩, match는 여러개 한꺼번에
        // next page work id(처음 시작할 tweet id 의미인데, 다음 페이지로 넘어가면 page work id가 나옴)
        // 추후에 while loop
        let next_page_max_id = Number(tweets.search_metadata.next_results.match(/max_id=([0-9]+)&/g)[0].match(/[0-9]+/g));
      
        return next_promise(next_page_max_id, since_id, tweets_num, retweet_num, favorite_num,raw_data,q);
      })
      .then(([tweets_num, retweet_num, favorite_num,raw_data])=>{
      //   console.log('final');
      //   console.log('period', start, '~', end);
      //   console.log('raw_num', raw_data.length, 'tweet_num=', tweets_num, 'retweet_num=', retweet_num, 'like_num=',favorite_num);
      //   console.log(raw_data);
        resolve({start:start, end:end, tweets_num:tweets_num, retweet_num:retweet_num, favorite_num:favorite_num});
      })
      .catch((err)=>{
        console.log('err',err);
      })
    });
  }

exports.handler = function(event, context, callback) {
    googleTrends.interestOverTime(optionsObject)
    .then(function(results){
        // console.log(JSON.parse(results).default);
        // res = JSON.parse(results).default.timelineData.filter(x=>x.hasData[0]==true);
        // 클레이튼 영어랑 한글 정보 합치고 데이터 보여주기
        // 문제 : 가장 높은 것 기준으로 보여주는것이니까(증감세는 보여줄수 있을듯!)
        let res_json = JSON.parse(results).default.timelineData;
        // console.log(res_json);

        let result_obj = res_json.map(x=>{
            let trends_sum = x.value.reduce((acc,cur)=>acc+cur,0);
            let formatted_date = moment(x.formattedTime, "MMM DD, YYYY").format("YYYY-MM-DD");;
            
            return {'data_date':formatted_date, 'val':trends_sum}
        });
        return result_obj;
    })
    .then(Insert_go)
    .then(()=>{
    let promises = [];
    for(let i = 0; i<7;i++){
        let end_day = moment().subtract(i, 'days').format("YYYY-MM-DD");
        let start_day = moment().subtract(i+1, 'days').format("YYYY-MM-DD");

        promises.push(
        get_twitter_info(start = start_day, end = end_day,q='klaytn')
        );  
    }
    Promise.all(promises).then(Insert_tw).then(()=>{pg_client.end()});
    })
    .catch(function(err){
        console.error('Oh no there was an error', err);
    });
}


