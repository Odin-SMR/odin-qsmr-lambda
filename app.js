const { spawn } = require('child_process');
const binaryPath = '/qsmr/run_runscript.sh';

exports.handler = (event, context) => {
    const env = { ...process.env, LD_LIBRARY_PATH: '/opt/matlab/v90/runtime/glnxa64:/opt/matlab/v90/bin/glnxa64:/opt/matlab/v90/sys/os/glnxa64' };
    const child = spawn(binaryPath, ["/opt/matlab/v90", event.source, event.target] , { env });
    console.log(event.source)
    console.log(event.target)
    child.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    child.stderr.on('data', (data) => {
        console.log(`stderr: ${data}`);
    });

    child.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });
}

