// FAQ Schema for batch-processing.html
document.addEventListener('DOMContentLoaded', function() {
    const schemaScript = document.createElement('script');
    schemaScript.type = 'application/ld+json';
    schemaScript.innerHTML = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is batch processing in legal research?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Batch processing in legal research is the ability to simultaneously analyze multiple legal documents, cases, or statutes using AI algorithms. OWL AI's batch processing allows law firms to upload hundreds of documents at once, automatically categorize them, extract key information, and identify relevant precedents across the entire batch."
      }
    },
    {
      "@type": "Question",
      "name": "How many documents can be processed in a single batch?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "OWL AI's batch processing system can handle up to 1,000 documents in a single batch, with typical processing times of 5-15 minutes depending on document complexity. There are no practical limits on document length, and our system can process various formats including PDF, DOCX, TXT, and scanned documents with OCR."
      }
    },
    {
      "@type": "Question",
      "name": "What information can be extracted through batch processing?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Our batch processing system extracts key case elements including parties, judges, citations, legal principles, procedural history, and holdings. It can also identify specific language patterns like dissenting opinions, dicta, or statutory interpretations across multiple documents, enabling comprehensive legal analysis impossible with manual methods."
      }
    }
  ]
};
    document.head.appendChild(schemaScript);
});
