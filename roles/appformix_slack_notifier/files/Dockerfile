FROM node:7.9.0
MAINTAINER AppFormix <support@appformix.com>

RUN npm install \
    express \
    request \
    lodash \
    slackbots \
    url \
    body-parser
RUN npm install -g nodemon

COPY slack_notifier.js /

EXPOSE 80 443
CMD ["nodemon", "/slack_notifier.js", "--watch", "/slack_notifier.js"]
