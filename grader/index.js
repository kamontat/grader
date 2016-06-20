let yargs = require('yargs');
let Docker = require('dockerode-promise');
let fivebeans = require('fivebeans');
let winston = require('winston');
let Job = require('./job');

let argv = yargs.env('GRADER')
	.usage('usage: $0 --secret hackme')
	.options({
		's': {
			alias: 'secret',
			demand: true,
			describe: 'API secret',
			type: 'string',
			group: 'Grader',
		},
		'b': {
			alias: 'beanstalk',
			default: '127.0.0.1:11300',
			describe: 'Beanstalkd server',
			type: 'string',
			group: 'Beanstalk',
		},
		't': {
			alias: 'beanstalk-tube',
			default: 'grader',
			describe: 'Beanstalkd tube name',
			type: 'string',
			group: 'Beanstalk',
		},
		'v': {
			alias: 'verbose',
			count: true,
			describe: 'Output test cases and run results',
		},
		'server': {
			default: 'http://localhost/server/result',
			describe: 'Grader result API URL',
			type: 'string',
			group: 'Grader',
		},
		'docker-host': {
			type: 'string',
			describe: 'Docker API host',
			group: 'Docker',
		},
		'docker-port': {
			type: 'string',
			describe: 'Docker API port',
			group: 'Docker',
		},
		'docker-socket': {
			type: 'string',
			describe: 'Docker API port',
			group: 'Docker',
		},
	})
	.argv;

winston.level = argv.v ? 'debug' : 'info';
winston.cli();

let beanstalkHost = argv.b.split(':');

let docker = new Docker({
	host: argv['docker-host'],
	port: argv['docker-port'],
	socketPath: argv['docker-socket'],
});
let client = new fivebeans.client(beanstalkHost[0], parseInt(beanstalkHost[1], 10));
client.on('connect', () => {
		winston.info('Beanstalk connected');
		client.watch(argv.t, () => {
			winston.debug(`Watching ${argv.t}`);
		});

		getJob();
	})
	.on('error', (err) => {
		winston.error('Beanstalk error', err);
	})
	.on('close', () => {
		winston.error('Beanstalk closed');
	}).connect();

let getJob = () => {
	client.reserve((err, jobId, payload) => {
		if(err){
			winston.error('Job error', err);
			return;
		}
		let job = JSON.parse(payload.toString('utf8'));
		winston.info(`Got job ${job.result_id}`);
		winston.debug(job);
		new Job(job, client, jobId);
	});
}
