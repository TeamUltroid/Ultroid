const { exec } = require('child_process');
const { appendFile, truncate } = require('fs');

(async () => {
    const bash = exec('node ./src/ecmaHelper/evalJs.run.js');

    truncate('./src/ecmaHelper/evalJs.result.d.js', 0, function() { 
        console.log('Result File Truncated') 
    }); 

    bash.stdout.on('data', (data) => {
        appendFile('./src/ecmaHelper/evalJs.result.d.js', `${data.toString()}\n`, () => {});
    });

    bash.stderr.on('error', (error) => {
        appendFile('./src/ecmaHelper/evalJs.result.d.js', `${error}\n`, () => {});
    });
})();