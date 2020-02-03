const pdfjsLib = require('pdfjs-dist');
let pdfPath = '/Users/pratikkshirsagar/Desktop/Projects/ocrDemo/pdf/A.pdf';
// pdfjsLib.getDocument(pdfPath).then(function(doc) {
//   var numPages = doc.numPages;
//   console.log('# Document Loaded');
//   console.log('Number of Pages: ' + numPages);
// });

async function pageNo() {
  let val = await pdfjsLib.getDocument(pdfPath);
  let pageno = val._pdfInfo.numPages;
  for (let input = 1; input <= pageno; input++) {
    console.log(input);
  }
}

pageNo();
