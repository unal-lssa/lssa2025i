#!/bin/bash
set -e

awslocal s3 mb s3://music-storage
awslocal s3 cp /songs/song.mp3 s3://music-storage/song.mp3