/**
 * Microsoft UET Tag Injection Script
 * 
 * This script dynamically adds the UET tag to any page where it's included.
 * It checks if the tag is already present before adding it.
 */

(function() {
  // Check if UET tag already exists
  if (window.uetq || document.querySelector('script[src*="bat.bing.com/bat.js"]')) {
    console.log('UET tag already exists on this page');
    return;
  }
  
  // Create and add the UET tag
  var uetScript = document.createElement('script');
  uetScript.text = `
    (function(w,d,t,r,u){
      var f,n,i;
      w[u]=w[u]||[],f=function(){
        var o={ti:"97179628"};
        o.q=w[u],w[u]=new UET(o),w[u].push("pageLoad")
      },
      n=d.createElement(t),n.src=r,n.async=1,n.onload=n.onreadystatechange=function(){
        var s=this.readyState;
        s&&s!=="loaded"&&s!=="complete"||(f(),n.onload=n.onreadystatechange=null)
      },
      i=d.getElementsByTagName(t)[0],i.parentNode.insertBefore(n,i)
    })(window,document,"script","//bat.bing.com/bat.js","uetq");
  `;
  
  document.head.appendChild(uetScript);
  console.log('Microsoft UET tag (ID: 97179628) added to page');
})(); 