const admin = require('firebase-admin');

let serviceAccount = require('/Users/pratikkshirsagar/Desktop/Projects/ocr/function/serviceAccountKey.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://test-ocr-259809.firebaseio.com'
});

const { Storage } = require('@google-cloud/storage');
const storage = new Storage({
  projectId: 'test-ocr-77e4e',
  keyFilename: 'serviceAccountKey.json'
});

let db = admin.firestore();
const bucketName = 'test-ocr-259809.appspot.com';
const jsonBucket = 'user-pdf-jsonfile';

// ------ GET THE PDF FROM STORE -------- //

async function main() {
  try {
    const [files] = await storage.bucket(bucketName).getFiles();

    files.forEach(file => {
      // ----  VISION API ---- //

      const srcBucket = `gs://${bucketName}/${file.name}`;
      const desBucket = `gs://${jsonBucket}/${file.name}/`;

      // ----- VISION API CALL ---- //
      detectPdfText(srcBucket, desBucket);
    });
  } catch (err) {
    console.log(err);
  }
}

async function detectPdfText(srcBucket, desBucket) {
  try {
    // Imports the Google Cloud client libraries
    const vision = require('@google-cloud/vision').v1;

    const client = new vision.ImageAnnotatorClient();

    const inputConfig = {
      // Supported mime_types are: 'application/pdf' and 'image/tiff'
      mimeType: 'application/pdf',
      gcsSource: {
        uri: srcBucket
      }
    };
    const outputConfig = {
      gcsDestination: {
        uri: desBucket
      },
      batchSize: 1
    };
    const features = [{ type: 'DOCUMENT_TEXT_DETECTION' }];
    const request = {
      requests: [
        {
          inputConfig: inputConfig,
          features: features,
          outputConfig: outputConfig
        }
      ]
    };

    const [operation] = await client.asyncBatchAnnotateFiles(request);
    const [filesResponse] = await operation.promise();
    const destinationUri =
      filesResponse.responses[0].outputConfig.gcsDestination.uri;
    console.log('Json saved to: ' + destinationUri);
  } catch (err) {
    console.log(err);
  }
}

main();
