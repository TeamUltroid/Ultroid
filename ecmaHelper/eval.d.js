const { exec } = require('child_process');
const { appendFileSync, truncate, writeFileSync } = require('fs');
console.log("Command -> `" + String(process.argv.slice(2)).replace(',', ' ').replace('"', '') + '`');


truncate('./ecmaHelper/evalJs.run.js', 0, function() { 
    console.log('Script File Truncated');

});
truncate('./ecmaHelper/evalJs.result.d.txt', 0, function() { 
    console.log('Result File Truncated');
    writeFileSync('', String(process.argv.slice(2)), () => {});
}); 

const evalJs = exec('node ./ecmaHelper/evalJs.run.js');

evalJs.stdout.on('data', (data) => {
    console.log("data")
    appendFileSync('./ecmaHelper/evalJs.result.d.txt', `${data.toString()}\n`, () => {});
})

evalJs.stdout.on('error', (error) => {
    console.log("error")
    appendFileSync('./ecmaHelper/evalJs.result.d.txt', `${error.message}\n`, () => {});
})
