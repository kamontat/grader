let winston = require('winston');
let Docker = require('dockerode-promise');
let Job = require('./job');

winston.level = 'debug';
winston.cli();

let docker = new Docker();
let job = new Job({
	result_id: 1,
	input: {
		lang: 'py',
		code: `def run():
	yield 44
	yield 'echo'`,
	},
	output: {
		lang: 'java',
		code: `import java.util.Scanner
public class CustomName {
	public static void main(String[] args){
		Scanner scan = new Scanner(System.in);
		System.out.println(scan.nextLine());
	}
}`
	},
	submission: {
		lang: 'py3',
		code: `while True:
	print(input())`
	},
	limits: {
		time: 1,
		mem: 32,
	}
}, docker);

job.grade().then(console.log).catch(console.error);
