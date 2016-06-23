let fs = require('fs');
let winston = require('winston');
let yaml = require('js-yaml');
let Container = require('./container');

let settingsCache = {}

class Job {
	constructor(data, docker, beanstalk, id){
		this.docker = docker;
		this.beanstalk = beanstalk;
		this.beanstalkId = id;
		this.data = data;
		this.collectedErrors = [];
		this.containers = {};

		this.extendInterval = 10000;
		this.inputTimeout = 1000;
		this.compileTimeout = 30000;
	}

	autoExtend(){
		if(!this.beanstalk){
			return;
		}

		this._timer = setInterval(() => {
			this.beanstalk.touch(this.beanstalkId, (err) => {
				if(err){
					winston.error(`Extending job error`, err);
				}
			});
		}, this.extendInterval);
	}

	getLanguageSettings(lang){
		if(!settingsCache[lang]){
			settingsCache[lang] = yaml.safeLoad(fs.readFileSync('languages/' + lang + '.yaml', 'utf8'));
		}
		return settingsCache[lang];
	}

	generateInput(){
		let settings = this.getLanguageSettings(this.data.input.lang);
		winston.debug(`Creating input container using image ${settings.input.image}...`);

		let container = new Container(this.docker);
		return container.create({
			Image: settings.input.image,
			Cmd: settings.input.cmd,
			memLimit: 64,
		}).then(() => {
			let files = {};
			files[`/grader/${settings.input.input_file}`] = this.data.input.code;

			if(settings.input.helper){
				files[`/grader/${settings.input.helper_file}`] = settings.input.helper;
			}

			return container.putFile(files);
		}).then(() => {
			return container.runWithTimeout(this.inputTimeout);
		}).then((data) => {
			container.remove();
			if(data[1]){
				this.collectedErrors.push(data[1]);
			}
			return JSON.parse(data[0]);
		}).catch((err) => {
			if(Array.isArray(err) && err.length >= 2){
				this.collectedErrors.push(err[1]);
			}
			winston.error('Error running input generator', err);
			if(container.hasContainer()){
				winston.info(`Removing stale container ${container.id}...`);
				container.remove();
			}
			return Promise.reject(['E']);
		});
	}

	grade(){
		let cleanup = (res) => {
			this.cleanup();
			if(this._timer){
				clearInterval(this._timer);
			}
			return res;
		};

		return this.generateInput().then((inputs) => {
			winston.info(`Found ${inputs.length} test cases`);
			winston.debug(inputs);
			return this._runCase(inputs);
		}).then(cleanup, cleanup);
	}

	cleanup(){
		for(let key of Object.keys(this.containers)){
			winston.debug(`Removed ${key} container`);
			this.containers[key].remove();
		}
	}

	_runCase(cases, index = 1){
		let testCase = cases.shift();
		winston.info(`Running case ${index}: ${testCase}`);
		let expected, thisResult = 'E';
		return this._runOutput('output', this.data.output, testCase).then((e) => {
			expected = e[0];

			winston.debug(`solution:\n${expected}`);
			if(e[1]){
				this.collectedErrors.push(e[1]);
				winston.debug(`solution stderr:\n${e[1]}`);
			}
		}, (e) => {
			winston.error(e);
			thisResult = 'E';
			return Promise.reject();
		}).then(() => {
			return this._runOutput('submission', this.data.submission, testCase);
		}).then((result) => {
			winston.debug(`submission:\n${result[0]}`);
			// this.collectedErrors.push(result[1]);
			if(result[0].trim() === expected.trim()){
				thisResult = 'P';
			}else if(result[0].replace(/\s/g, '') === expected.replace(/\s/g, '')){
				thisResult = 'S';
			}else if(result[0].toLowerCase() === expected.toLowerCase()){
				thisResult = 'C';
			}else{
				thisResult = 'F';
			}
			winston.debug(`verdict: ${thisResult}`);
		}, (result) => {
			if(thisResult) return Promise.reject();

			winston.debug(`submission:\n${result[0]}`);
			if(result[2] === 'Timed out'){
				thisResult = 'T';
			}else{
				thisResult = 'E';
			}
			winston.debug(`verdict: ${thisResult}`);
			return Promise.reject();
		}).then(() => {
			if(cases.length === 0){
				return [];
			}
			return this._runCase(cases, index + 1);
		}).then((nextResult) => {
			return [thisResult].concat(nextResult);
		}, () => {
			return [thisResult];
		});
	}

	_runOutput(type, config, input){
		let settings = this.getLanguageSettings(config.lang);
		let container, promise;
		if(!this.containers[type]){
			winston.info(`Creating ${type} container`);
			container = new Container(this.docker);
			this.containers[type] = container;

			let filename = settings.input_file;
			let name;
			if(settings.input_file_regex){
				name = new RegExp(settings.input_file_regex).exec(config.code);
				name = name.length > 1 ? name[1] : 'input';
				filename = settings.input_file_regex_format.replace(/\$1/g, name);
				winston.debug(`Naming file ${filename}`);
			}

			let cmd = settings.cmd;
			if(settings.compile){
				cmd = settings.compile;
			}
			if(name){
				cmd = cmd.map((item) => item.replace(/\$1/g, name));
				winston.debug(`Rewrote command line`, cmd);
			}

			promise = container.create({
				Image: settings.image,
				Cmd: cmd,
				memLimit: this.data.limits.mem || 64,
				OpenStdin: true,
				AttachStdin: true,
				User: settings.compile ? '0': '1000',
				Volumes: settings.compile ? {'/grader/': {}} : null
			}).then(() => {
				let files = {};
				files[`/grader/${filename}`] = config.code;

				return container.putFile(files);
			}).then(() => {
				if(settings.compile){
					winston.debug(`Compiling ${type}...`);
					return container.runWithTimeout(this.compileTimeout).then((res) => {
						let oldContainerId = container.id;
						this.containers[`${type} compile`] = container;

						container = new Container(this.docker);
						this.containers[type] = container;
						winston.debug(`Creating child container ${type}...`);

						let cmd = settings.cmd;
						if(name){
							cmd = cmd.map((item) => item.replace(/\$1/g, name));
							winston.debug(`Rewrote command line`, cmd);
						}

						return container.create({
							Image: settings.image,
							Cmd: cmd,
							memLimit: this.data.limits.mem || 64,
							OpenStdin: true,
							AttachStdin: true,
							ReadonlyRootfs: true,
							VolumesFrom: [`${oldContainerId}:ro`],
						});
					}, (res) => {
						winston.error('Compile error', res);
						this.collectedErrors.push(res[1]);
						return Promise.reject(res);
					});
				}
			});
		}else{
			container = this.containers[type];
			promise = Promise.resolve();
		}
		return promise.then(() => {
			return container.runWithTimeout(this.data.limits.time * 1000 || 10000, input);
		});
	}
}

module.exports = Job;
