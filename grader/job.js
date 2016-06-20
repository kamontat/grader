let fs = require('fs');
let winston = require('winston');
let concat = require('concat-stream');
let yaml = require('js-yaml');
let tar = require('tar-stream');

let settingsCache = {}

class Job {
	constructor(data, docker, beanstalk, id){
		this.docker = docker;
		this.beanstalk = beanstalk;
		this.beanstalkId = id;
		this.data = data;

		this.extendInterval = 10000;
		this.inputTimeout = 1000;
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

		var container;
		return this._prepareAndPull(settings.input.image)
			.then(() => {
				return this.docker.createContainer({
					Image: settings.input.image,
					Cmd: settings.input.cmd,
					Labels: {grader: 'true'},
					NetworkDisabled: true,
					StopSignal: 'SIGKILL',
					HostConfig: {
						MemoryReservation: 64,
						PidsLimit: 100,
						LogConfig: { Type: 'none' },
					}
				});
			}).then((c) => {
				container = c;
				winston.debug(`Created input container ${container.id}. Generating files...`);

				let archive = tar.pack();
				archive.entry({
					name: `/grader/${settings.input.input_file}`
				}, this.data.input.code);
				if(settings.input.helper){
					archive.entry({
						name: `/grader/${settings.input.helper_file}`
					}, settings.input.helper);
				}
				archive.finalize();

				return new Promise((resolve, reject) => {
					archive.pipe(concat((data) => {
						resolve(new Buffer(data));
					}));
				});
			}).then((archive) => {
				return container.putArchive(archive, {
					path: '/',
				});
			}).then(() => {
				return container.attach({stream: true, stdout: true, stderr: true});
			}).then((stream) => {
				container.start().then(() => winston.debug('Container started'));
				return new Promise((resolve, reject) => {
					let timeout = setTimeout(() => {
						winston.warn('Input timed out');
						// todo: remove readers
						reject('Input timed out');
					}, this.inputTimeout);

					let outStream = concat((out) => {
						clearTimeout(timeout);
						try{
							resolve(JSON.parse(out.toString('utf8')));
						}catch(e){
							reject(e);
						}
					});

					container.modem.demuxStream(stream, outStream);
					stream.on('end', () => outStream.end());
				});
			}).then((data) => {
				winston.info(`Removing stale container ${container.id}...`);
				return container.remove({
					force: true,
					v: true,
				}).then(() => {
					return data;
				});
			}, (err) => {
				winston.error('Error running input generator');
				if(container){
					winston.info(`Removing stale container ${container.id}...`);
					return container.remove({
						force: true,
						v: true,
					}).then(() => {
						return Promise.reject(err);
					});
				}
				return Promise.reject(err);
			});
	}

	grade(){
		return this.generateInput().then((inputs) => {
			console.log(inputs);
		});
	}

	_prepareAndPull(image){
		return this.docker.listImages({
			filter: image
		}).then((data) => {
			if(data.length === 0){
				winston.info(`Image ${image} does not exists. Pulling...`);
				return new Promise((resolve, reject) => {
					this.docker.pull(image).then((stream) => {
						stream.pipe(process.stdout);
						stream.on('end', resolve);
					});
				});
			}
			return true;
		});
	}
}

module.exports = Job;
