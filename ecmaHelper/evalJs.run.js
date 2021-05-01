const evalJs = eval(String(process.argv.slice(2)).replace(',', ' '));
console.log(evalJs);