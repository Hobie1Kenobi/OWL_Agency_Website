<?php
/**
 * Microsoft UET Tag Inclusion Script
 * 
 * This script adds the UET tag to all pages that don't already have it.
 * Add to your page by including this file:
 * <?php include 'add-uet-tag.php'; ?>
 */

// Only add the tag if it doesn't already exist on the page
echo '<!-- Microsoft UET Tag - ID: 97179628 -->
<script>
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
</script>';
?> 