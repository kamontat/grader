# Grader runner Docker image readme

Must run as privileged user

Usage:

```
sudo docker run --restart=always --privileged \
	-v /var/run/docker.sock:/var/run/docker.sock \
	-e GRADER_SECRET=.... \
	-e GRADER_BEANSTALK=....:11300 \
	-e GRADER_VERBOSE=true \
	-e GRADER_SERVER=http://.../server/result \
	willwill/grader-runner
```

## Environment variables

- GRADER_SECRET: Set to the same value as configured in grader
- GRADER_BEANSTALK: Set to IP:port of beanstalkd. The port is required.
- GRADER_VERBOSE: Set to `true` to print test cases and run result
- GRADER_BEANSTALK_TUBE: Set to beanstalkd tube name as configured in grader.
  The default of `grader` is probably correct in most cases.
