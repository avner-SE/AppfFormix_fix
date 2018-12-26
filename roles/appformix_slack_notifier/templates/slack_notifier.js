var express = require('express');
var app = express();
var url = require('url');
var request = require('request');
var _ = require('lodash');
var SlackBot = require('slackbots');

var bodyParser = require('body-parser');
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Internal port can always be 80
app.set('port', 80);
app.set('host_port', '{{ appformix_slack_notifier_port }}');
app.set('token', '{{ appformix_slack_notifier_token }}');
app.set('channel', '{{ appformix_slack_notifier_channel }}');

app.get('/', function(req, res){
  res.send('Slack bot integration works. Params :' +
           '\ntoken : ' + app.get('token') +
           '\nchannel : ' + app.get('channel') +
           '\nhost_port : ' + app.get('host_port'));
});

app.post('/slack', function(req, res){
  var params = {
        attachments: [
        {
            "fallback": "AppFormix Alert",
            "title": "AppFormix Alert",
            "text": JSON.stringify(req.body, null, 2),
            "mrkdwn_in": [
                "text",
                "pretext"
            ]
        }],
        icon_emoji: ':alarm_clock:'
    };
  bot.postMessageToChannel(app.get('channel'), 'SDK Notification:', params);
  res.send('Success');
});

// To add a new bot
// Add a bot https://<channel>.slack.com/services/new/bot
// and put the token
var bot = new SlackBot({
    token: app.get('token'),
    name: 'AppFormix SlackBot'
});

app.listen(app.get('port'), function() {
  console.log('App running on port ' +
              app.get('host_port') +
              ': - ' +
              app.get('port'));
});
