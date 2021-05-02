const { exec } = require('child_process');
const { appendFile, truncate } = require('fs');
(async () => {
    const evalJs = exec('node ./src/ecmaHelper/evalJs.run.js');
    
    truncate('./src/ecmaHelper/evalJs.result.d.txt', 0, function() { 
        console.log('Result File Truncated');
    });
    
    evalJs.stdout.on('data', (data) => {
        appendFile('./src/ecmaHelper/evalJs.result.d.txt', `${data.toString()}\n`, () => {});
    })
    
    evalJs.stderr.on('data', (error) => {
        appendFile('./src/ecmaHelper/evalJs.result.d.txt', `${error.toString()}\n`, () => {});
    }) 
})()

