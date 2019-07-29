const { WebClient } = require('@slack/client');
const token = process.env.SLACK_TOKEN;
const web = new WebClient(token);

function send_message(){
    //메시지 body로 만들req
    web.chat.postMessage({
      //https://ground-x.slack.com/messages/GFQ6XM23Y
      channel: "GFQ6XM23Y",
      // jason과 okr owner에게 mention하기
      "text": `HELLOW WORLD`,
      "attachments": [
          {"type": "section",
          "text": {
              "type": "mrkdwn",
              "text": "*HIHIHIHI*"
            }
          },
      ]
    })
    .then((res_slack) => {
    // `res` contains information about the posted message
    console.log(res_slack)
    return 
    })
    .catch((err)=>console.log(err));
  }

  send_message();