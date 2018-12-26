var CryptoJS = require('crypto-js');
console.log(CryptoJS.AES.encrypt(process.argv[2],
                'NGMzMTUyMmY0NGIyOWI5YTYxYzRhYTRjNzcyYzc3YWM2NGQwZDg2YzA1NmE5ZmNh').toString());
