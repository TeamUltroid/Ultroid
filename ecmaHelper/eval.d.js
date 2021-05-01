const { exec } = require('child_process');
const { appendFileSync, truncate, writeFile } = require('fs');
console.log("Command -> `" + String(process.argv.slice(2)).replace(',', ' ').replace('"', '\'') + '`');
(async () => {
    const evalJs = exec('node ./ecmaHelper/evalJs.run.js');
    
    truncate('./ecmaHelper/evalJs.run.js', 0, function() { 
        console.log('Script File Truncated');
    });
    
    truncate('./ecmaHelper/evalJs.result.d.txt', 0, function() { 
        console.log('Result File Truncated');
    });
    
    
    writeFile('./ecmaHelper/evalJs.run.js', String(process.argv.slice(2)), () => {
        console.log('written script');
    });
    
    evalJs.stdout.on('data', (data) => {
        console.log(data)
        appendFileSync('./ecmaHelper/evalJs.result.d.txt', `${data.toString()}\n`, () => {});
    })
    
    evalJs.stderr.on('data', (error) => {
        console.log(error.toString())
        appendFileSync('./ecmaHelper/evalJs.result.d.txt', `${error.toString()}\n`, () => {});
    }) 
})()

