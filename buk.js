const admin = require('firebase-admin');

let serviceAccount = require('./serviceAccountKey.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: 'https://test-ocr-259809.firebaseio.com'
});

let db = admin.firestore();

async function setDoc() {
  try {
    let docRef = db.collection('users').doc('pratik');

    docRef.set({
      first: 'pratik',
      last: 'kshirsagar',
      born: 1995
    });
  } catch (err) {}
}

// setDoc();

async function getUser() {
  const pdfText = {
    1: 'sometext',
    2: 'some more text'
  };
  db.collection('users')
    .get()
    .then(snapshot => {
      snapshot.forEach(doc => {
        if (doc.id === 'pratik') {
          console.log(doc.id, '=>', doc.data());
          let docRef = db.collection('users').doc(doc.id);

          docRef.update({
            pdfText
          });
        }
      });
    })
    .catch(err => {
      console.log('Error getting documents', err);
    });
}

getUser();
