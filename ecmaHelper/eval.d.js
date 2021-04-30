const { appendFileSync, truncate } = require('fs');

console.log("Command -> `" + String(process.argv.slice(2)).replace(',', ' ') + '`');

const evalJs = eval(String(process.argv.slice(2)).replace(',', ' '));

truncate('Ernest/NodeHelper/bash_output.txt', 0, function() { 
    console.log('File Content Deleted');
}); 

bash.stdout.on('data', (data) => {
    appendFileSync('./ecmaHelper/evalJs.result.d.txt', `${data.toString()}\n`, () => {});
})

bash.stdout.on('error', (error) => {
    appendFileSync('./ecmaHelper/evalJs.result.d.txt', `${error.message}\n`, () => {});
})
