let concat = require('concat-stream');
let tar = require('tar-stream');
let winston = require('winston');

class Container{
	constructor(docker){
		this.docker = docker;
	}

	hasContainer(){
		return !!this.container;
	}

	get id(){
		return this.container.id;
	}

	create(config){
		return this._prepareAndPull(config.Image)
			.then(() => {
				let conf = {
					HostConfig: {
						Memory: config.memLimit * 1024 * 1024,
						PidsLimit: 100,
						LogConfig: { Type: 'none' },
						VolumesFrom: config.VolumesFrom || null,
					},
					NetworkDisabled: true,
					User: '1000',
					StopSignal: 'SIGKILL',
				};

				Object.assign(conf, config);
				return this.docker.createContainer(conf);
			}).then((c) => {
				this.container = c;
				return c;
			});
	}

	putFile(item){
		// TODO: Put multiple files
		let archive = tar.pack();
		for(let key of Object.keys(item)){
			archive.entry({
				name: key,
			}, item[key]);
		}
		archive.finalize();

		return new Promise((resolve, reject) => {
			archive.pipe(concat((data) => {
				resolve(new Buffer(data));
			}));
		}).then((archive) => {
			return this.container.putArchive(archive, {
				path: '/',
			});
		});
	}

	runWithTimeout(timeout, stdin){
		return this.container.attach({stream: true, hijack: true, stdin: true, stdout: true, stderr: true})
			.then((stream) => {
				return new Promise((resolve, reject) => {
					let stdout = null, stderr = null, timer, err = null;
					let resolution = resolve;
					this.container.start().then(() => {
						timer = setTimeout(() => {
							winston.warn('Timed out');
							stream.end();
							this.container.kill({signal: 'SIGKILL'});
							err = 'Timed out';
							resolution = reject;
						}, timeout);

						winston.debug('Container started');
						if(stdin){
							stream.write(stdin + '\n');
						}
					});

					let attemptResolve = () => {
						if(stdout !== null && stderr !== null){
							resolution([stdout, stderr, err]);
						}
					};

					let outStream = concat((out) => {
						stdout = out.toString('utf8');
						attemptResolve();
					});
					let errStream = concat((out) => {
						stderr = out.toString('utf8');
						attemptResolve();
					});

					this.container.modem.demuxStream(stream, outStream, errStream);
					stream.on('error', () => {
						reject();
					});
					stream.on('end', () => {
						clearTimeout(timer);
						outStream.end();
						errStream.end();
					});
				});
			}).then((result) => {
				return this.container.wait().then((code) => {
					if(code.StatusCode !== 0){
						result[2] = code.StatusCode;
						return Promise.reject(result);
					}
					return result;
				});
			}, (result) => {
				if(result[2]){
					return Promise.reject(result);
				}
				return this.container.wait().then((code) => {
					result[2] = code.StatusCode;
					return Promise.reject(result);
				});
			});
	}

	remove(){
		if(!this.container){
			return;
		}
		let result = this.container.remove({
			force: true,
			v: true,
		});
		this.container = null;
		return result;
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

module.exports = Container;
