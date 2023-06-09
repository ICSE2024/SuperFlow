const util = require('util');
const AWS = require('aws-sdk');
const rekognition = new AWS.Rekognition();


/**
 * Calls the Rekognition service to detect lables in an image.
 * @param event should contain "s3Bucket" and "s3Key" fields
 * @param context
 * @param callback
 */
exports.handler = async (event, context, callback) => {
	console.log("Reading input from event:\n", util.inspect(event, { depth: 5 }));

	const srcBucket = event.s3Bucket;
	// Object key may have spaces or unicode non-ASCII characters.
	const srcKey = decodeURIComponent(event.s3Key.replace(/\+/g, " "));

	var params = {
		Image: {
			S3Object: {
				Bucket: srcBucket,
				Name: srcKey
			}
		},
		MaxLabels: 10,
		MinConfidence: 60
	};

	try {
		const result = await rekognition.detectLabels(params).promise();
		callback(null, result.Labels);
	} catch (err) {
		callback(err);
	}

};
