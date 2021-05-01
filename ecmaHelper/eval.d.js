const { exec } = require('child_process');
const { appendFileSync, truncate } = require('fs');
console.log("Command -> `" + String(process.argv.slice(2)).replace(',', ' ').replace('"', '') + '`');

const evalJs = exec(String(`node ./ecmaHelper/evalJs.run.js ${String(process.argv.slice(2)).replace(',', ' ').replace('"', '')}`));

truncate('./ecmaHelper/evalJs.result.d.txt', 0, function() { 
    console.log('File Content Deleted');
}); 


evalJs.stdout.on('data', (data) => {
    console.log("data")
    appendFileSync('./ecmaHelper/evalJs.result.d.txt', `${data.toString()}\n`, () => {});
})

evalJs.stdout.on('error', (error) => {
    console.log("error")
    appendFileSync('./ecmaHelper/evalJs.result.d.txt', `${error.message}\n`, () => {});
})
