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
	for i in range(2):
		yield 'echo'`,
	},
	output: {
		lang: 'py3',
		code: `print(input())`,
	},
	submission: {
		lang: 'java',
		code: `import java.util.Scanner;
public class CustomName {
	public static void main(String[] args){
		Scanner scan = new Scanner(System.in)
		System.out.println(scan.nextLine());
	}
}`,
	},
	limits: {
		time: 1,
		mem: 32,
	}
}, docker);

job.grade().then((result) => {
	console.log(result);
	console.log(job.collectedErrors);
}).catch(console.error);
