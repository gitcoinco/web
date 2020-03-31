const secrets = require('secrets.js-grempe');


if (!process.argv[2] || !process.argv[3]) {
  process.exit(1);
}

const gitcoinSecret = process.argv[2];
const tipKey = process.argv[3];

const secret = secrets.combine([gitcoinSecret, tipKey]);

console.log(secret);

process.exit(0);
