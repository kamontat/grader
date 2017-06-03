#!/bin/bash

for i in java:jdk python:3-alpine python:2-alpine; do
	sudo docker pull $i
done
