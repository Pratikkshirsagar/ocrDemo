const admin = require('firebase-admin');

let serviceAccount = require('./serviceAccountKey.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://test-ocr-259809.firebaseio.com'
});

let db = admin.firestore();

const vision = require('@google-cloud/vision').v1;

const client = new vision.ImageAnnotatorClient();

const bucketName = 'test-ocr-259809.appspot.com';
const fileName = 'Pratik_kshirsagar-CASE STUDY REPORT_02.pdf';

const gcsSourceUri = `gs://${bucketName}/${fileName}`;

const inputConfig = {
  // Supported mime_types are: 'application/pdf' and 'image/tiff'
  mimeType: 'application/pdf',
  gcsSource: {
    uri: gcsSourceUri
  }
};
const features = [{ type: 'DOCUMENT_TEXT_DETECTION' }];
const request = {
  requests: [
    {
      inputConfig: inputConfig,
      features: features,
      pages: [1]
    }
  ]
};

async function ocr(request, fileName) {
  try {
    const res = await client.batchAnnotateFiles(request);
    let pageNo = res[0].responses[0].totalPages;
    convertPdfPageNoToArray(pageNo, fileName);
  } catch (err) {
    console.log(err);
  }
}

async function convertPdfPageNoToArray(pageNo, fileName) {
  let pageNoArray = [];
  for (let input = 1; input <= pageNo; input++) {
    pageNoArray.push(input);
  }

  const chunked = [];
  const size = 1;

  for (const element of pageNoArray) {
    const last = chunked[chunked.length - 1];

    if (!last || last.length === size) {
      chunked.push([element]);
    } else {
      last.push(element);
    }
  }

  getText(chunked, fileName);
}

async function getText(pageNoArray, fileName) {
  try {
    let userObj = {};
    userObj[fileName] = {};
    for (let setOfPages of pageNoArray) {
      let request = {
        requests: [
          {
            inputConfig: inputConfig,
            features: features,
            pages: setOfPages
          }
        ]
      };

      const finalOutPut = await client.batchAnnotateFiles(request);
      let pageObj = await finalOutPut[0].responses[0].responses[0];
      userObj[fileName][pageObj.context.pageNumber] =
        pageObj.fullTextAnnotation.text;
    }

    setToDb(userObj);
  } catch (err) {
    console.log(err);
  }
}


async function setToDb(pdfText) {
  db.collection('users')
    .get()
    .then(snapshot => {
      snapshot.forEach(doc => {
        if (doc.id === 'pratik') {
          let docRef = db.collection('users').doc(doc.id);

          docRef.set({
            pdfText
          });
        }
      });
    })
    .catch(err => {
      console.log('Error getting documents', err);
    });
}



ocr(request, fileName);