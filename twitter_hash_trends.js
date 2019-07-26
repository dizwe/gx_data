
var HashtagCount = require('hashtag-count');
 
var client = new Twitter({
  consumer_key: '4RTtiiqxX4ID949CZi7Wnr62M',
  consumer_secret: process.env.CONSUMER_SECRET,
  access_token_key: '1127968910-XAALt7MLvPZuQzRS33Ksf4RtzaOBy6rXSBMzcHD',
  access_token_secret: process.env.ACCESSTOKEN_SECRET,
});


// Array of hashtags to tally. Do not include # prefix.
var hashtags = ['klaytn','블록체인','b'];
 
// Hashtag tallies for each time interval will be added to the results object.
var interval = '30 seconds';

// Delete data older than this.
var history = '5 minutes';
 
// Called at the end of each time interval.
var intervalCb = function (err, results) {
  if (err) {
    console.error(err);
  } else {
    console.log(results);
  }
};
 
// Open a connection to Twitter's Streaming API and start capturing tweets!
hc.start({
  hashtags: hashtags,       // required
  interval: interval,       // required
  history: history,         // optional
  intervalCb: intervalCb,   // optional
});